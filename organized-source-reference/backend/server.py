import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from connectors import CONNECTORS

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="KETCHUM SOS — Public Infrastructure API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ketchum-sos")

START_TIME = time.time()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(name: str) -> Any:
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_of(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


REGISTRY = load_json("registry.json")
EVIDENCE_MODEL = load_json("evidence_ladder.json")
AUTHORITY_MODEL = load_json("authority.json")
MANIFEST_BASE = load_json("SYSTEM-MANIFEST.json")
DOCS_INDEX = load_json("docs_index.json")

DEFAULT_COMPONENT = {
    "evidence_level": "NOT_MEASURED",
    "verification": "NOT_VERIFIED",
    "qualification": "NOT_QUALIFIED",
    "dependencies": [],
    "capabilities": [],
    "limitations": [],
    "source": "[SOURCE_REPOSITORY]",
    "version": "[COMMIT_HASH]",
}

ALL_COMPONENTS: List[dict] = []
for _section in REGISTRY["sections"]:
    for _c in _section["components"]:
        full = {"section": _section["id"], "section_name": _section["name"], **DEFAULT_COMPONENT, **_c}
        ALL_COMPONENTS.append(full)

COMPONENTS_BY_ID = {c["id"]: c for c in ALL_COMPONENTS}
REGISTRY_SHA256 = sha256_of(REGISTRY)
STATUS_VOCAB = [
    "IMPLEMENTED", "INTEGRATION_REQUIRED", "TEST_REQUIRED",
    "VERIFICATION_REQUIRED", "QUALIFICATION_REQUIRED", "NOT_MEASURED", "BLOCKED",
]
DEPLOYMENT_VOCAB = ["DEVELOPMENT", "STAGING", "PRODUCTION", "NOT_DEPLOYED"]


def status_counts() -> Dict[str, int]:
    return dict(Counter(c["status"] for c in ALL_COMPONENTS))


# ---------------------------------------------------------------- security
RATE_LIMIT_PER_MIN = int(os.environ.get("EXECUTION_RATE_LIMIT_PER_MIN", "30"))
_rate_bucket: Dict[str, tuple] = {}


def enforce_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start, count = _rate_bucket.get(ip, (now, 0))
    if now - window_start > 60:
        window_start, count = now, 0
    count += 1
    _rate_bucket[ip] = (window_start, count)
    if count > RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="Rate limit exceeded: execution requests are limited per minute. This is recorded in the audit log.")


async def audit(event: str, detail: dict) -> dict:
    doc = {"id": str(uuid.uuid4()), "event": event, "detail": detail, "time": utcnow()}
    await db.audit_log.insert_one(dict(doc))
    return doc


# ---------------------------------------------------------------- models
class ExecutionCreate(BaseModel):
    connector_id: str
    task: str = Field(min_length=1, max_length=200)
    params: dict = Field(default_factory=dict)


# ---------------------------------------------------------------- core routes
@api_router.get("/")
async def root():
    return {"system": "KETCHUM SYSTEM-OF-SYSTEMS", "layer": "public infrastructure API", "invariant": REGISTRY["invariant"]}


@api_router.get("/health")
async def health():
    t0 = time.perf_counter()
    try:
        await db.command("ping")
        mongo_ms = round((time.perf_counter() - t0) * 1000, 2)
        mongo_state = "reachable"
    except Exception as e:
        mongo_ms = round((time.perf_counter() - t0) * 1000, 2)
        mongo_state = f"unreachable ({e})"
    return {
        "status": "ok",
        "datastore": mongo_state,
        "datastore_ping_ms": mongo_ms,
        "uptime_s": round(time.time() - START_TIME, 1),
        "time": utcnow(),
    }


@api_router.get("/manifest")
async def manifest():
    return {
        **MANIFEST_BASE,
        "registry_sha256": REGISTRY_SHA256,
        "component_count": len(ALL_COMPONENTS),
        "status_counts": status_counts(),
        "connector_count": len(CONNECTORS),
        "uptime_s": round(time.time() - START_TIME, 1),
        "generated_at": utcnow(),
    }


