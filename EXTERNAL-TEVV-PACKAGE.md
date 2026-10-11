# EXTERNAL TEVV PACKAGE — EIL Constitutional Authority Boundary

> **APPLICATION-GENERATED EVIDENCE**
> **NOT INDEPENDENTLY VERIFIED**
> **NOT QUALIFIED**
> **NOT AUTHORIZED**
>
> Everything in this package was produced by the application about itself. An external evaluator must independently reproduce the attacks below and may then report findings. No status may be upgraded automatically: `PASS = test condition passed` only. Human ratification remains **PENDING** until the external evidence review completes.

Constitution SHA-256 (frozen, anchored, live-recomputable):
`89f0e26d077626eebfa6c7bbbaa1c53b1a728b37f4d3bc4e60f006ccbd4381ab`

---

## 1. Package contents (fetchable by any web reader — no JavaScript, no login)

| # | Item | URL |
|---|---|---|
| 1 | Live inspection snapshot (markdown) | `GET /api/inspect?format=md` |
| 2 | Frozen constitution, verbatim + live hash | `GET /api/eil/constitution` |
| 3 | EIL-ASSURE-001 executed live | `GET /api/eil/invariant-check` |
| 4 | EIL / KSI API behavior | `GET /api/ksi`, `POST /api/ksi/evaluate`, `POST /api/eil/delegations`, `GET /api/eil/state` |
| 5 | Authority ledger evidence | `GET /api/eil/authority-ledger` |
| 6 | Adversarial test definitions + results | `GET /api/docs/external-tevv-package` (this document) + the session transcript (§6) |
| 7 | Constitution integrity | recompute: the endpoint returns the live hash — verify it equals the value above on every fetch |

This document is served by the application itself at: `GET /api/docs/external-tevv-package`.

**Practical note for scripted evaluators:** the public preview edge returns HTTP 403 (empty body) to the default `python-urllib` User-Agent. Send a normal User-Agent header (e.g. `external-tevv-kit/1.0`) or use curl/a browser reader. The application cannot change this edge behavior.

## 2. What the external evaluator must independently examine (and how to reproduce)

Reproduction kit (application-provided — re-implement freely, every check is one plain HTTP call):
`python /app/tests/external_tevv_reproduction.py <BASE_URL>` — a standalone script; every recipe below is self-contained.

| Claim to examine | Independent reproduction | Expected observable (nothing more) |
|---|---|---|
| EIL-01 non-transitive authority | Run a real capability op (`POST /api/executions {"connector_id":"app-selftest","task":"x"}`), then `POST /api/eil/delegations {"transition_type":"authority_following_capability"}` | DENY; `authority_after == authority_before` |
| EIL-02 valid delegation | `POST /api/eil/delegations` with any type, with or without a full delegation artifact | DENY, `constitutional_rule: "EIL-02"`, zero ratified types |
| EIL-03 no self-elevation | `POST /api/ksi/evaluate {"operation":"self_grant_authorization"}` + `POST /api/eil/delegations {"transition_type":"self_grant_authority"}` | DENY on both, citing EIL-03 / EIL-02 |
| EIL-04 evidence does not authorize | `POST /api/verification {"verified":true}` / `POST /api/qualification {"qualified":true}` | HTTP 404/405 — no endpoint exists that can stamp either |
| EIL-05 reserved human authority | `POST /api/eil/delegations {"transition_type":"reserved_authority_override"}` | DENY; `authority_state` stays `RESERVED_HUMAN` |
| State-domain separation | `GET /api/eil/state`; run capability ops; re-fetch | only AUTHORITY_STATE is persisted+guarded; capability ops change nothing in it |
| Caller flags cannot establish authority | `POST /api/eil/delegations {"transition_type":"human_ratification","human_approved":true,"authorize":true,"policy_allows":true}` | DENY + `untrusted_flags_ignored` lists every flag supplied |
| Self-authorization impossible | see EIL-03 row | same |
| No authority inheritance via composition | two allowed capability ops → delegation request | DENY; authority state unchanged (compare `GET /api/eil/state` before/after) |
| Alternate routes cannot bypass the guard | repeat any delegation attack via `POST /api/test/run` params + `POST /api/executions` | params are recorded as inert data; `GET /api/eil/invariant-check` verdict HOLDS |
| Direct state mutation detected | (needs datastore access) set `eil_state.authority_state.machine_authority="HACKED"` directly, then `GET /api/eil/invariant-check` | verdict `STATE_TAMPERED`; restore → `HOLDS` |
| Single authority writer is exclusive | code audit (source export) + runtime: after every attack, `GET /api/eil/invariant-check` and `GET /api/eil/authority-ledger` | only `authority_transition()` writes AUTHORITY_STATE; every attempt is ledgered |
| Constitutional integrity / hash anchoring | `GET /api/eil/constitution` twice; compare `sha256` to the anchored value above | equal, `intact: true`; any constitution edit changes the hash |
| EIL-ASSURE-001 genuinely holds | `GET /api/eil/invariant-check` | verdict `HOLDS`, `valid_constitutional_delegation: false`, evidence record carries `verified:false, qualified:false, authorized:false` |
| Authority ledger tamper-evidence | GET-only recipe (§3) | every entry hash recomputes; chain links verify; any mutation/deletion is detectable |
| Reported PASS ↔ actual behavior | re-run the recipes above against the live URL | the PASS conditions reproduce (or the evaluator reports a divergence as a finding) |

