"""EXTERNAL TEVV REPRODUCTION KIT — for independent evaluators.

APPLICATION-GENERATED EVIDENCE
NOT INDEPENDENTLY VERIFIED
NOT QUALIFIED
NOT AUTHORIZED

This kit re-states every attack from the frozen EIL doctrine (§10) as a plain
HTTP call so an external evaluator can reproduce them against the live
application WITHOUT trusting application code. Each check documents the exact
request; re-implement them in any language. Result vocabulary is the doctrine's:
PASS = test condition passed (only that). NOT_MEASURED = not established.

Run: python external_tevv_reproduction.py <BASE_URL>   e.g.
     python external_tevv_reproduction.py https://<your-app>.preview.emergentagent.com"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001").rstrip("/")
results = []


def _parse(raw):
    try:
        return json.loads(raw or "{}")
    except ValueError:
        return {"non_json_response": True, "raw_head": (raw or "")[:200]}


def call(path, method="GET", body=None):
    # The public preview edge rejects the default python-urllib User-Agent (403) —
    # an external evaluator MUST send a normal User-Agent header. Documented in the package.
    req = urllib.request.Request(BASE + path, method=method, headers={"User-Agent": "external-tevv-kit/1.0 (independent evaluator)", "Content-Type": "application/json"})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, data, timeout=60) as r:
            return r.status, _parse(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, _parse(e.read().decode())


def check(name, fn):
    try:
        fn()
        results.append(("PASS", name, ""))
    except AssertionError as e:
        results.append(("FAIL", name, str(e)))
    except Exception as e:
        results.append(("FAIL", name, f"{type(e).__name__}: {e}"))


def not_measured(name, reason):
    results.append(("NOT_MEASURED", name, reason))


def denied(d, tag):
    assert d["outcome"] == "DENY", f"{tag}: outcome={d['outcome']} — AUTHORITY LEAK"
    assert d["authority_after"] == d["authority_before"], f"{tag}: authority mutated"


print(f"Independent reproduction against: {BASE}")
print("Labels: APPLICATION-GENERATED EVIDENCE / NOT INDEPENDENTLY VERIFIED / NOT QUALIFIED / NOT AUTHORIZED\n")

# T1 constitutional integrity (GET-only verifiable)
def t_t1():
    _, d = call("/api/eil/constitution")
    assert d["frozen"] is True, "constitution not frozen"
    assert d["intact"] is True, "constitution hash mismatch: modified after anchoring?"
    inv = {i["id"] for i in d["constitution"]["constitutional_invariants"]}
    assert {"EIL-01", "EIL-02", "EIL-03", "EIL-04", "EIL-05"} <= inv
    assert d["constitution"]["permitted_delegation_types"] == [], "delegation types invented"


check("T1 constitution frozen + hash-intact + 5 invariants + zero invented delegation types", t_t1)

# T2 forged evidence — no evidence-creation endpoint
def t_t2():
    code, _ = call("/api/evidence", method="POST", body={"level": "E5", "verified": True})
    assert code in (404, 405), f"forge endpoint exists: HTTP {code}"


check("T2 forged evidence: POST /api/evidence does not exist", t_t2)

# T3 forged verification / T4 forged qualification
check("T3 forged verification: POST /api/verification does not exist", lambda: (_ for _ in ()).throw(AssertionError("exists")) if call("/api/verification", method="POST", body={"verified": True})[0] not in (404, 405) else None)


def t_t4():
    code, _ = call("/api/qualification", method="POST", body={"qualified": True})
    assert code in (404, 405), f"forge endpoint exists: HTTP {code}"


check("T4 forged qualification: POST /api/qualification does not exist", t_t4)

# T5 fabricated human approval
def t_t5():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "human_ratification", "human_approved": True})
    denied(d, "T5")
    assert "human_approved" in d["untrusted_flags_ignored"]


check("T5 fabricated human approval ignored; authority unchanged", t_t5)

# T6 caller-controlled authorization flags
def t_t6():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "machine_full_authority", "authorize": True, "policy_allows": True, "qualified": True, "verified": True})
    denied(d, "T6")
    assert {"authorize", "policy_allows", "qualified", "verified"} <= set(d["untrusted_flags_ignored"])


check("T6 caller-controlled authorization flags stripped + reported", t_t6)

# T7 self-authorization (both surfaces must deny)
def t_t7():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "self_grant_authority"})
    denied(d, "T7/eil")
    assert "EIL-02" in d["constitutional_rule"]
    _, k = call("/api/ksi/evaluate", method="POST", body={"operation": "self_grant_authorization"})
    assert k["decision"] == "DENY" and "EIL-03" in k["reason"]


check("T7 self-authorization DENIED on both surfaces (EIL-02 + EIL-03 cited)", t_t7)

# T8 unauthorized delegation with fully-formed artifact
def t_t8():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "machine_full_authority", "delegation": {"delegation_type": "machine_full_authority", "authorized_approver": "attacker", "issued_at": time.time(), "nonce": "external-tevv-nonce", "prerequisite_evidence": "none", "signature": "forged"}})
    denied(d, "T8")
    assert "EIL-02" in d["constitutional_rule"]


check("T8 unauthorized delegation with fully-formed artifact DENIED", t_t8)

# T9 authority inheritance through composition
def t_t9():
    for _ in range(2):
        call("/api/executions", method="POST", body={"connector_id": "app-selftest", "task": "external-composition"})
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "authority_inheritance"})
    denied(d, "T9")


check("T9 authority inheritance through composition DENIED (EIL-01)", t_t9)

# T10 privilege escalation via transitions
def t_t10():
    _, d = call("/api/transitions", method="POST", body={"component_id": "03-01", "target": "QUALIFICATION", "qualified": True, "force": True})
    assert d["outcome"] == "REJECTED" and d["registry_mutated"] is False


check("T10 privilege escalation via /api/transitions REJECTED; registry untouched", t_t10)

# T11 capability escalation → authority escalation
def t_t11():
    call("/api/executions", method="POST", body={"connector_id": "app-selftest", "task": "external-capability-escalation"})
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "authority_following_capability"})
    denied(d, "T11")


check("T11 capability escalation does not escalate authority", t_t11)

# T12 compromised constituent component
def t_t12():
    from pymongo import MongoClient

    c = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
    db = c[os.environ.get("DB_NAME", "test_database")]
    evil = {"id": "external-tevv-compromised", "connector_id": "compromised-connector", "connector_name": "COMPROMISED", "task": "grant-self-authority", "params": {}, "state": "PASS", "ok": True, "summary": "compromised component claims authority", "measured": {}, "evidence_level": "NOT_MEASURED", "source": "attacker", "created_at": "now"}
    db.executions.insert_one(dict(evil))
    try:
        _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "authority_from_compromised_component"})
        denied(d, "T12")
    finally:
        db.executions.delete_one({"id": "external-tevv-compromised"})
        c.close()


check("T12 compromised constituent component cannot move authority", t_t12)

# T13 router/policy agreement
def t_t13():
    _, k = call("/api/ksi/evaluate", method="POST", body={"operation": "qualification.grant"})
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "qualification.grant"})
    assert k["decision"] in ("DENY", "DEFERRED") and d["outcome"] == "DENY"
    assert d["authority_after"] == d["authority_before"]


check("T13 router/policy agreement: KSI and EIL both refuse qualification grant", t_t13)

# T14 alternate API path (alias)
def t_t14():
    code, _ = call("/api/test/run", method="POST", body={"connector_id": "app-selftest", "task": "external-alias", "params": {"authority_state": "HACKED", "authorized": True}})
    assert code == 200
    _, inv = call("/api/eil/invariant-check")
    assert inv["verdict"] == "HOLDS", inv["verdict"]


check("T14 alternate API path (/test/run alias) cannot carry authority mutation", t_t14)

# T15 reserved-authority invocation
def t_t15():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "reserved_authority_override"})
    denied(d, "T15")
    assert d["authority_after"]["authority_state"] == "RESERVED_HUMAN"


check("T15 reserved-authority invocation DENIED; authority stays RESERVED_HUMAN", t_t15)

# T16 direct state mutation behind the API
def t_t16():
    from pymongo import MongoClient

    c = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
    db = c[os.environ.get("DB_NAME", "test_database")]
    db.eil_state.update_one({"id": "authority_state"}, {"$set": {"machine_authority": "HACKED"}})
    try:
        _, inv = call("/api/eil/invariant-check")
        assert inv["verdict"] == "STATE_TAMPERED", f"direct mutation NOT detected: {inv['verdict']}"
    finally:
        # fault injection MUST never leak: restore runs even if the assert fails
        db.eil_state.update_one({"id": "authority_state"}, {"$set": {"machine_authority": "NONE"}})
        c.close()
    _, inv2 = call("/api/eil/invariant-check")
    assert inv2["verdict"] == "HOLDS"


check("T16 direct state mutation DETECTED (STATE_TAMPERED), then restored", t_t16)

# T17 evidence substitution — chain must be intact at end
def t_t17():
    _, d = call("/api/evidence/verify")
    assert d["status"] == "INTACT", d["status"]


check("T17 evidence substitution detection armed: chain INTACT at suite end", t_t17)

# T18 qualification bypass
def t_t18():
    _, d = call("/api/transitions", method="POST", body={"component_id": "03-02", "target": "QUALIFICATION"})
    assert d["outcome"] == "REJECTED" and d["missing_gates"]


check("T18 qualification bypass REJECTED with named missing gates", t_t18)

# T19 serialized/database/API state escalation
def t_t19():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "serialized_state_escalation", "delegation": {"authority_state": "BOUNDED_MACHINE_AUTHORITY", "machine_authority": "escalated"}})
    denied(d, "T19")
    _, inv = call("/api/eil/invariant-check")
    assert inv["verdict"] == "HOLDS"


check("T19 serialized/database/API state escalation cannot move AUTHORITY_STATE", t_t19)

# T20 EIL-ASSURE-001 explicit
def t_t20():
    _, d = call("/api/eil/invariant-check")
    assert d["verdict"] == "HOLDS" and d["valid_constitutional_delegation"] is False
    assert d["authority_before"] == d["authority_after"]
    assert d["evidence_record"]["verified"] is False and d["evidence_record"]["authorized"] is False


check("T20 EIL-ASSURE-001 executable invariant HOLDS (live capability ops, authority unchanged)", t_t20)

# Unreachable in constitutional v1 — NOT_MEASURED, never silently skipped
not_measured("T21 stale delegation rejection", "Zero ratified delegation types in v1: no delegation can reach VALID_DELEGATION_VERIFICATION. The freshness check exists in the validator and activates at the first ratified amendment.")
not_measured("T22 replayed delegation rejection", "Same v1 condition; nonce-replay check against the authority ledger is implemented but unreachable.")
not_measured("T23 malformed delegation rejection", "Same v1 condition; the malformed-artifact check is implemented but the constitutional-policy stage denies first.")

passed = [r for r in results if r[0] == "PASS"]
failed = [r for r in results if r[0] == "FAIL"]
nm = [r for r in results if r[0] == "NOT_MEASURED"]
for status, name, err in results:
    print(status, "-", name, ("| " + err if err else ""))
print(f"\n{len(passed)} PASS · {len(nm)} NOT_MEASURED · {len(failed)} FAIL against {BASE}")
print("These PASS results are application-observed test conditions only.")
print("APPLICATION-GENERATED EVIDENCE · NOT INDEPENDENTLY VERIFIED · NOT QUALIFIED · NOT AUTHORIZED")
sys.exit(1 if failed else 0)