@api_router.get("/inspect")
async def inspect(format: str = "json"):
    """Single public snapshot for external inspection (web readers, verifiers). Live, read-only, no fabrication."""
    from fastapi.responses import PlainTextResponse
    from lifecycle import evidence_verify

    chain = await evidence_verify()
    transitions = await db.transitions.aggregate([{"$group": {"_id": "$outcome", "n": {"$sum": 1}}}]).to_list(10)
    ledger = {t["_id"]: t["n"] for t in transitions}
    ledger_total = sum(ledger.values())
    from eil import CONSTITUTION, CONSTITUTION_SHA256
    auth_doc = await db.eil_state.find_one({"id": "authority_state"}, {"_id": 0}) or {}
    ledger_count = await db.authority_transitions.count_documents({})

    data = {
        "system": REGISTRY["name"],
        "tagline": REGISTRY["tagline"],
        "invariant": REGISTRY["invariant"],
        "release": {"version": MANIFEST_BASE["version"], "channel": MANIFEST_BASE["release_channel"], "registry_sha256": REGISTRY_SHA256},
        "component_count": len(ALL_COMPONENTS),
        "status_counts": status_counts(),
        "connectors": [{"id": c.id, "name": c.name, "configured": c.is_configured(), "deployment_state": "CONFIGURED" if c.is_configured() else "NOT_CONFIGURED"} for c in CONNECTORS.values()],
        "evidence_chain": {"status": chain["status"], "records_checked": chain["records_checked"], "chained": chain.get("chained_records"), "tampered": chain["tampered_record_ids"], "chain_broken": chain["chain_broken_record_ids"], "head": chain["chain_head"], "algorithm": chain["algorithm"]},
        "transition_ledger": {"total_attempts": ledger_total, "outcomes": ledger, "note": "Registry statuses are never mutated by the application; ledger entries are provenance for the authoritative owner."},
        "verification": {"verified_components": 0, "reason": "No independent witness connected. [INDEPENDENT_WITNESS_REQUIRED]"},
        "qualification": {"qualified_components": 0, "reason": "TEVV qualification gates have not been run. [QUALIFICATION_REQUIRED]"},
        "ai_runtime": {"configured": bool(os.environ.get("EMERGENT_LLM_KEY")), "models": [{"slug": s, "model": os.environ.get(f"AI_MODEL_{s.upper()}", f"gpt-6-{s}")} for s in ("sol", "luna")]},
        "docs_available": len(DOCS_INDEX),
        "eil": (lambda c, a: {
            "constitution_version": c["version"],
            "constitution_sha256": CONSTITUTION_SHA256,
            "frozen": c["frozen"],
            "permitted_delegation_types": len(c.get("permitted_delegation_types", [])),
            "authority_state": a.get("authority_state", "RESERVED_HUMAN"),
            "machine_authority": a.get("machine_authority", "NONE"),
            "authority_ledger_entries": ledger_count,
            "invariant_check": "/api/eil/invariant-check",
            "note": "EIL is the constitutional engine beneath the KSI boundary. All authority transitions DENY in v1 (no ratified delegation types).",
        })(CONSTITUTION, await db.eil_state.find_one({"id": "authority_state"}, {"_id": 0}) or {}),
        "inspection_urls": ["/api/inspect?format=md", "/api/system", "/api/components", "/api/evidence", "/api/evidence/verify", "/api/transitions", "/api/ksi", "/api/authority", "/api/manifest", "/api/health", "/api/docs", "/api/ai/models"],
        "honesty_statement": "This snapshot is generated live from the running system. Nothing is simulated: unconfigured integrations are reported as such, and zero verification / zero qualification is the current truth.",
    }

    if format == "md":
        lines = [
            f"# {data['system']} — External Inspection Snapshot",
            "",
            f"> {data['invariant']}",
            "",
            f"- Release: v{data['release']['version']} ({data['release']['channel']}) · registry SHA-256 `{data['release']['registry_sha256'][:32]}…`",
            f"- Components: {data['component_count']} — " + ", ".join(f"{k}: {v}" for k, v in data["status_counts"].items()),
            "",
            "## Connectors",
            "",
        ]
        lines += [f"- {c['id']} {c['name']} → **{c['deployment_state']}**" for c in data["connectors"]]
        lines += [
            "",
            "## Evidence chain (tamper detection)",
            "",
            f"- Status: **{chain['status']}** — {chain['records_checked']} records ({chain.get('chained_records')} hash-chained), head `{chain['chain_head'][:32]}…`",
            f"- Tampered: {len(chain['tampered_record_ids'])} · Chain broken: {len(chain['chain_broken_record_ids'])}",
            "",
            "## Transition ledger",
            "",
            f"- {ledger_total} attempts — " + (", ".join(f"{k}: {v}" for k, v in ledger.items()) if ledger else "empty"),
            "",
            "## Verification & qualification",
            "",
            f"- Verified components: **0** — {data['verification']['reason']}",
            f"- Qualified components: **0** — {data['qualification']['reason']}",
            "",
            "## AI runtime",
            "",
            f"- Configured: {data['ai_runtime']['configured']} — models: " + ", ".join(m["model"] for m in data["ai_runtime"]["models"]),
            "",
            "## Inspect further (plain JSON, crawlable)",
            "",
        ]
        lines += [f"- `{u}`" for u in data["inspection_urls"]]
        lines += ["", f"*{data['honesty_statement']}*", ""]
        return PlainTextResponse("\n".join(lines), media_type="text/markdown")
    return data


