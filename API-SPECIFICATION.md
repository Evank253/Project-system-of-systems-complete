# API-SPECIFICATION

Base URL: `{REACT_APP_BACKEND_URL}/api` — all routes behind the `/api` prefix. Content type: `application/json`.

## Registry & system state

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/system` | 8 sections, all components, status counts, invariant |
| GET | `/api/capabilities` | Capability registry (capability ≠ evidence) |
| GET | `/api/components` | Filter: `?section=&status=&evidence=&verification=&deployment=&q=` |
| GET | `/api/components/{id}` | Full component detail incl. `[PLACEHOLDER]` fields |
| GET | `/api/health` | Liveness + **measured** datastore ping latency |
| GET | `/api/manifest` | Release manifest: version, channel, registry SHA-256, counts |

## Live execution

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/tasks` | Connector catalog: configured state, endpoint env, suggested tasks |
| POST | `/api/executions` | Create execution. Body: `{"connector_id": "...", "task": "...", "params": {}}`. Alias: `POST /api/test/run` |
| GET | `/api/executions?limit=` | Recent executions (real records only) |
| GET | `/api/executions/{id}` | Single execution |

**Execution result states** (exhaustive): `PASS` · `FAIL` · `UNAVAILABLE` · `NOT_CONFIGURED` · `BLOCKED`.
A `PASS` is only ever returned when a real configured runtime answered `{"ok": true}` — or, for `app-selftest`, when the datastore round-trip actually succeeded. There is no simulation path.

**Rate limit:** per-IP sliding window, default 30/min on execution creation → HTTP 429.

## Evidence, verification, qualification, authority

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/evidence?limit=` | E0–E5 slots + NOT_MEASURED, no-upgrade rules, hashed records |
| GET | `/api/verification` | Always honest: `verified_component_count` is 0 until an external witness verifies |
| GET | `/api/qualification` | Always honest: `qualified_component_count` is 0 until TEVV gates pass |
| GET | `/api/authority?limit=` | Authority principles, H0–H3 slots, lifecycle, audit trail |

## Documentation

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/docs` | Index of spec documents (slug, title, status) |
| GET | `/api/docs/{slug}` | Markdown content of one document |

## Governance & integrity enforcement

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/ksi/evaluate` | KSI authorization boundary (local stand-in `KSI_LOCAL_POLICY_V0`): ALLOW (non-privileged) / DENY (self-authorization, unknown) / DEFERRED (privileged, needs connected KSI runtime). Caller-supplied approval flags structurally ignored |
| GET | `/api/ksi` | Boundary invariants, operation allowlists, ignored-flag list |
| POST | `/api/transitions` | Lifecycle transition attempt — enforces EXECUTION → EVIDENCE → REPRODUCTION → VERIFICATION → QUALIFICATION → HUMAN_RATIFICATION; rejects skipped gates and privileged flags; appends to the ledger; never mutates registry statuses |
| GET | `/api/transitions?component_id=` | Append-only transition ledger |
| GET | `/api/evidence/verify` | Hash-chain integrity walk: INTACT / TAMPER_DETECTED / CHAIN_BROKEN (mutating or deleting a stored record is detected) |
| POST | `/api/executions/{id}/reproduce` | Reproduction run against the same connector/task/params; chained evidence record with `provenance.reproduces`; factual `states_match` comparison — never an evidence upgrade |
| GET | `/api/inspect` (`?format=md`) | Single live snapshot for external inspection — statuses, connectors, chain integrity, ledger, AI runtime — as JSON or web-reader markdown |

## EIL — constitutional authority layer

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/eil/constitution` | The frozen EIL doctrine, verbatim, with live-recomputed SHA-256 (modification is detectable) |
| GET | `/api/eil/state` | The five state domains; AUTHORITY_STATE persisted, guarded, single-writer |
| POST | `/api/eil/delegations` | The constitutional authority path: REQUESTED_AUTHORITY_CHANGE → CONSTITUTIONAL_POLICY → VALID_DELEGATION_VERIFICATION → DENY OR AUTHORITY_TRANSITION → AUDIT_RECORD. v1: zero ratified delegation types → every transition DENYs |
| GET | `/api/eil/authority-ledger` | Hash-chained ledger of every authority mutation attempt (all doctrine-required fields) |
| GET | `/api/eil/invariant-check` | EIL-ASSURE-001 executed live: capability transitions run, then authority_before == authority_after is asserted |

Untrusted inputs (`verified`, `human_approved`, `policy_allows`, `qualified`, `authorize`) are stripped and reported wherever supplied.

## AI interface (reasoning layer — never the source of truth)

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/ai/models` | Configured models; identifiers set server-side via `AI_MODEL_SOL` / `AI_MODEL_LUNA` |
| POST | `/api/ai/ask` | "Ask the System": grounded over registry + evidence rules + docs + recent executions. Body: `{"question", "model": "sol"\|"luna", "session_id?"}`. Streams SSE: `start` → `delta`… → `done` (with grounding) or honest `error` |
| POST | `/api/ai/explain/{component_id}` | Per-component explain, same SSE contract, grounded in that component's full record |

Hard rules: the AI never issues verification, qualification, or authority; answers must cite `[registry:ID]` / `[doc:slug]`; unknown facts are reported as unavailable or NOT_MEASURED; per-IP limit default 10/min (`AI_RATE_LIMIT_PER_MIN`); HTTP 503 with factual detail if the runtime key is missing. Audit entries contain metadata only, never content.

## Status vocabulary (machine contract)

`IMPLEMENTED` `INTEGRATION_REQUIRED` `TEST_REQUIRED` `VERIFICATION_REQUIRED` `QUALIFICATION_REQUIRED` `NOT_MEASURED` `BLOCKED`

Deployment states: `DEVELOPMENT` `STAGING` `PRODUCTION` `NOT_DEPLOYED`.

Evidence levels: `E0`–`E5` (definitions `[AUTHORITATIVE_DEFINITION_PENDING]`) and `NOT_MEASURED` (first-class). No record asserts a level today.
