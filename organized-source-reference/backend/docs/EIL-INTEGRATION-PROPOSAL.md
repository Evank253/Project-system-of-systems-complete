# EIL INTEGRATION PROPOSAL

**Status: PROPOSED — NOT IMPLEMENTED · NOT DEPLOYED · NOT VERIFIED.**
No code, data, registry, or configuration has been changed for EIL yet. This document is the integration shape submitted for review, per instruction. The frozen doctrine (EIL-01 … EIL-05, state-domain separation, EIL-ASSURE-001, forbidden paths, TEVV list, vocabulary) will be stored **verbatim** — no rule invented, no rule inferred, no redesign.

---

## 0. The doctrine artifact (frozen, hash-anchored)

- **Path:** `/app/backend/data/eil/constitution.json`
- **Content:** exactly the doctrine as provided: the five constitutional invariants (EIL-01 … EIL-05), STATE-DOMAIN SEPARATION, the authority trajectory, the authoritative authority-transition path, EIL-ASSURE-001 with the machine-testable invariant, the untrusted-input list, the forbidden authority paths, the TEVV requirements, the evidence vocabulary (PASS ≠ VERIFIED ≠ QUALIFIED ≠ AUTHORIZED; NOT_MEASURED first-class), and the assurance chain.
- **Discipline:** anything the constitution does not define → `[NOT_DEFINED_IN_CONSTITUTION]` (same discipline as existing `[PLACEHOLDER]`s).
- **Tamper-evidence:** `sha256(constitution.json)` is recorded in the chain-anchor collection and surfaced in `/api/manifest` and `/api/inspect`; any modification of the frozen doctrine is detectable. `frozen: true`, `source: "owner-provided frozen doctrine (external architecture work)"`.
- **Human-readable copy:** `/app/backend/docs/EIL-CONSTITUTION.md` (verbatim text), served at `GET /api/docs/eil-constitution`.

## 1. Where it lives in the source tree

```
/app/backend/data/eil/constitution.json     ← the frozen doctrine (authoritative artifact)
/app/backend/eil.py                         ← EIL policy engine: state domains, delegation validation, invariant check
/app/backend/ksi.py                         ← thin adapter (contract unchanged) — delegates privileged evaluation to eil.py
/app/tests/run_eil_adversarial.py           ← doctrine TEVV suite (full attack list from §10 of the doctrine)
/app/backend/docs/EIL-CONSTITUTION.md       ← verbatim doctrine, readable in the app
/app/backend/docs/EIL-INTEGRATION-PROPOSAL.md ← this document (unregistered until approved)
```

## 2. Connection to the existing KSI boundary

`/api/ksi/evaluate` keeps its contract. Internally, privileged operations delegate to `eil.evaluate()`, which decides **from the constitution artifact only**:

| Doctrine rule | Enforcement |
|---|---|
| EIL-03 — NO SELF-ELEVATION | `self_*` operations → **DENY**, reason cites `[eil:EIL-03]` |
| EIL-04 — EVIDENCE DOES NOT AUTHORIZE | verification/qualification issue & grant → **DEFERRED** (evidence-domain outcomes never authorize) |
| EIL-02 — VALID DELEGATION | authority transitions → only via the delegation validator; **v1 constitution defines no permitted delegation types → DENY**, citing `[eil:EIL-02]` + `[NOT_DEFINED_IN_CONSTITUTION]` |
| EIL-05 — RESERVED HUMAN AUTHORITY | reserved-authority invocation → **DENY** (no exception is defined in v1) |

Policy id becomes `EIL_POLICY_V1` with the previous `KSI_LOCAL_POLICY_V0` retained in provenance. Every DENY/DEFERRED response cites the constitutional rule id behind it.

## 3. Where the five states are represented

- New collection **`eil_state`** with exactly five documents: `capability_state`, `evidence_state`, `verification_state`, `qualification_state`, `authority_state`.
- Each domain state derives **only** from its own domain's records (evidence_state ← evidence_records; capability_state ← registry/executions; authority_state ← authority_transitions ONLY).
- **Cross-domain mutation is structurally impossible:** the single writer of `authority_state` in the entire codebase is `eil.authority_transition()`; no other module imports it. Default authority state: `RESERVED_HUMAN / machine_authority: NONE`.
- **Vocabulary separation is schema, not convention:** evidence records carry four distinct fields — `test_result` (PASS/FAIL/NOT_CONFIGURED/…), `verified: false`, `qualified: false`, `authorized: false` — and `authorized` can only become true via a RECORDED authority transition.

## 4. Where constitutional delegation is enforced

`POST /api/eil/delegations` implements the authoritative path **verbatim**:

