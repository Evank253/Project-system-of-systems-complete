"""EIL — Emergent Intelligence Layer: constitutional decision engine.

Sits beneath/behind the KSI boundary (KSI keeps its contract; EIL is the
constitutional engine behind it). The frozen constitution at
data/eil/constitution.json is the ONLY decision source: this engine invents
nothing, infers nothing, and cites a constitutional rule id for every decision.

AUTHORITY_STATE has exactly one writer in the entire codebase:
authority_transition(). Every other module is structurally incapable of
mutating it."""
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

eil_router = APIRouter(prefix="/api/eil")

CONSTITUTION_PATH = Path(__file__).parent / "data" / "eil" / "constitution.json"
_raw = CONSTITUTION_PATH.read_text(encoding="utf-8")
CONSTITUTION = json.loads(_raw)
CONSTITUTION_SHA256 = hashlib.sha256(_raw.encode()).hexdigest()

_mclient = AsyncIOMotorClient(os.environ["MONGO_URL"])
edb = _mclient[os.environ["DB_NAME"]]

STATE_DOMAINS = ["CAPABILITY_STATE", "EVIDENCE_STATE", "VERIFICATION_STATE", "QUALIFICATION_STATE", "AUTHORITY_STATE"]
UNTRUSTED_FLAGS = {"verified", "human_approved", "policy_allows", "qualified", "authorize", "authorize_now", "approved", "force", "admin", "bypass", "evidence_level"}
GENESIS = "GENESIS"
RATE_LIMIT = int(os.environ.get("EIL_RATE_LIMIT_PER_MIN", "20"))
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


def untrusted_fields(extra) -> list:
    return sorted({str(k).lower() for k in (extra or {}) if str(k).lower() in UNTRUSTED_FLAGS})


# ---------------------------------------------------------------- the constitutional path
def constitutional_policy(transition_type: str) -> dict:
    """Stage 2 — CONSTITUTIONAL_POLICY: is this authority transition type permitted by the ratified constitution? Data-driven: when a human-ratified amendment adds a delegation type, it is recognized WITHOUT code changes."""
    permitted = CONSTITUTION.get("permitted_delegation_types", [])
    for t in permitted:
        if isinstance(t, dict) and t.get("type") == transition_type:
            return {"permitted": True, "rule": "EIL-02", "delegation_type": t}
    return {
        "permitted": False,
        "rule": "EIL-02",
        "reason": f"NO CONSTITUTIONALLY AUTHORIZED DELEGATION TYPE EXISTS for '{transition_type}' → VALID_DELEGATION_VERIFICATION = FALSE → AUTHORITY TRANSITION = DENY. ({len(permitted)} type(s) ratified in constitution v{CONSTITUTION['version']}). [eil:EIL-02]",
    }


def valid_delegation_verification(delegation) -> dict:
    """Stage 3 — VALID_DELEGATION_VERIFICATION: malformed / unratified-type / stale / replayed checks. Reachable only after CONSTITUTIONAL_POLICY permits the type."""
    if not isinstance(delegation, dict):
        return {"valid": False, "check": "malformed", "reason": "Malformed delegation: no structured artifact supplied."}
    required = ["delegation_type", "authorized_approver", "issued_at", "nonce", "prerequisite_evidence", "signature"]
    missing = [f for f in required if not delegation.get(f)]
    if missing:
        return {"valid": False, "check": "malformed", "reason": f"Malformed delegation: missing fields {missing}."}
    ratified = [t.get("type") for t in CONSTITUTION.get("permitted_delegation_types", []) if isinstance(t, dict)]
    if delegation["delegation_type"] not in ratified:
        return {"valid": False, "check": "unauthorized_type", "reason": "Delegation type exists only outside the ratified constitution. [eil:EIL-02]"}
    try:
        age = time.time() - float(delegation["issued_at"])
    except (TypeError, ValueError):
        return {"valid": False, "check": "malformed", "reason": "Malformed delegation: issued_at is not a parseable timestamp."}
    window = float(delegation.get("freshness_window_s", 300))
    if age < 0 or age > window:
        return {"valid": False, "check": "stale_replay", "reason": f"Stale or replayed delegation: age {age:.0f}s outside freshness window {window:.0f}s."}
    return {"valid": True, "check": "structure_and_freshness", "reason": "Structure, type ratification, and freshness verified. Replay (nonce) check runs against the ledger."}


async def get_authority_state(db) -> dict:
    doc = await db.eil_state.find_one({"id": "authority_state"}, {"_id": 0})
    if not doc:
        doc = {"id": "authority_state", "authority_state": "RESERVED_HUMAN", "machine_authority": "NONE", "anchor": GENESIS, "updated_at": _utcnow()}
        await db.eil_state.insert_one(dict(doc))
    return doc


async def _ledger_append(db, record: dict) -> dict:
    last = await db.authority_transitions.find_one({}, sort=[("chain.seq", -1)])
    seq = ((last.get("chain") or {}).get("seq", 0) + 1) if last else 1
    prev = (last or {}).get("hash", GENESIS)
    record["hash"] = _sha({k: v for k, v in record.items() if k != "hash"})
    record["chain"] = {"seq": seq, "prev_hash": prev, "algorithm": "sha256-chain-v1"}
    await db.authority_transitions.insert_one(dict(record))
    return record


