# SYSTEM-ARCHITECTURE

```
KETCHUM SYSTEM-OF-SYSTEMS
│
├── 01 — PUBLIC APPLICATION        (this package: frontend SPA)
├── 02 — APPLICATION API           (this package: FastAPI /api/*)
├── 03 — SYSTEM CONNECTORS         (this package: interface stubs → external runtimes)
│      ├── KCN                      authoritative external system
│      ├── MANIFEX                  authoritative external system
│      ├── KSI                      authoritative external system
│      ├── TEVV                     authoritative external system
│      ├── ARENA                    authoritative external system
│      └── Independent Witness      authoritative external party
├── 04 — EVIDENCE SYSTEM           (this package: records + hashes; E0–E5 definitions pending)
├── 05 — AUTHORITY                 (model documented here; enforced by KSI + humans)
├── 06 — TEVV                      (basic execution runner here; independent gates external)
├── 07 — SECURITY                  (boundaries, rate limits, audit — basic, TEST_REQUIRED)
└── 08 — DEPLOYMENT                (development live; staging INTEGRATION_REQUIRED; production BLOCKED)
```

## Principle of layering

- The **public application** is a product/interface layer. It is *not* the system of systems; it is how the outside world inspects it.
- The **authoritative source** for any system remains its actual repository, runtime, artifact, and evidence record.
- Connectors are one-directional reporters: they forward tasks and return **factual states**. They cannot upgrade themselves.

## Execution data flow (implemented)

```
Browser (Live Test page)
  → POST /api/executions {connector_id, task}
    → rate limit (per IP)
    → connector dispatch
        ├─ app-selftest: real measurement against this deployment's datastore
        └─ external stubs: endpoint env var set?
              ├─ no  → NOT_CONFIGURED
              └─ yes → real HTTP call → PASS / FAIL / UNAVAILABLE (actual response)
    → execution record persisted
    → evidence record persisted (SHA-256 hash, provenance, level NOT_MEASURED)
    → audit log entry
  ← result panel shows the factual state, measured values, and evidence hash
```

## What is deliberately NOT in this build

- No authentication/authorization runtime (no privileged operations exist yet) — `INTEGRATION_REQUIRED`.
- No E0–E5 semantic definitions — `[AUTHORITATIVE_DEFINITION_PENDING]`.
- No benchmark values — the Benchmarks surface is explicitly empty.
- No verification or qualification stamps — impossible without an independent witness.