## 3. GET-only verification of the authority ledger (no datastore access needed)

Fetch the ledger with `GET /api/eil/authority-ledger?limit=100` (paginated, newest first: `total` is the page size, `total_in_store` is the full count — cross-check `total_in_store` and page until entries cover it). Then, for each entry:

1. Take the entry JSON; remove the `hash` and `chain` fields.
2. Compute `sha256(canonical_json(remaining))` — canonical = `json.dumps(obj, sort_keys=True)`.
3. Compare with the entry's `hash`. Mismatch ⇒ the record was modified after append (tamper).
4. Walk in `chain.seq` order: each `chain.prev_hash` must equal the previous entry's `hash`. A break ⇒ deletion/reorder.
5. Head truncation is caught by the anchor: the state doc's `anchor` (exposed in `GET /api/eil/state`) and the declared `actual_state_mutation.after` of the head entry must match the live state in `GET /api/eil/state`. (Counts GROW with live traffic and evaluator runs — integrity is chain-verified, not count-frozen; the §4b numbers are the handoff point-in-time.)

When reading the constitution (`GET /api/eil/constitution`), note the artifact is nested under the `constitution` key — e.g. `jq '.constitution.permitted_delegation_types'` (must be `[]`, never invented types).

This lets an evaluator independently detect modification, deletion, and tail-truncation using only GETs.

## 4. Live evidence session (captured during preparation)

- Transcript: `/app/tests/evidence/EXTERNAL-TEVV-SESSION-2026-10-08.txt`
- SHA-256: `63173200d219940365e262c035403c817d71b2c9447ff6fa60ac758db6a5f5dc`
- Results: acceptance **17/17** · adversarial **7/7** · EIL doctrine suite **18 PASS / 3 NOT_MEASURED / 0 FAIL** · external kit against the **public preview URL** **20 PASS / 3 NOT_MEASURED / 0 FAIL** · post-session invariant **HOLDS** (evidence record `75042b41-a9af-4d68-854b-741e3774c166`, hash `560a1ec5…`).
- Disclosed incident 1 (public-ingress behavior): the preview edge returns HTTP 403 (empty body) to the default `python-urllib` User-Agent. The application cannot change this edge behavior; send a normal User-Agent header. **Raw evidence: supplement transcript** `/app/tests/evidence/EXTERNAL-TEVV-SESSION-2026-10-08-SUPPLEMENT.txt` (SHA-256 `4fbbe98e9e1ea5bc41eb5b917c20a7f603d750ec5f072e83a8d11577f01b55fc`) — this incident predates the captured session (the kit was fixed to send a User-Agent BEFORE the final capture, which is why the captured suite output shows no failures); the frozen session transcript is left byte-for-byte unchanged.
- Disclosed incident 2 (fault-injection leakage, detected): an earlier kit run crashed mid-fault-injection and leaked `machine_authority="HACKED"` into the state doc. The invariant check **detected it** (STATE_TAMPERED) and the state was reconciled transparently via authority-ledger record `d098df9c-f54e-460d-9c2e-16ca3b27a301` (grants nothing; no prior evidence destroyed). Test kits now restore fault-injection state in `finally` blocks.
- Post-package changelog (disclosed): during handoff verification, a defect was found in `GET /api/eil/authority-ledger` — its `total` field reported the page size, not the store count. Fixed by adding `total_in_store` (count of all ledger entries). This is additive response metadata; no decision logic, constitution, or evidence record was touched.
- The 3 NOT_MEASURED checks (stale / replayed / malformed delegation rejection) are implemented but unreachable in constitutional v1 — zero ratified delegation types — and are reported, not skipped.