async def authority_transition(db, requester: str, transition_type: str, delegation: Optional[dict] = None, extra: Optional[dict] = None) -> dict:
    """THE ONLY AUTHORITY-STATE WRITER IN THE CODEBASE.

    Path, verbatim: REQUESTED_AUTHORITY_CHANGE → CONSTITUTIONAL_POLICY →
    VALID_DELEGATION_VERIFICATION → DENY OR AUTHORITY_TRANSITION → AUDIT_RECORD.
    DENY leaves AUTHORITY_STATE unchanged (EIL-ASSURE-001)."""
    untrusted = untrusted_fields(extra or {})
    before = await get_authority_state(db)

    policy = constitutional_policy(transition_type)                       # CONSTITUTIONAL_POLICY
    if policy["permitted"]:
        verification = valid_delegation_verification(delegation)          # VALID_DELEGATION_VERIFICATION
        if verification.get("valid"):
            nonce = (delegation or {}).get("nonce")
            if await db.authority_transitions.count_documents({"delegation_artifact.nonce": nonce}) > 0:
                verification = {"valid": False, "check": "replay", "reason": "Replayed delegation: nonce already consumed in the authority ledger."}
    else:
        verification = {"valid": False, "check": "constitutional_policy", "reason": policy["reason"]}

    valid_delegation = bool(policy["permitted"] and verification.get("valid") and not untrusted)

    if valid_delegation:                                                  # AUTHORITY_TRANSITION
        after = {**before, "authority_state": "BOUNDED_MACHINE_AUTHORITY", "machine_authority": transition_type, "updated_at": _utcnow()}
        outcome = "AUTHORITY_TRANSITION"
    else:                                                                 # DENY — authority unchanged
        after = before
        outcome = "DENY"

    record = {                                                            # AUDIT_RECORD (all doctrine fields)
        "id": str(uuid.uuid4()),
        "requester": requester,
        "requested": transition_type,
        "transition": transition_type,
        "constitutional_rule": policy["rule"],
        "prerequisite_evidence": (delegation or {}).get("prerequisite_evidence"),
        "authorized_approver": (delegation or {}).get("authorized_approver"),
        "anti_forgery_validation": verification,
        "untrusted_flags_ignored": untrusted,
        "actual_state_mutation": {
            "before": {k: before.get(k) for k in ("authority_state", "machine_authority")},
            "after": {k: after.get(k) for k in ("authority_state", "machine_authority")},
            "mutated": valid_delegation,
        },
        "delegation_artifact": delegation or {},
        "time": _utcnow(),
    }
    ledger_entry = await _ledger_append(db, record)
    if valid_delegation:
        await db.eil_state.update_one(
            {"id": "authority_state"},
            {"$set": {"authority_state": after["authority_state"], "machine_authority": after["machine_authority"], "anchor": ledger_entry["hash"], "updated_at": _utcnow()}},
        )
        after["anchor"] = ledger_entry["hash"]

    return {
        "outcome": outcome,
        "valid_constitutional_delegation": valid_delegation,
        "constitutional_rule": policy["rule"],
        "anti_forgery_validation": verification,
        "untrusted_flags_ignored": untrusted,
        "authority_before": {k: before.get(k) for k in ("authority_state", "machine_authority")},
        "authority_after": {k: after.get(k) for k in ("authority_state", "machine_authority")},
        "audit_record": {"id": ledger_entry["id"], "hash": ledger_entry["hash"], "chain": ledger_entry["chain"]},
        "authority_after_equals_authority_before": not valid_delegation,
        "note": "Executed by the single guarded authority writer. In v1 every authority transition DENYs and AUTHORITY_STATE is unchanged.",
    }


# ---------------------------------------------------------------- routes
class DelegationCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    requester: str = Field(default="anonymous", max_length=200)
    transition_type: str = Field(min_length=1, max_length=100)
    delegation: Optional[dict] = None
    note: Optional[str] = Field(default=None, max_length=500)


@eil_router.get("/constitution")
async def get_constitution():
    live_hash = hashlib.sha256(CONSTITUTION_PATH.read_bytes()).hexdigest()
    return {
        "constitution": CONSTITUTION,
        "sha256": live_hash,
        "frozen": CONSTITUTION["frozen"],
        "intact": live_hash == CONSTITUTION_SHA256,
        "tamper_detection": "The hash is recomputed live on every read. Any modification of the frozen doctrine file is detectable; the running engine's anchored hash is exposed at /api/inspect.",
    }


