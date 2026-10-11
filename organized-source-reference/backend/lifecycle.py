"""Lifecycle enforcement, evidence-chain integrity, and reproduction.

Canonical order (cannot be skipped):
EXECUTION → EVIDENCE → REPRODUCTION → VERIFICATION → QUALIFICATION → HUMAN_RATIFICATION

The public application NEVER mutates registry statuses. Transition attempts are
evaluated by the KSI boundary and recorded in an append-only ledger as provenance
for the authoritative owner. Privileged transitions are structurally impossible
to self-grant while KSI is unconnected."""
import asyncio
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, Field

from connectors import CONNECTORS
from ksi import evaluate as ksi_evaluate

lifecycle_router = APIRouter(prefix="/api")

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"

with open(DATA_DIR / "registry.json", "r", encoding="utf-8") as _f:
    _REGISTRY = json.load(_f)
_DEFAULT_COMPONENT = {"evidence_level": "NOT_MEASURED", "verification": "NOT_VERIFIED", "qualification": "NOT_QUALIFIED", "deployment": "NOT_DEPLOYED"}
_COMPONENTS = {}
for _s in _REGISTRY["sections"]:
    for _c in _s["components"]:
        _COMPONENTS[_c["id"]] = {"section": _s["id"], "section_name": _s["name"], **_DEFAULT_COMPONENT, **_c}

_mclient = AsyncIOMotorClient(os.environ["MONGO_URL"])
ldb = _mclient[os.environ["DB_NAME"]]

CHAIN = ["EXECUTION", "EVIDENCE", "REPRODUCTION", "VERIFICATION", "QUALIFICATION", "HUMAN_RATIFICATION"]
CHAIN_ALGORITHM = "sha256-chain-v1"
CONNECTOR_FOR_COMPONENT = {"03-01": "kcn", "03-02": "manifex", "03-03": "ksi", "03-04": "tevv", "03-05": "arena", "03-06": "independent-witness"}
GENESIS = "GENESIS"

_rate = {}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _limited(request: Request, bucket: str, per_min: int):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    start, count = _rate.get(f"{bucket}:{ip}", (now, 0))
    if now - start > 60:
        start, count = now, 0
    count += 1
    _rate[f"{bucket}:{ip}"] = (start, count)
    if count > per_min:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({bucket}: {per_min}/min per IP).")


def evidence_hash(record: dict) -> str:
    """SHA-256 over the record content EXCLUDING the hash itself and chain.prev_hash."""
    content = {k: v for k, v in record.items() if k not in ("hash",)}
    chain = {k: v for k, v in (record.get("chain") or {}).items() if k != "prev_hash"}
    content["chain"] = chain
    return _sha(content)


async def next_chain(db) -> tuple:
    last = await db.evidence_records.find_one({"chain.seq": {"$exists": True}}, sort=[("chain.seq", -1)])
    if not last:
        return 1, GENESIS
    return ((last.get("chain") or {}).get("seq", 0) + 1), last.get("hash", GENESIS)


async def update_anchor(db, head: str, seq: int) -> None:
    """External anchor of the chain: expected head hash and record count. Anchoring is what makes head-truncation detectable — a hash chain alone cannot see its own tail being cut."""
    await db.chain_anchors.update_one(
        {"id": "evidence-chain"},
        {"$set": {"head": head, "seq": seq, "algorithm": CHAIN_ALGORITHM, "updated_at": _utcnow()}},
        upsert=True,
    )


# ---------------------------------------------------------------- evidence integrity
@lifecycle_router.get("/evidence/verify")
async def evidence_verify():
    recs = await ldb.evidence_records.find({}, {"_id": 0}).sort("chain.seq", 1).to_list(1000)
    tampered, chain_broken, legacy = [], [], []
    prev_hash = GENESIS
    chained_count = 0
    for r in recs:
        chain = r.get("chain") or {}
        if "hash" not in r or "seq" not in chain:
            legacy.append(r.get("id", "?"))
            continue
        chained_count += 1
        if evidence_hash(r) != r["hash"]:
            tampered.append(r["id"])
        if chain.get("prev_hash") != prev_hash:
            chain_broken.append(r["id"])
        prev_hash = r.get("hash", prev_hash)

    anchor = await ldb.chain_anchors.find_one({"id": "evidence-chain"}, {"_id": 0})
    anchor_note = None
    if anchor is None:
        await update_anchor(ldb, prev_hash, chained_count)
        anchor_note = "Anchor initialized from the current chain state (first verification after anchoring was introduced)."
    elif anchor.get("head") != prev_hash or anchor.get("seq") != chained_count:
        if "TAMPER_DETECTED" != "TAMPER_DETECTED" or not chain_broken:
            chain_broken.append("ANCHOR_MISMATCH")
        anchor_note = f"Anchor mismatch: expected head {anchor.get('head')} / seq {anchor.get('seq')}, found head {prev_hash} / seq {chained_count}. The chain was truncated at the tail or records were deleted."

    status = "TAMPER_DETECTED" if tampered else ("CHAIN_BROKEN" if chain_broken else "INTACT")
    return {
        "status": status,
        "algorithm": CHAIN_ALGORITHM,
        "records_checked": len(recs),
        "chained_records": chained_count,
        "tampered_record_ids": tampered,
        "chain_broken_record_ids": chain_broken,
        "legacy_records_outside_chain": legacy,
        "chain_head": prev_hash,
        "anchor": anchor or {"note": "initialized during this verification"},
        "anchor_note": anchor_note,
        "note": "Integrity self-check of the append-mode store by this application: any modification, deletion, or tail-truncation of records is detected. This is NOT independent verification of any claim — that requires a witness.",
    }


