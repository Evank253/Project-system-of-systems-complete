# DATA-MODEL

## Component registry (`data/registry.json`)

Authoritative seed for `/api/components`. Each component:

```json
{
  "id": "03-01",
  "section": "03",
  "name": "KCN",
  "purpose": "Connector interface to KCN (Ketchum Cognitive Network) runtime.",
  "status": "INTEGRATION_REQUIRED",
  "deployment": "NOT_DEPLOYED",
  "evidence_level": "NOT_MEASURED",
  "verification": "NOT_VERIFIED",
  "qualification": "NOT_QUALIFIED",
  "dependencies": ["KCN_RUNTIME_ENDPOINT"],
  "capabilities": ["forward a task to the configured KCN endpoint"],
  "limitations": ["No runtime endpoint configured."],
  "source": "[SOURCE_REPOSITORY]",
  "version": "[COMMIT_HASH]"
}
```

Registry SHA-256 is recomputed at startup and exposed at `/api/manifest`.

## Execution record (MongoDB: `executions`)

`id` (uuid) · `connector_id` · `connector_name` · `task` · `params` · `state` (PASS/FAIL/UNAVAILABLE/NOT_CONFIGURED/BLOCKED) · `ok` · `summary` · `details` · `measured` (real numbers only) · `evidence_level` · `source` · `created_at`

## Evidence record (MongoDB: `evidence_records`)

`id` · `type: "execution_result"` · `execution_id` · `claim` · `level: "NOT_MEASURED"` · `provisional_level: null` · `hash` (SHA-256 over the execution payload, canonical JSON) · `provenance {source, recorded_at}` · `note` · `append_mode: "append_by_convention"`

Rules enforced by construction:

- A record's `level` is always `NOT_MEASURED` until authoritative E0–E5 definitions exist and a real measurement maps to one.
- `hash` recomputable from the execution payload — tamper detection is possible today; cryptographic immutability is not yet enforced (`VERIFICATION_REQUIRED`).

## Audit log (MongoDB: `audit_log`)

`id` · `event` (e.g. `execution.attempt`) · `detail` · `time` — exposed via `/api/authority` as the public audit trail.

## Replacement path for authoritative data

All placeholders are data, not schema: `[SOURCE_REPOSITORY]`, `[COMMIT_HASH]`, `[API_ENDPOINT]`, `[EVIDENCE_RECORD]`, `[AUTHORITATIVE_DEFINITION_PENDING]` are replaced by editing `data/registry.json`, `data/evidence_ladder.json`, `data/authority.json`, or connector env vars — no frontend or API restructuring required.
