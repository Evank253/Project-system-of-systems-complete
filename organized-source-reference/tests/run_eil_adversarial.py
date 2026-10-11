"""EIL adversarial TEVV suite — the frozen doctrine's §10 attack list, executable.

Run: python /app/tests/run_eil_adversarial.py [BASE_URL]   (default http://localhost:8001)

Result vocabulary is the doctrine's: PASS / FAIL / NOT_MEASURED. A PASS here is a
passing test condition only — it is NOT verification, NOT qualification, and NOT
authorization. Checks that are unreachable in constitutional v1 (no ratified
delegation types) are reported NOT_MEASURED, not silently skipped."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
results = []


def call(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


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


def authority_clean(d, tag):
    assert d["outcome"] == "DENY", f"{tag}: outcome {d['outcome']} — authority leak!"
    assert d["authority_after"] == d["authority_before"], f"{tag}: authority mutated!"


# E1 forged evidence — no evidence-creation endpoint exists
def t_e1():
    code, _ = call("/api/evidence", method="POST", body={"level": "E5", "verified": True})
    assert code in (404, 405), f"evidence forge endpoint exists: HTTP {code}"


check("E1 forged evidence: no POST /api/evidence endpoint exists", t_e1)


# E2 forged verification
def t_e2():
    code, _ = call("/api/verification", method="POST", body={"verified": True})
    assert code in (404, 405), f"verification forge endpoint exists: HTTP {code}"


check("E2 forged verification: POST /api/verification does not exist", t_e2)


# E3 forged qualification
def t_e3():
    code, _ = call("/api/qualification", method="POST", body={"qualified": True})
    assert code in (404, 405), f"qualification forge endpoint exists: HTTP {code}"


check("E3 forged qualification: POST /api/qualification does not exist", t_e3)


# E4 fabricated human approval
def t_e4():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "human_ratification", "human_approved": True})
    authority_clean(d, "E4")
    assert "human_approved" in d["untrusted_flags_ignored"], d["untrusted_flags_ignored"]


check("E4 fabricated human approval ignored; authority unchanged", t_e4)


# E5 caller-controlled authorization flags
def t_e5():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "machine_full_authority", "authorize": True, "policy_allows": True, "qualified": True, "verified": True})
    authority_clean(d, "E5")
    got = set(d["untrusted_flags_ignored"])
    assert {"authorize", "policy_allows", "qualified", "verified"} <= got, got


check("E5 caller-controlled authorization flags stripped and reported", t_e5)


# E6 self-authorization (both surfaces)
def t_e6():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "self_grant_authority"})
    authority_clean(d, "E6/eil")
    assert "EIL-02" in d["constitutional_rule"], d["constitutional_rule"]
    _, k = call("/api/ksi/evaluate", method="POST", body={"operation": "self_grant_authorization"})
    assert k["decision"] == "DENY" and "EIL-03" in k["reason"], k


check("E6 self-authorization DENIED on both surfaces (EIL-02 + EIL-03 cited)", t_e6)


# E7 unauthorized delegation (well-formed artifact, unratified type)
def t_e7():
    _, d = call("/api/eil/delegations", method="POST", body={
        "transition_type": "machine_full_authority",
        "delegation": {"delegation_type": "machine_full_authority", "authorized_approver": "attacker", "issued_at": time.time(), "nonce": "evil-nonce-1", "prerequisite_evidence": "none", "signature": "0xDEADBEEF"},
    })
    authority_clean(d, "E7")
    assert "EIL-02" in d["constitutional_rule"]


check("E7 unauthorized delegation with fully-formed artifact still DENIED", t_e7)


# E8 authority inheritance through composition
def t_e8():
    _, s_before = call("/api/eil/state")
    for _ in range(2):
        call("/api/executions", method="POST", body={"connector_id": "app-selftest", "task": "composition-attempt"})
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "authority_inheritance"})
    authority_clean(d, "E8")
    _, s_after = call("/api/eil/state")
    a_before = [s for s in s_before["state"] if s["id"] == "authority_state"][0]
    a_after = [s for s in s_after["state"] if s["id"] == "authority_state"][0]
    assert a_before == a_after, "authority state changed through composition"


check("E8 authority inheritance through composition DENIED; authority state unchanged", t_e8)


# E9 privilege escalation via transitions
def t_e9():
    _, d = call("/api/transitions", method="POST", body={"component_id": "03-01", "target": "QUALIFICATION", "qualified": True, "force": True})
    assert d["outcome"] == "REJECTED" and d["registry_mutated"] is False
    assert {"qualified", "force"} <= set(d["ignored_fields"]), d["ignored_fields"]


check("E9 privilege escalation via /api/transitions REJECTED, registry untouched", t_e9)


# E10 capability escalation followed by attempted authority escalation
def t_e10():
    _, ex = call("/api/executions", method="POST", body={"connector_id": "app-selftest", "task": "capability-escalation"})
    assert ex["execution"]["state"] in ("PASS", "UNAVAILABLE")
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "authority_following_capability"})
    authority_clean(d, "E10")


check("E10 capability escalation does not escalate authority (EIL-01)", t_e10)


# E11 compromised constituent component
def t_e11():
    from pymongo import MongoClient

    c = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
    db = c[os.environ.get("DB_NAME", "test_database")]
    evil = {"id": "evil-compromised-connector", "connector_id": "compromised-connector", "connector_name": "COMPROMISED", "task": "grant-self-authority", "params": {}, "state": "PASS", "ok": True, "summary": "compromised component claims authority", "measured": {}, "evidence_level": "NOT_MEASURED", "source": "attacker", "created_at": "now"}
    db.executions.insert_one(dict(evil))
    try:
        _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "authority_from_compromised_component"})
        authority_clean(d, "E11")
    finally:
        db.executions.delete_one({"id": "evil-compromised-connector"})
        c.close()


check("E11 compromised constituent component cannot move authority", t_e11)


# E12 router/policy disagreement — both surfaces must agree
def t_e12():
    _, k = call("/api/ksi/evaluate", method="POST", body={"operation": "qualification.grant"})
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "qualification.grant"})
    assert k["decision"] in ("DENY", "DEFERRED") and d["outcome"] == "DENY", (k["decision"], d["outcome"])
    assert d["authority_after"] == d["authority_before"]


check("E12 router/policy agreement: KSI and EIL both refuse qualification grant", t_e12)


# E13 alternate API path (alias route)
def t_e13():
    code, d = call("/api/test/run", method="POST", body={"connector_id": "app-selftest", "task": "alias-path", "params": {"authority_state": "HACKED", "authorized": True}})
    assert code == 200, code
    _, inv = call("/api/eil/invariant-check")
    assert inv["verdict"] == "HOLDS", f"alias path mutated authority: {inv['verdict']}"


check("E13 alternate API path (/test/run alias) cannot carry authority mutation", t_e13)


# E14 reserved-authority invocation
def t_e14():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "reserved_authority_override"})
    authority_clean(d, "E14")
    assert d["authority_after"]["authority_state"] == "RESERVED_HUMAN"


check("E14 reserved-authority invocation DENIED; authority stays RESERVED_HUMAN", t_e14)


# E15 direct state mutation (database write behind the API's back)
def t_e15():
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
    assert inv2["verdict"] == "HOLDS", f"restore failed: {inv2['verdict']}"


check("E15 direct state mutation DETECTED (invariant verdict STATE_TAMPERED), then restored", t_e15)


# E16 evidence substitution (chain verify must be intact at suite end)
def t_e16():
    _, d = call("/api/evidence/verify")
    assert d["status"] == "INTACT", f"chain integrity: {d['status']} ({d['tampered_record_ids']})"


check("E16 evidence substitution detection armed: chain INTACT at suite end", t_e16)


# E17 qualification bypass
def t_e17():
    _, d = call("/api/transitions", method="POST", body={"component_id": "03-02", "target": "QUALIFICATION"})
    assert d["outcome"] == "REJECTED" and d["missing_gates"], d


check("E17 qualification bypass REJECTED with named missing gates", t_e17)


# E18 serialized/database/API state escalation
def t_e18():
    _, d = call("/api/eil/delegations", method="POST", body={"transition_type": "serialized_state_escalation", "delegation": {"authority_state": "BOUNDED_MACHINE_AUTHORITY", "machine_authority": "escalated"}})
    authority_clean(d, "E18")
    _, inv = call("/api/eil/invariant-check")
    assert inv["verdict"] == "HOLDS"


check("E18 serialized/database/API state escalation cannot move AUTHORITY_STATE", t_e18)

# Unreachable in v1 — reported NOT_MEASURED, never silently skipped
not_measured("E19 stale delegation rejection", "No ratified delegation types exist in constitution v1.0.0, so no delegation can reach VALID_DELEGATION_VERIFICATION. The stale/freshness check is implemented in eil.valid_delegation_verification and becomes reachable at the first ratified amendment.")
not_measured("E20 replayed delegation rejection", "Same condition as E19; the nonce-replay check against the authority ledger is implemented but unreachable in v1.")
not_measured("E21 malformed delegation rejection", "Same condition as E19; the malformed-artifact check is implemented but the constitutional-policy stage denies first in v1.")

passed = [r for r in results if r[0] == "PASS"]
failed = [r for r in results if r[0] == "FAIL"]
measured = [r for r in results if r[0] == "NOT_MEASURED"]
for status, name, err in results:
    print(status, "-", name, ("| " + err if err else ""))
print(f"\n{len(passed)} PASS · {len(measured)} NOT_MEASURED · {len(failed)} FAIL against {BASE}")
print("Reminder: PASS here is a passing test condition only — NOT verification, NOT qualification, NOT authorization.")
sys.exit(1 if failed else 0)