# ---------------------------------------------------------------- system + registry
@api_router.get("/system")
async def system():
    return {
        "name": REGISTRY["name"],
        "tagline": REGISTRY["tagline"],
        "invariant": REGISTRY["invariant"],
        "sections": REGISTRY["sections"],
        "total_components": len(ALL_COMPONENTS),
        "status_counts": status_counts(),
        "note": "Statuses describe the public infrastructure layer built by this package. Placeholders in [BRACKETS] await authoritative data.",
    }


@api_router.get("/capabilities")
async def capabilities():
    caps = []
    for c in ALL_COMPONENTS:
        if c["capabilities"]:
            caps.append({"component_id": c["id"], "component": c["name"], "capabilities": c["capabilities"], "status": c["status"]})
    return {"capabilities": caps, "note": "Capability is not evidence. Capabilities listed here are implemented interfaces only."}


@api_router.get("/components")
async def list_components(
    section: Optional[str] = None,
    status: Optional[str] = None,
    evidence: Optional[str] = None,
    verification: Optional[str] = None,
    deployment: Optional[str] = None,
    q: Optional[str] = None,
):
    items = ALL_COMPONENTS
    if section:
        items = [c for c in items if c["section"] == section]
    if status:
        items = [c for c in items if c["status"] == status]
    if evidence:
        items = [c for c in items if c["evidence_level"] == evidence]
    if verification:
        items = [c for c in items if c["verification"] == verification]
    if deployment:
        items = [c for c in items if c["deployment"] == deployment]
    if q:
        needle = q.lower()
        items = [c for c in items if needle in c["name"].lower() or needle in c.get("purpose", "").lower()]
    return {"total": len(items), "components": items, "status_vocab": STATUS_VOCAB, "deployment_vocab": DEPLOYMENT_VOCAB}