```
REQUESTED_AUTHORITY_CHANGE → CONSTITUTIONAL_POLICY → VALID_DELEGATION_VERIFICATION → DENY OR AUTHORITY_TRANSITION → AUDIT_RECORD
```

- CONSTITUTIONAL_POLICY: lookup of permitted delegation types in `constitution.json`. v1 → none → DENY.
- VALID_DELEGATION_VERIFICATION (when a type exists): delegation artifact with authorized approver + anti-forgery validation (hash-verified, freshness window → **stale and replayed delegations rejected**).
- Every attempt — allowed or denied — appends to the **`authority_transitions` ledger** (hash-chained) preserving: requester, requested, transition, constitutional_rule, prerequisite_evidence, authorized_approver, anti_forgery_validation, actual_state_mutation, audit_record.
- Machine-testable invariant made executable: `GET /api/eil/invariant-check` runs EIL-ASSURE-001 live — executes every capability-elevating operation available (run test, add evidence, reproduce) and returns `{authority_before, authority_after, valid_constitutional_delegation, verdict}` where verdict is HOLDS iff `authority_after == authority_before`.
- Future delegation types enter **only** as a frozen doctrine amendment (new version, new hash) — never through application logic.

## 5. Where audit records are generated

- Existing `audit_log` (reused) for all events; new **`authority_transitions`** ledger for authority mutations/attempts, hash-chained with `sha256-chain-v1`, anchored like the evidence chain, exposed at `GET /api/eil/authority-ledger` and summarized in `/api/inspect`.

## 6. What is reused, not replaced

- `ksi.py` boundary (evolved, contract stable) · `lifecycle.py` chain + transition ledger (pattern extended to the authority ledger) · evidence_records schema (extended, no migration break) · audit_log · registry pattern (new components: `02-17` EIL policy engine, `05-10` delegation validator, `04-12` EIL state separation, `07-08` EIL adversarial suite) · acceptance suite · AI grounding (constitution added to `/api/ai/ask` context; the assistant may interpret EIL but per EIL-03 can never confer authority; citations gain `[eil:EIL-xx]`).

## 7. Protected enforcement points

- `/api/transitions`, `/api/executions` + the `/api/test/run` alias, `/api/evidence/*`, `/api/ksi/evaluate`, `/api/eil/*`, `/api/executions/{id}/reproduce`.
- Untrusted-flag strip list extended to the doctrine's list: `verified`, `human_approved`, `policy_allows`, `qualified`, `authorize` (+ `force`, `admin`, `bypass`, case-insensitive) — reported as ignored, never read into logic.
- **Alternate-path protection:** the EIL guard is a FastAPI dependency on privileged routers — any future route on those routers inherits it automatically.
- **Direct state mutation:** `eil_state` documents are anchor-hashed; `invariant-check` and `/api/evidence/verify` detect out-of-band writes.

## 8. TEVV surfaces (doctrine §10 — the full attack list, as a new suite)

`/app/tests/run_eil_adversarial.py` covers: forged evidence · forged verification · forged qualification · fabricated human approval · caller-controlled authorization flags · unauthorized delegation · authority inheritance through composition (compose two ALLOWED capability ops → request authority → DENY) · privilege escalation · self-authorization · capability escalation followed by attempted authority escalation · compromised constituent component · router/policy disagreement (alias vs canonical route must decide identically) · alternate API/code paths · direct state mutation (DB write to authority_state → detected) · reserved-authority invocation · stale delegation · replayed delegation · malformed delegation · evidence substitution · qualification bypass · serialized/database/API state escalation.

Acceptance additions: vocabulary separation, EIL-ASSURE-001 invariant check, constitution-hash integrity, rule-citation presence in DENY reasons.

**Reporting contract after implementation:** every result in the doctrine's vocabulary — IMPLEMENTED / PASS / FAIL / NOT_MEASURED / VERIFIED / QUALIFIED / AUTHORIZED — with each status tied to actual test/evidence. Honest defaults: everything remains NOT_VERIFIED / NOT_QUALIFIED / NOT_AUTHORIZED until external TEVV exists; a PASS never becomes AUTHORIZED.

## Execution sequence after your approval

1. constitution.json + EIL-CONSTITUTION.md (verbatim, hashed, anchored)
2. eil.py: state domains, delegation validator, invariant-check, authority ledger
3. ksi.py adapter rewiring (rule-cited decisions)
4. Protected routes + extended flag stripping
5. Registry components + docs registration
6. Acceptance suite + adversarial suite + EIL adversarial suite + GPT-6 assisted review
7. Evidence-backed report in the doctrine's vocabulary
