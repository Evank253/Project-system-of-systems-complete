"""KETCHUM adversarial test suite.

Attacks the enforcement mechanisms the way an abusive caller would:
  A1 caller-supplied approval flags (human_approved=true) are ignored
  A2 lifecycle gates cannot be skipped
  A3 no endpoint exists that sets/promotes evidence levels
  A4 KSI cannot be tricked into self-authorization
  A5 modification of an existing evidence record is DETECTED (tamper check)
  A6 deletion of an existing evidence record is DETECTED (chain break)
  A7 no component is ever displayed as VERIFIED/QUALIFIED

Run: python /app/tests/run_adversarial.py [BASE_URL]   (default http://localhost:8001)"""
import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
results = []


def call(path, method="GET", body=None, ok_codes=(200,)):
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
        results.append((name, True, ""))
    except AssertionError as e:
        results.append((name, False, str(e)))
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))


def t_a1():
    _, d = call("/api/transitions", method="POST", body={"component_id": "03-01", "target": "QUALIFICATION", "human_approved": True, "verified": "true", "force": True})
    assert d["outcome"] == "REJECTED", f"outcome {d['outcome']} — flags leaked?"
    assert set(d.get("ignored_fields", [])) >= {"human_approved", "verified", "force"}, f"ignored_fields={d.get('ignored_fields')}"
    assert d["registry_mutated"] is False


check("A1 human_approved=true does NOT grant QUALIFICATION (flags ignored, rejected)", t_a1)


def t_a2():
    _, d = call("/api/transitions", method="POST", body={"component_id": "03-01", "target": "VERIFICATION"})
    assert d["outcome"] == "REJECTED", f"outcome {d['outcome']}"
    assert "EXECUTION" in d["missing_gates"] or "EVIDENCE" in d["missing_gates"] or "REPRODUCTION" in d["missing_gates"], d["missing_gates"]


check("A2 skipping lifecycle gates is REJECTED with named missing gates", t_a2)


def t_a3():
    code, _ = call("/api/evidence/promote", method="POST", body={"component_id": "03-01", "level": "E5"})
    assert code in (404, 405), f"evidence promotion endpoint exists?! HTTP {code}"
    code2, _ = call("/api/evidence/level", method="POST", body={"level": "E2"})
    assert code2 in (404, 405), f"evidence level setter exists?! HTTP {code2}"


check("A3 no endpoint exists that promotes evidence levels", t_a3)


def t_a4():
    for op in ("self_grant_authorization", "self_qualify", "self_ratify"):
        _, d = call("/api/ksi/evaluate", method="POST", body={"operation": op})
        assert d["decision"] == "DENY", f"{op} → {d['decision']}"
    _, d2 = call("/api/ksi/evaluate", method="POST", body={"operation": "qualification.grant"})
    assert d2["decision"] == "DEFERRED", d2


check("A4 KSI denies self-authorization, defers privileged grants", t_a4)


def t_a5():
    from pymongo import MongoClient
    import os

    c = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
    db = c[os.environ.get("DB_NAME", "test_database")]
    rec = db.evidence_records.find_one({"hash": {"$exists": True}, "chain.seq": {"$exists": True}})
    assert rec, "no chained evidence records exist yet — run a live test first"
    original_claim = rec["claim"]
    db.evidence_records.update_one({"id": rec["id"]}, {"$set": {"claim": "TAMPERED CLAIM — do not trust"}})
    _, d = call("/api/evidence/verify")
    assert d["status"] == "TAMPER_DETECTED", f"tamper NOT detected: {d['status']}"
    assert rec["id"] in d["tampered_record_ids"]
    db.evidence_records.update_one({"id": rec["id"]}, {"$set": {"claim": original_claim}})
    _, d2 = call("/api/evidence/verify")
    assert d2["status"] == "INTACT", f"restore failed: {d2['status']}"
    c.close()


check("A5 modifying an existing evidence record is DETECTED (then restored)", t_a5)


def t_a6():
    from pymongo import MongoClient
    import os

    c = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
    db = c[os.environ.get("DB_NAME", "test_database")]
    rec = db.evidence_records.find_one({"chain.seq": {"$exists": True}})
    assert rec, "no chained evidence records exist yet"
    db.evidence_records.delete_one({"id": rec["id"]})
    _, d = call("/api/evidence/verify")
    assert d["status"] == "CHAIN_BROKEN", f"deletion NOT detected: {d['status']}"
    db.evidence_records.insert_one(rec)
    _, d2 = call("/api/evidence/verify")
    assert d2["status"] == "INTACT", f"reinsert failed: {d2['status']}"
    c.close()


check("A6 deleting an existing evidence record is DETECTED (then restored)", t_a6)


def t_a7():
    _, d = call("/api/components")
    for comp in d["components"]:
        assert comp["verification"] != "VERIFIED" and comp["qualification"] != "QUALIFIED", comp["id"]


check("A7 no component displays VERIFIED/QUALIFIED anywhere in the registry", t_a7)

passed = [r for r in results if r[1]]
for name, ok, err in results:
    print(("PASS" if ok else "FAIL"), "-", name, ("| " + err if err else ""))
print(f"\n{len(passed)}/{len(results)} adversarial checks passed against {BASE}")
sys.exit(0 if len(passed) == len(results) else 1)