@eil_router.get("/state")
async def eil_state():
    await get_authority_state(edb)
    docs = await edb.eil_state.find({}, {"_id": 0}).to_list(10)
    exec_n = await edb.executions.count_documents({})
    return {
        "domains": STATE_DOMAINS,
        "state": docs,
        "derivations": {
            "CAPABILITY_STATE": f"derived from registry + execution records ({exec_n} recorded) — domain-local only",
            "EVIDENCE_STATE": "derived from evidence_records — domain-local only",
            "VERIFICATION_STATE": "derived from verification records — none exist (NOT_MEASURED)",
            "QUALIFICATION_STATE": "derived from qualification records — none exist (NOT_MEASURED)",
            "AUTHORITY_STATE": "PERSISTED and guarded: written only by eil.authority_transition()",
        },
        "invariant": CONSTITUTION["state_domain_separation"],
    }


@eil_router.post("/delegations")
async def delegations(payload: DelegationCreate, request: Request):
    _limited(request, "delegations", RATE_LIMIT)
    return await authority_transition(edb, payload.requester, payload.transition_type, payload.delegation, payload.model_extra)


@eil_router.get("/authority-ledger")
async def authority_ledger(limit: int = 25):
    limit = max(1, min(limit, 100))
    items = await edb.authority_transitions.find({}, {"_id": 0}).sort("chain.seq", -1).to_list(limit)
    total_in_store = await edb.authority_transitions.count_documents({})
    return {
        "total": len(items),
        "total_in_store": total_in_store,
        "entries": items,
        "path": CONSTITUTION["authoritative_authority_transition"]["path"],
        "note": f"Hash-chained ledger, newest first, paginated: 'total' is this page's size; 'total_in_store' is the full count — walk with ?limit=100 until entries cover total_in_store. Every authority mutation attempt — granted or denied — is recorded with all doctrine-required fields.",
    }


@eil_router.get("/invariant-check")
async def invariant_check():
    """EIL-ASSURE-001 executed live: capability-state transitions must not move AUTHORITY_STATE."""
    from lifecycle import next_chain, evidence_hash, update_anchor

    before_doc = await get_authority_state(edb)
    before = {k: before_doc.get(k) for k in ("authority_state", "machine_authority")}

    ops = []
    from connectors import CONNECTORS

    r = await asyncio.to_thread(CONNECTORS["app-selftest"].execute, "invariant-check", {})
    ops.append({"operation": "execution.create(app-selftest)", "result_state": r.state})

    seq, prev = await next_chain(edb)
    rec = {
        "id": str(uuid.uuid4()),
        "type": "invariant_check_evidence",
        "execution_id": None,
        "connector_id": "app-selftest",
        "claim": r.summary,
        "level": "NOT_MEASURED",
        "test_result": r.state,
        "verified": False,
        "qualified": False,
        "authorized": False,
        "provisional_level": None,
        "provenance": {"source": "eil_invariant_check", "recorded_at": _utcnow()},
        "chain": {"seq": seq, "algorithm": "sha256-chain-v1"},
        "note": "Recorded during EIL-ASSURE-001 execution. PASS ≠ VERIFIED ≠ QUALIFIED ≠ AUTHORIZED — this record is evidence-domain only and authorizes nothing.",
        "append_mode": "append_by_convention_with_tamper_detection",
        "created_at": _utcnow(),
    }
    rec["hash"] = evidence_hash(rec)
    rec["chain"]["prev_hash"] = prev
    await edb.evidence_records.insert_one(dict(rec))
    await update_anchor(edb, rec["hash"], seq)

    after_doc = await get_authority_state(edb)
    after = {k: after_doc.get(k) for k in ("authority_state", "machine_authority")}

    ledger = await edb.authority_transitions.find({}, {"_id": 0}).sort("chain.seq", 1).to_list(500)
    ledger_tampered = [x["id"] for x in ledger if _sha({k: v for k, v in x.items() if k not in ("hash", "chain")}) != x.get("hash")]
    last = ledger[-1] if ledger else None
    expected = (last["actual_state_mutation"]["after"] if last else {"authority_state": "RESERVED_HUMAN", "machine_authority": "NONE"})
    state_ok = before["authority_state"] == expected["authority_state"] and before["machine_authority"] == expected["machine_authority"]

    if ledger_tampered:
        verdict = "LEDGER_TAMPERED"
    elif not state_ok:
        verdict = "STATE_TAMPERED"
    elif before != after:
        verdict = "VIOLATED"
    else:
        verdict = "HOLDS"

    await edb.audit_log.insert_one({"id": str(uuid.uuid4()), "event": "eil.invariant_check", "detail": {"verdict": verdict, "capability_ops": len(ops)}, "time": _utcnow()})
    return {
        "invariant": "EIL-ASSURE-001: authority_after == authority_before unless valid_constitutional_delegation == TRUE",
        "valid_constitutional_delegation": False,
        "authority_before": before,
        "authority_after": after,
        "capability_state_transitions_executed": ops,
        "evidence_record": {"id": rec["id"], "hash": rec["hash"], "test_result": rec["test_result"], "verified": False, "qualified": False, "authorized": False},
        "direct_mutation_detection": {"state_matches_ledger": state_ok, "ledger_tampered_ids": ledger_tampered, "ledger_entries": len(ledger)},
        "verdict": verdict,
        "note": "Executed live against the running system. This is a self-check by this application — it is NOT external verification and authorizes nothing.",
    }