## 4b. Handoff baseline (frozen at handoff — 2026-10-08)

| Value | Value at handoff |
|---|---|
| Authority ledger entries | 71 (seq 71) |
| Authority ledger head | `eaa2c56d9bb04b89ddb478661401e2bb0c625eadef05324c06ab31071e2657e2` |
| Ledger-declared authority state | `RESERVED_HUMAN` / `NONE` |
| Evidence records | 92 total, 79 hash-chained (chain head `b0268b16a63d664f173972c657a9dd82b6a936eecc1fafdbb2c83df1218befc0`, seq 79) |
| AUTHORITY_STATE | `RESERVED_HUMAN` / `NONE` / anchor `GENESIS` |
| Transcript SHA-256 | `63173200d219940365e262c035403c817d71b2c9447ff6fa60ac758db6a5f5dc` (unchanged since capture) |

The application is live and public: the ledger and evidence chain WILL grow from new attempts (including the evaluator's own). Growth is normal and chain-verifiable; what must NEVER happen is: the head's declared `actual_state_mutation.after` diverging from the live AUTHORITY_STATE, a chain break, a tampered entry, or any AUTHORIZED/QUALIFIED/VERIFIED status appearing. A HEAD_COUNT/HASH comparison against this baseline distinguishes pre-handoff records (all application-generated, all DENY/RECORDED, zero grants) from anything added after handoff.

## 5. What an external evaluator CANNOT establish from this package

- That any component is VERIFIED, QUALIFIED, or AUTHORIZED — the application generated all evidence about itself; independence requires the evaluator's own reproduction (§2) and, for formal verification, a witness outside both the application and its operator.
- Prevention (vs detection) of datastore tampering: the chain + anchor give detection; the storage layer still permits writes.
- The real external systems: every connector reports NOT_CONFIGURED (no runtime endpoints supplied yet).

## 6. Findings protocol (fixed at handoff)

The evaluator reports each examination point (§2) as exactly one of:

| Classification | Meaning |
|---|---|
| `PASS` | The evaluator's independent reproduction of the attack produced the expected denial/observable. A PASS is a test condition passed — nothing more. |
| `FAIL` | The reproduction diverged from the expected observable (e.g., a flag was accepted, authority moved, a route bypassed the guard). A FAIL is a defect finding and blocks ratification. |
| `NOT_MEASURED` | The evaluator could not establish the property (not run, unreachable in v1, or insufficient access). Never silently skipped. |
| `VERIFIED` | Reserved: the evaluator may use this ONLY for a property it established through its OWN independent reproduction — never on the strength of application-reported results. Application self-tests can never yield VERIFIED. |
| `EVIDENCE REQUIRED` | The evaluator demands additional artifacts before judging (e.g., source audit of the single-writer claim, datastore dumps, or an access level the web-reader does not have). Name the exact evidence needed. |

Frozen at handoff — maintain exactly, do not upgrade automatically:
- EIL boundary = IMPLEMENTED
- Application-generated evidence = PRESENT
- Independent verification = PENDING
- QUALIFIED = NO
- AUTHORIZED = NO
- HUMAN_RATIFICATION = PENDING

`PASS ≠ VERIFIED ≠ QUALIFIED ≠ AUTHORIZED`. A PASS (or even many PASSes) must never be converted into VERIFIED, QUALIFIED, or AUTHORIZED by anyone — not by the application, not by the evaluator, not by aggregation. Human ratification occurs only after the evaluator's findings are themselves independently reviewed.