"""KETCHUM SOS acceptance checks. Run: python /app/tests/run_acceptance.py [BASE_URL]
Default BASE_URL: http://localhost:8001 (use the public preview URL for e2e).

These checks assert the no-fabrication invariants of the package:
nothing may claim VERIFIED / QUALIFIED without evidence, and every unconfigured
connector must return NOT_CONFIGURED — never a simulated success."""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
results = []


def call(path, method="GET", body=None):
    req = urllib.request.Request(BASE + path, method=method)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data) as r:
        return json.loads(r.read().decode())


def check(name, fn):
    try:
        fn()
        results.append((name, True, ""))
    except AssertionError as e:
        results.append((name, False, str(e)))
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))


check("health responds ok", lambda: (lambda d: [_ for _ in [d] if d["status"] == "ok"][0] if call("/api/health")["status"] == "ok" else (_ for _ in ()).throw(AssertionError("status != ok")))(call("/api/health")))


def t_system():
    d = call("/api/system")
    assert len(d["sections"]) == 8, f"expected 8 sections, got {len(d['sections'])}"
    assert d["total_components"] > 50, "registry suspiciously small"


check("system registry exposes 8 sections", t_system)


def t_no_verified():
    d = call("/api/components")
    for c in d["components"]:
        assert c["verification"] != "VERIFIED", f"{c['id']} claims VERIFIED"
        assert c["qualification"] != "QUALIFIED", f"{c['id']} claims QUALIFIED"


check("no component claims VERIFIED/QUALIFIED", t_no_verified)


def t_kcn_not_configured():
    body = {"connector_id": "kcn", "task": "ping"}
    req = urllib.request.Request(BASE + "/api/executions", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())
    assert d["execution"]["state"] == "NOT_CONFIGURED", f"kcn state {d['execution']['state']} — fabrication?"
    assert d["execution"]["evidence_level"] == "NOT_MEASURED"


check("unconfigured KCN returns NOT_CONFIGURED (no fake success)", t_kcn_not_configured)


def t_selftest_real():
    d = call("/api/executions", method="POST", body={"connector_id": "app-selftest", "task": "datastore-ping"})
    ex = d["execution"]
    assert ex["state"] in ("PASS", "UNAVAILABLE"), ex["state"]
    assert isinstance(ex["measured"], dict) and ex["measured"], "selftest returned no measurements"
    assert len(d["evidence_record"]["hash"]) == 64, "evidence hash missing"


check("self-test returns a measured result + hashed evidence record", t_selftest_real)


def t_evidence_rules():
    d = call("/api/evidence")
    assert any("NOT_MEASURED must never be promoted to PASS" in r for r in d["rules"]), "upgrade rules missing"


check("evidence no-upgrade rules present", t_evidence_rules)


def t_verification_honest():
    d = call("/api/verification")
    assert d["status"] == "NOT_MEASURED" and d["verified_component_count"] == 0


check("verification endpoint reports nothing verified", t_verification_honest)


def t_authority():
    d = call("/api/authority")
    assert "AUTHORITY belongs to humans" in d["invariant"]


check("authority invariant present", t_authority)


def t_docs():
    d = call("/api/docs")
    assert len(d["docs"]) >= 10
    c = call("/api/docs/api-specification")
    assert len(c["content"]) > 200


check("documentation index + content served", t_docs)


def t_executions_listed():
    d = call("/api/executions?limit=5")
    assert "executions" in d


check("execution history persisted", t_executions_listed)


def t_ai_models():
    d = call("/api/ai/models")
    slugs = {m["slug"] for m in d["models"]}
    assert {"sol", "luna"} <= slugs, f"model slugs missing: {d['models']}"


check("AI models endpoint lists sol + luna with server-configured ids", t_ai_models)


def t_ai_ask_grounded():
    body = {"question": "According to the component registry, what is the status of component 08-03 (Production)? Answer in one short sentence and cite the registry id.", "model": "luna"}
    req = urllib.request.Request(BASE + "/api/ai/ask", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read().decode()
    assert '"done"' in raw, "SSE stream did not finish with a done event"
    assert "BLOCKED" in raw.upper(), f"assistant answer not grounded in registry (expected BLOCKED for 08-03); got: {raw[:400]}"


check("Ask-the-System answer is grounded (08-03 reported BLOCKED, not fabricated)", t_ai_ask_grounded)


def t_ai_explain():
    body = {"model": "sol"}
    req = urllib.request.Request(BASE + "/api/ai/explain/03-01", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read().decode()
    assert '"done"' in raw, "SSE stream did not finish with a done event"
    assert '"component_id": "03-01"' in raw or '"component_id":"03-01"' in raw, f"done event missing grounding metadata: {raw[-300:]}"


check("Component Explain streams a grounded answer for KCN", t_ai_explain)


def t_ai_health():
    d = call("/api/ai/health")
    assert d["status"] in ("CONFIGURED", "OPERATIONAL", "NOT_CONFIGURED"), d["status"]
    assert d["rate_limit_per_min"] >= 1 and d["stream_timeout_s"] >= 30


check("AI health endpoint reports configured state + limits", t_ai_health)


def t_eil_constitution():
    d = call("/api/eil/constitution")
    assert d["frozen"] is True and len(d["sha256"]) == 64 and d["intact"], "constitution hash mismatch — modified?"
    inv = {i["id"] for i in d["constitution"]["constitutional_invariants"]}
    assert {"EIL-01", "EIL-02", "EIL-03", "EIL-04", "EIL-05"} <= inv, inv
    assert d["constitution"]["permitted_delegation_types"] == [], "delegation types invented?"


check("EIL constitution frozen, hash-intact, five invariants, zero invented delegation types", t_eil_constitution)


def t_eil_invariant():
    d = call("/api/eil/invariant-check")
    assert d["verdict"] == "HOLDS", f"EIL-ASSURE-001 verdict: {d['verdict']}"
    assert d["authority_before"] == d["authority_after"]
    assert d["evidence_record"]["verified"] is False and d["evidence_record"]["authorized"] is False


check("EIL-ASSURE-001 executable invariant HOLDS (capability ops, authority unchanged)", t_eil_invariant)


def t_eil_vocabulary():
    d = call("/api/evidence?limit=1")
    rec = d["records"][0]
    assert rec["verified"] is False and rec["qualified"] is False and rec["authorized"] is False, "vocabulary separation broken"


check("Evidence vocabulary separation in schema: PASS ≠ VERIFIED ≠ QUALIFIED ≠ AUTHORIZED", t_eil_vocabulary)


passed = [r for r in results if r[1]]
for name, ok, err in results:
    print(("PASS" if ok else "FAIL"), "-", name, ("| " + err if err else ""))
print(f"\n{len(passed)}/{len(results)} acceptance checks passed against {BASE}")
sys.exit(0 if len(passed) == len(results) else 1)
