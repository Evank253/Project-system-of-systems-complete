# AUTHORITY-MODEL

## Prime principle

**Authority belongs to humans.** A system's ability to perform an action is *capability*, never *authority*. The public application must not imply that an AI system holds authority merely because it can act.

## Levels

| Level | Definition |
|---|---|
| H0 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| H1 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| H2 | `[AUTHORITATIVE_DEFINITION_PENDING]` |
| H3 | `[AUTHORITATIVE_DEFINITION_PENDING]` — highest human sign-off |

H0–H3 semantics come from the authoritative governance documentation (KSI) when supplied. Nothing here redefines them.

## Lifecycle

| Operation | State | Note |
|---|---|---|
| Delegation | `INTEGRATION_REQUIRED` | Interface only. No delegation records exist. |
| Authorization | `INTEGRATION_REQUIRED` | Interface only. No privileged operations exist in this build. |
| Revocation | `INTEGRATION_REQUIRED` | Interface only. |
| Audit trail | `IMPLEMENTED` (basic) | Every execution attempt is logged and exposed at `GET /api/authority`. No tamper-evidence yet. |

## Enforcement boundary

Enforcement is provided by **KSI and human operators**, not by this public layer. The public layer can display authority state; it can never grant it.

## Design consequences in this build

- No component, connector, or AI system is displayed as holding authority.
- The Live Test page reports what a system *did*, never what it was *allowed to decide*.
- The authority registry (`data/authority.json`) is data: authoritative definitions replace placeholders without code changes.
