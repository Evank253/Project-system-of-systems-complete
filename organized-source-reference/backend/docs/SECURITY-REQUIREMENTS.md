# SECURITY-REQUIREMENTS

## Implemented in this build (basic — TEST_REQUIRED)

| Control | Implementation | Limits |
|---|---|---|
| Secret management | Environment variables only (`MONGO_URL`, `DB_NAME`, `*_RUNTIME_ENDPOINT`). No secrets in client code. | Rotation procedure pending. |
| API boundaries | Single `/api` ingress; privileged operations server-side only. The browser never talks to external runtimes. | — |
| Rate limiting | Per-IP sliding window (default 30/min) on execution creation → HTTP 429. | In-memory, single-process. Distributed limiter required at production scale. |
| Audit logging | Every execution attempt recorded (`audit_log`) and exposed at `/api/authority`. | No tamper-evidence yet. |
| CORS | Configured via `CORS_ORIGINS` env. | Tighten for production (no `*`). |

## Required before production (`INTEGRATION_REQUIRED` / `BLOCKED`)

1. **Authentication** — identity for privileged operations. Not implemented; no privileged operations exist yet.
2. **Authorization** — permission checks aligned with the KSI authority model (H0–H3).
3. **Secret management hardening** — managed secret store, rotation, least privilege for connector endpoints.
4. **Transport & headers** — TLS via host platform; add CSP, HSTS, strict headers at the edge.
5. **Distributed rate limiting** — shared store (Redis or equivalent) when scaled beyond one process.
6. **Tamper-evident records** — append-only storage or hash-chaining for evidence and audit.

## Non-negotiable invariants

- External API credentials never appear in client-side code.
- The Live Test interface never fabricates a success to look complete.
- Security findings and limitations are published, not hidden: the registry's `limitations` fields are part of the public product.
