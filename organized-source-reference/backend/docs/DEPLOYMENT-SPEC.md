# DEPLOYMENT-SPEC

## Environments

| Channel | State | Notes |
|---|---|---|
| Development / preview | **LIVE** | This build. Frontend :3000, backend :8001 behind `/api` ingress. |
| Staging | `INTEGRATION_REQUIRED` | Requires staging datastore + at least one configured connector endpoint. |
| Production | `BLOCKED` | Blocked on: custom domain, production secrets, configured external runtimes, security review. |

## Configuration (environment variables — never hardcoded)

**Backend** (`.env`): `MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`, and per-connector endpoints `KCN_RUNTIME_ENDPOINT`, `MANIFEX_RUNTIME_ENDPOINT`, `KSI_RUNTIME_ENDPOINT`, `TEVV_RUNTIME_ENDPOINT`, `ARENA_RUNTIME_ENDPOINT`, `WITNESS_ENDPOINT` (all optional; unset → `NOT_CONFIGURED`).

**Frontend** (`.env`): `REACT_APP_BACKEND_URL` — the only backend origin the browser may call.

## Health checks

- `GET /api/health` → `status`, `datastore`, **measured** `datastore_ping_ms`, uptime. Used for liveness; returns real state even when degraded.
- `GET /api/manifest` → release identity: version `0.1.0`, channel, registry SHA-256, component counts. Treat the registry hash as the build fingerprint.

## Release manifest policy

A release is identified by: package version + `registry_sha256` + channel. If the registry changed, the hash changed — the release manifest makes that visible instead of hiding it.

## Deployment checklist (gates, in order)

1. [ ] Acceptance suite green against the target: `python /app/tests/run_acceptance.py <BASE_URL>`
2. [ ] Production CORS origins set (no `*`)
3. [ ] Connector endpoints configured for every system intended to actually execute
4. [ ] Custom domain + TLS
5. [ ] Security review per SECURITY-REQUIREMENTS
6. [ ] Only then: production channel flips from `BLOCKED`
