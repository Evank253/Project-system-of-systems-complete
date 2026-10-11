# EVIDENCE-MODEL

## The ladder

| Level | State in this package |
|---|---|
| E5 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| E4 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| E3 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| E2 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| E1 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| E0 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| **NOT_MEASURED** | **Implemented as a first-class status** — displayed honestly everywhere, never rendered as PASS |

The E0–E5 semantics will be used **exactly as defined by the authoritative project documentation** once supplied. This package asserts no interpretation and invents none.

## Upgrade rules (hard rules, also enforced in the acceptance tests)

1. `NOT_MEASURED` must never be promoted to `PASS`.
2. No level upgrades without a recorded measurement + provenance.
3. `E0 → E2`, `E2 → E3`, `E3 → E4`, `E4 → E5`: forbidden without real supporting evidence.
4. No evidence level implies `QUALIFIED`.
5. Historical ≠ current: historical results are labeled historical; only current reproducible results may be labeled current. They are never mixed.

## What an evidence record looks like here

Every live test writes one record: claim (factual summary), level `NOT_MEASURED`, `provisional_level: null`, SHA-256 hash of the execution payload, provenance (source + timestamp), execution link. Inspect them at **/evidence** or `GET /api/evidence`.

## Honesty guarantees in code

- `POST /api/executions` has no code path returning `PASS` without a real configured runtime answering `ok: true` (or a real measured self-test).
- `/api/verification` and `/api/qualification` derive from the registry: zero verified, zero qualified — because no independent witness or TEVV gate has ever produced contrary evidence.