@api_router.get("/components/{component_id}")
async def get_component(component_id: str):
    c = COMPONENTS_BY_ID.get(component_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Component '{component_id}' not in registry.")
    return c


# ---------------------------------------------------------------- live tests / executions
@api_router.get("/tasks")
async def tasks():
    catalog = []
    for conn in CONNECTORS.values():
        catalog.append({**conn.describe(), "configured": conn.is_configured(), "suggested_tasks": conn.suggested_tasks})
    return {
        "connectors": catalog,
        "principle": "Execution results reflect real runtime state only. When a connector is not configured, the API returns NOT_CONFIGURED — never a simulated success.",
    }


@api_router.post("/executions")
@api_router.post("/test/run")
async def create_execution(payload: ExecutionCreate, request: Request):
    enforce_rate_limit(request)
    conn = CONNECTORS.get(payload.connector_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Connector '{payload.connector_id}' is not registered.")

    result = await asyncio.to_thread(conn.execute, payload.task, payload.params)

    execution = {
        "id": str(uuid.uuid4()),
        "connector_id": conn.id,
        "connector_name": conn.name,
        "task": payload.task,
        "params": payload.params,
        "state": result.state,
        "ok": result.ok,
        "summary": result.summary,
        "details": result.details,
        "measured": result.measured,
        "evidence_level": result.evidence_level,
        "source": "public_app_live_test",
        "created_at": utcnow(),
    }
    from lifecycle import next_chain, evidence_hash, update_anchor

    seq, prev_hash = await next_chain(db)
    evidence_record = {
        "id": str(uuid.uuid4()),
        "type": "execution_result",
        "execution_id": execution["id"],
        "connector_id": conn.id,
        "claim": result.summary,
        "level": "NOT_MEASURED",
        "test_result": result.state,
        "verified": False,
        "qualified": False,
        "authorized": False,
        "provisional_level": None,
        "provenance": {
            "source": "public_app_live_test",
            "recorded_at": utcnow(),
            "environment": os.environ.get("RELEASE_CHANNEL", "development"),
            "source_repo": "[SOURCE_REPOSITORY]",
            "source_commit": "[COMMIT_HASH]",
            "artifact_id": execution["id"],
            "input_hash": sha256_of({"connector_id": conn.id, "task": payload.task, "params": payload.params}),
            "output_hash": sha256_of({"state": result.state, "measured": result.measured}),
            "runtime_result": result.state,
            "logs": "[TRACE_PENDING]",
        },
        "chain": {"seq": seq, "algorithm": "sha256-chain-v1"},
        "note": "E0-E5 level mapping awaits authoritative definitions; this record asserts no evidence level.",
        "append_mode": "append_by_convention_with_tamper_detection",
        "created_at": utcnow(),
    }
    evidence_record["hash"] = evidence_hash(evidence_record)
    evidence_record["chain"]["prev_hash"] = prev_hash

    await db.executions.insert_one(dict(execution))
    await db.evidence_records.insert_one(dict(evidence_record))
    await update_anchor(db, evidence_record["hash"], seq)
    await audit("execution.attempt", {"execution_id": execution["id"], "connector_id": conn.id, "state": result.state})
    return {"execution": execution, "evidence_record": evidence_record}


@api_router.get("/executions")
async def list_executions(limit: int = 25):
    limit = max(1, min(limit, 100))
    items = await db.executions.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return {"total": len(items), "executions": items}


@api_router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    doc = await db.executions.find_one({"id": execution_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Execution not found.")
    return doc


# ---------------------------------------------------------------- evidence
@api_router.get("/evidence")
async def evidence(limit: int = 50):
    limit = max(1, min(limit, 100))
    records = await db.evidence_records.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return {
        "levels": EVIDENCE_MODEL["levels"],
        "rules": EVIDENCE_MODEL["rules"],
        "records": records,
        "record_count": len(records),
        "note": "Records below are real records created by this application, hash-chained for tamper detection (verify at /api/evidence/verify). Fields marked [PLACEHOLDER] await authoritative data. No record asserts an evidence level.",
    }


# ---------------------------------------------------------------- verification / qualification
@api_router.get("/verification")
async def verification():
    verified = [c["id"] for c in ALL_COMPONENTS if c["verification"] == "VERIFIED"]
    return {
        "status": "NOT_MEASURED",
        "verified_component_count": len(verified),
        "verified_component_ids": verified,
        "external_verifier": "[INDEPENDENT_WITNESS_REQUIRED]",
        "statement": "No component in this registry has been independently verified. Verification requires an independent witness outside this application.",
        "rule": "Capability does not imply verification. Verification does not imply qualification.",
    }


@api_router.get("/qualification")
async def qualification():
    qualified = [c["id"] for c in ALL_COMPONENTS if c["qualification"] == "QUALIFIED"]
    return {
        "status": "NOT_MEASURED",
        "qualified_component_count": len(qualified),
        "qualified_component_ids": qualified,
        "statement": "No component in this registry is qualified. Qualification requires TEVV gates that have not been run by an independent party.",
        "rule": "QUALIFICATION_REQUIRED is the highest status any component here may honestly hold today.",
    }


# ---------------------------------------------------------------- authority
@api_router.get("/authority")
async def authority(limit: int = 20):
    limit = max(1, min(limit, 100))
    trail = await db.audit_log.find({}, {"_id": 0}).sort("time", -1).to_list(limit)
    return {
        "principles": AUTHORITY_MODEL["principles"],
        "levels": AUTHORITY_MODEL["levels"],
        "lifecycle": AUTHORITY_MODEL["lifecycle"],
        "enforcement_status": AUTHORITY_MODEL["enforcement_status"],
        "audit_trail": trail,
        "invariant": "AUTHORITY belongs to humans. A system's ability to act is capability, never authority.",
    }


# ---------------------------------------------------------------- documentation
@api_router.get("/docs")
async def docs_list():
    items = []
    for entry in DOCS_INDEX:
        path = DOCS_DIR / entry["file"]
        exists = path.exists()
        items.append({**entry, "available": exists})
    return {"docs": items, "note": "These documents are the build specification of this package. Status column reflects build state, not product claims."}


@api_router.get("/docs/{slug}")
async def docs_content(slug: str):
    entry = next((d for d in DOCS_INDEX if d["slug"] == slug), None)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Document '{slug}' not found.")
    path = DOCS_DIR / entry["file"]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Document file for '{slug}' is missing.")
    content = path.read_text(encoding="utf-8")
    return {**entry, "content": content}


app.include_router(api_router)

from ai_assistant import ai_router  # AI reasoning layer (grounded assistants)
app.include_router(ai_router)

from ksi import ksi_router  # KSI authorization boundary (local stand-in policy engine)
app.include_router(ksi_router)

from lifecycle import lifecycle_router  # lifecycle transitions, evidence chain integrity, reproduction
app.include_router(lifecycle_router)

from eil import eil_router  # EIL constitutional engine (beneath the KSI boundary)
app.include_router(eil_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