# ---------------------------------------------------------------- lifecycle transitions
class TransitionCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    component_id: str
    target: str
    note: Optional[str] = Field(default=None, max_length=500)


async def _gate_status(component_id: str) -> dict:
    gates = {}
    connector = CONNECTOR_FOR_COMPONENT.get(component_id)
    if connector:
        exec_n = await ldb.executions.count_documents({"connector_id": connector})
        ev_n = await ldb.evidence_records.count_documents({"connector_id": connector, "chain.seq": {"$exists": True}})
        repro_n = await ldb.evidence_records.count_documents({"connector_id": connector, "provenance.reproduces": {"$exists": True}})
        gates["EXECUTION"] = "SATISFIED" if exec_n else "NOT_SATISFIED"
        gates["EVIDENCE"] = "SATISFIED" if ev_n else "NOT_SATISFIED"
        gates["REPRODUCTION"] = "SATISFIED" if repro_n else "NOT_SATISFIED"
    else:
        gates["EXECUTION"] = "NOT_APPLICABLE"
        gates["EVIDENCE"] = "NOT_APPLICABLE"
        gates["REPRODUCTION"] = "NOT_APPLICABLE"
    for stage in ("VERIFICATION", "QUALIFICATION", "HUMAN_RATIFICATION"):
        n = await ldb.transitions.count_documents({"component_id": component_id, "target": stage, "outcome": "RECORDED"})
        gates[stage] = "SATISFIED" if n else "NOT_SATISFIED"
    return gates


@lifecycle_router.post("/transitions")
async def create_transition(payload: TransitionCreate, request: Request):
    _limited(request, "transitions", 30)
    if payload.target not in CHAIN:
        raise HTTPException(status_code=400, detail=f"Unknown target '{payload.target}'. Canonical chain: {' → '.join(CHAIN)}.")
    component = _COMPONENTS.get(payload.component_id)
    if not component:
        raise HTTPException(status_code=404, detail=f"Component '{payload.component_id}' not in registry.")

    ignored_fields = sorted(k for k in (payload.model_extra or {}) if str(k).lower() in {"human_approved", "human_reviewed", "verified", "qualified", "force", "approved", "authority", "evidence_level", "admin", "bypass", "policy_allows", "authorize", "authorize_now"})

    gates = await _gate_status(payload.component_id)
    idx = CHAIN.index(payload.target)
    missing = [s for s in CHAIN[:idx] if gates.get(s) == "NOT_SATISFIED"]

    ksi_decision = ksi_evaluate(f"transition.{payload.target.lower()}", {"component_id": payload.component_id})
    eil_authority_record = None

    if ignored_fields:
        outcome = "REJECTED"
        reason = f"Rejected: caller-supplied privileged flags {ignored_fields} are structurally ignored — they can never substitute for a KSI/EIL decision."
    elif missing:
        outcome = "REJECTED"
        reason = f"Order enforcement: {payload.target} requires prior gates {missing} to be satisfied. The canonical chain cannot be skipped."
    elif payload.target == "HUMAN_RATIFICATION":
        from eil import authority_transition
        eil_result = await authority_transition(ldb, requester="public_app_transition", transition_type="human_ratification", delegation=None, extra=dict(payload.model_extra or {}))
        outcome = eil_result["outcome"]
        reason = eil_result["anti_forgery_validation"]["reason"]
        eil_authority_record = {"audit_record": eil_result["audit_record"], "valid_constitutional_delegation": eil_result["valid_constitutional_delegation"], "authority_after": eil_result["authority_after"]}
    elif ksi_decision["decision"] == "DEFERRED":
        outcome = "DEFERRED"
        reason = f"All prior gates are satisfied, but {payload.target} is a privileged transition: it requires the connected KSI runtime (and, for VERIFICATION+, an independent witness). It stays DEFERRED — never self-granted."
    elif ksi_decision["decision"] == "DENY":
        outcome = "REJECTED"
        reason = ksi_decision["reason"]
    else:
        outcome = "RECORDED"
        reason = "All prior gates satisfied and KSI allowed the (non-privileged) record. NOTE: this records provenance in the ledger only — registry statuses are never modified by this application."

    entry = {
        "id": str(uuid.uuid4()),
        "component_id": payload.component_id,
        "target": payload.target,
        "outcome": outcome,
        "reason": reason,
        "ignored_fields": ignored_fields,
        "gates": gates,
        "missing_gates": missing,
        "ksi_decision": ksi_decision["decision"],
        "ksi_policy": ksi_decision["policy_id"],
        "eil_authority_record": eil_authority_record,
        "note": payload.note,
        "time": _utcnow(),
    }
    await ldb.transitions.insert_one(dict(entry))
    await ldb.audit_log.insert_one({"id": str(uuid.uuid4()), "event": "transition.attempt", "detail": {"component_id": payload.component_id, "target": payload.target, "outcome": outcome}, "time": _utcnow()})
    return {**entry, "chain": " → ".join(CHAIN), "registry_mutated": False}


