# LIFECYCLE-ENFORCEMENT

The canonical sequence, enforced in application code. A component moves through gates in order or not at all.

```
IMPLEMENTATION → EXECUTION → EVIDENCE → REPRODUCTION → VERIFICATION → QUALIFICATION → HUMAN_RATIFICATION
```

## The authorization boundary (KSI)

Every lifecycle decision routes through `POST /api/ksi/evaluate` — a local stand-in policy engine (`KSI_LOCAL_POLICY_V0`) that is **structurally incapable of manufacturing authorization**:

| Decision | When |
|---|---|
| `ALLOW` | Non-privileged operations only (reads, controlled tests, integrity checks) |
| `DENY` | Self-authorization attempts (`self_verify`, `self_grant_authorization`, …) and unknown operations (default-deny) |
| `DEFERRED` | Privileged operations (verification, qualification, ratification, evidence promotion) — require the connected KSI runtime |

Caller-supplied flags — `human_approved=true`, `verified`, `qualified`, `force`, `bypass`, … — are **structurally ignored**: they are never read into any decision, and attempts to use them are rejected and listed in the response.

## Transitions (`POST /api/transitions`)

- Enforces gate order: a transition to any stage is REJECTED with the named missing prior gates.
- Privileged targets stay `DEFERRED` until the real KSI runtime (and for VERIFICATION+, an independent witness) exists.
- Every attempt is appended to the **transitions ledger** (`GET /api/transitions`) and the audit log.
- **The application never mutates registry statuses.** RECORDED transitions are provenance for the authoritative owner, who updates the registry data.

## Evidence integrity (`GET /api/evidence/verify`)

Every evidence record is hash-chained (`sha256-chain-v1`): each record's SHA-256 covers its full content (excluding the hash and the previous-hash pointer), and each record points to the previous record's hash. The verify endpoint walks the chain and detects:

- **TAMPER_DETECTED** — any modification of an existing record's content,
- **CHAIN_BROKEN** — deletion or reordering of records.

Demonstrated adversarially in `/app/tests/run_adversarial.py` (A5, A6): mutate a record → detected; delete a record → detected; restore → INTACT. This is tamper **detection** by the app itself — still self-verification, so prevention/cryptographic immutability and independent verification remain open gates.

## Reproduction (`POST /api/executions/{id}/reproduce`)

Re-runs a recorded execution against the same connector/task/params, records a new execution + chained evidence record with `provenance.reproduces`, and returns a factual comparison (`states_match`). A matching state is evidence of reproduction — it is **not** a verification stamp and does not upgrade any evidence level.

## Adversarial suite

`python /app/tests/run_adversarial.py <BASE_URL>` — A1 flags ignored · A2 no gate skipping · A3 no evidence-promotion endpoint exists · A4 KSI denies self-authorization · A5 tamper detected · A6 deletion detected · A7 nothing displays VERIFIED/QUALIFIED.