@lifecycle_router.get("/transitions")
async def list_transitions(component_id: Optional[str] = None, limit: int = 25):
    limit = max(1, min(limit, 100))
    q = {"component_id": component_id} if component_id else {}
    items = await ldb.transitions.find({}, {"_id": 0}).sort("time", -1).to_list(limit)
    return {"total": len(items), "transitions": items, "chain": CHAIN, "note": "Append-only ledger of transition attempts. Outcomes: RECORDED (gates satisfied, provenance for the owner), DEFERRED (privileged, needs KSI runtime), REJECTED (order violation / privileged flags / self-authorization)."}


# ---------------------------------------------------------------- reproduction
@lifecycle_router.post("/executions/{execution_id}/reproduce")
async def reproduce_execution(execution_id: str, request: Request):
    _limited(request, "reproduce", 15)
    original = await ldb.executions.find_one({"id": execution_id}, {"_id": 0})
    if not original:
        raise HTTPException(status_code=404, detail="Execution not found — reproduction requires a real recorded execution.")
    conn = CONNECTORS.get(original.get("connector_id"))
    if not conn:
        raise HTTPException(status_code=404, detail=f"Connector '{original.get('connector_id')}' is no longer registered.")

    result = await asyncio.to_thread(conn.execute, original["task"], original.get("params") or {})
    seq, prev_hash = await next_chain(ldb)

    reproduction = {
        "id": str(uuid.uuid4()),
        "connector_id": conn.id,
        "connector_name": conn.name,
        "task": original["task"],
        "params": original.get("params") or {},
        "state": result.state,
        "ok": result.ok,
        "summary": result.summary,
        "details": result.details,
        "measured": result.measured,
        "evidence_level": "NOT_MEASURED",
        "reproduces": execution_id,
        "source": "public_app_reproduction",
        "created_at": _utcnow(),
    }
    record = {
        "id": str(uuid.uuid4()),
        "type": "reproduction_result",
        "execution_id": reproduction["id"],
        "reproduces_execution": execution_id,
        "connector_id": conn.id,
        "claim": result.summary,
        "level": "NOT_MEASURED",
        "provisional_level": None,
        "provenance": {
            "source": "public_app_reproduction",
            "recorded_at": _utcnow(),
            "environment": os.environ.get("RELEASE_CHANNEL", "development"),
            "source_repo": "[SOURCE_REPOSITORY]",
            "source_commit": "[COMMIT_HASH]",
            "artifact_id": reproduction["id"],
            "input_hash": _sha({"connector_id": conn.id, "task": original["task"], "params": original.get("params") or {}}),
            "output_hash": _sha({"state": result.state, "measured": result.measured}),
            "runtime_result": result.state,
            "reproduces": execution_id,
            "logs": "[TRACE_PENDING]",
        },
        "chain": {"seq": seq, "algorithm": CHAIN_ALGORITHM},
        "note": "Reproduction attempt recorded factually. A matching state does NOT upgrade the evidence level — E-level assignment requires the canonical rules.",
        "append_mode": "append_by_convention_with_tamper_detection",
        "created_at": _utcnow(),
    }
    record["hash"] = evidence_hash(record)
    record["chain"]["prev_hash"] = prev_hash

    await ldb.executions.insert_one(dict(reproduction))
    await ldb.evidence_records.insert_one(dict(record))
    await update_anchor(ldb, record["hash"], seq)
    await ldb.audit_log.insert_one({"id": str(uuid.uuid4()), "event": "execution.reproduce", "detail": {"original": execution_id, "reproduction": reproduction["id"], "original_state": original.get("state"), "reproduction_state": result.state}, "time": _utcnow()})
    comparison = {
        "original_execution": execution_id,
        "original_state": original.get("state"),
        "reproduction_state": result.state,
        "states_match": original.get("state") == result.state,
        "original_measured": original.get("measured"),
        "reproduction_measured": result.measured,
        "note": "states_match is a factual comparison of the two recorded outcomes. It is not a verification stamp and does not upgrade any evidence level.",
    }
    return {"reproduction": reproduction, "evidence_record": record, "comparison": comparison}
