# EXPORT REPORT — KETCHUM-SOS-SOURCE-EXPORT-2026-10-09

| Field | Value |
|---|---|
| Source project | KETCHUM SYSTEM-OF-SYSTEMS (Emergent workspace `/app`) — the existing application is the source of truth; nothing was regenerated |
| Export timestamp | 2026-10-09 (UTC) — generated at export time, recorded in FILE-MANIFEST.json |
| Source tree | git `09eefd1fcfbfbbaaa5a5e0205904903104133156` (2026-10-08 20:54:09 UTC) — includes the full EIL integration |
| Languages / frameworks | Python 3 / FastAPI 0.110.1 / uvicorn 0.25.0 / Motor 3.3.1 (MongoDB async) / emergentintegrations 0.2.2 · JavaScript / React 19.0.0 / react-router-dom 7.18.4 / framer-motion 11.18.0 / Tailwind CSS 3.4.17 / CRA-via-craco |
| Files discovered & exported | **148** (see FILE-MANIFEST.json / FILE-MANIFEST.md) |
| Hash verification | **PERFORMED for every copied file**: SHA-256 of each source file compared against its exported copy — **0 mismatches** |
| This export REPLACES | the stale `ketchum-sos-source-export.zip` (2026-10-08 19:26 UTC) which predated the EIL integration and is OUTDATED — do not use it for EIL review |

## What is included (by category)

| Category | Count | Notes |
|---|---|---|
| Backend source | 8 | server.py (FastAPI app + route map), eil.py (constitutional engine, single guarded authority writer, hash-chained authority ledger), ksi.py (KSI boundary), lifecycle.py (lifecycle + evidence chain), ai_assistant.py, pytest.ini |
| Backend connectors | 9 | base.py + kcn, manifex, ksi, tevv, arena, witness, app_selftest — all report NOT_CONFIGURED by design (no real endpoints exist) |
| Project-owned static data | 6 | registry.json (74-item component registry), evidence_ladder.json (E0–E5 = AUTHORITATIVE_DEFINITION_PENDING placeholders + NOT_MEASURED + 10 rules), authority.json, SYSTEM-MANIFEST.json, docs_index.json, eil/constitution.json (frozen constitution, SHA-256 `89f0e26d077626eebfa6c7bbbaa1c53b1a728b37f4d3bc4e60f006ccbd4381ab`) |
| Documentation | 21 | All backend/docs/*: SYSTEM-ARCHITECTURE, API-SPECIFICATION, DATA-MODEL, AUTHORITY-MODEL, EVIDENCE-MODEL, TEVV-MODEL, LIFECYCLE-ENFORCEMENT, SECURITY-REQUIREMENTS, ACCEPTANCE-GATES, TEST-MATRIX, COMPLETION-MATRIX, DEPLOYMENT-SPEC, UI-SPEC, AI-INTERFACE, EIL-CONSTITUTION, EIL-INTEGRATION-PROPOSAL, EXTERNAL-TEVV-PACKAGE, HOW-TO-INSPECT, RESEARCH-NOTES, BASE44-MASTER-PROMPT, README — preserved AS-IS (historical records, not rewritten) |
| Frontend source | 75 | All pages (Home/Hero/ArchitectureMap/InvariantModels/TevvLive, Explorer, DocsPage, EvidencePage, LiveTest, AskPage), 9 custom components, 39 shadcn ui components, lib (api.js, stream.js, utils.js), hooks, testIds constants, App.js, index.js, index.css |
| Frontend config | 6 + 2 | package.json, yarn.lock (dependency lockfile), craco/tailwind/postcss configs, components.json, jsconfig.json, README, plugins/health-check (2 files), public/index.html + favicon.svg |
| Test source | 5 | run_acceptance.py, run_adversarial.py, run_eil_adversarial.py, external_tevv_reproduction.py (public-URL reproduction kit), __init__.py — real assertions preserved as-is |
| Platform configuration | 8 | .emergent/emergent.yml + cron scripts + bootstrap markers |
| Root | 3 | README.md, .gitignore, design_guidelines.json (design system) |
| Sanitized env templates | 2 | backend/.env.example + frontend/.env.example — variable NAMES + documented purposes ONLY; no values were ever present in the export |

## Exclusions (with reasons)

| Excluded | Reason |
|---|---|
| `backend/.env`, `frontend/.env` | Contain secret/connection values. Variable names documented in `.env.example` files and DEPENDENCY-MANIFEST.md. Values were never copied into the export. |
| `frontend/node_modules/` | Restorable via `yarn install` from lockfile (580K lockfile included). |
| `tests/evidence/` | Incident/evidence materials (session transcripts, incident record) — preserved separately in the project evidence tree; NOT application source; deliberately not republished in this export. |
| `frontend/public/evaluator-bundle/`, `frontend/public/evaluator-bundle-2026-10-08.tar.gz` | Evidence publications (owner-authorized, separate workstream) — not application source. |
| `.git/` | VCS history preserved in the original workspace; export is a source-only snapshot (avoids history-wide leak surface). Obtainable separately via the platform's Save-to-GitHub mechanism if needed. |
| `/app/ketchum-sos-source-export.zip` | STALE prior export (2026-10-08 19:26 UTC, pre-EIL). Superseded by this export. |
| `.emergent/recordings/` | Platform runtime crash artifacts, not source. |
| `memory/`, `test_reports/`, `test_result.md`, `.ruff_cache`, `__pycache__` | Agent working artifacts / caches, not application source. |

## Dependencies on platform-managed services (not included in source)

1. **MongoDB** — the platform provides `MONGO_URL` (backend/.env). A clone must run its OWN MongoDB instance and supply its own `MONGO_URL`. No database data, migrations, or seeds are included (MongoDB; no migration framework exists in the project — collections are created by the application at runtime).
2. **Emergent LLM Key** — `EMERGENT_LLM_KEY` powers the AI assistant (Ask the System / Explain) via `emergentintegrations==0.2.2` (installed from Emergent's package index). Without a key, AI endpoints will fail; everything else runs.
3. **Preview hosting/ingress + Cloudflare** — the public URL, TLS, and edge bot-management (403 on default python-urllib UAs; challenge-script injection into HTML responses) are platform/edge services. A clone runs on its own host.
4. **Supervisor process management** — the workspace runs backend (0.0.0.0:8001) and frontend (0.0.0.0:3000) under supervisor; standalone instructions in RECONSTRUCTION-INSTRUCTIONS.md.

## Documented architecture vs observed source

- The exported source IS the observed implementation (no regeneration). Docs are preserved as historical records; the export does not certify doc-to-code line-level equivalence — the external TEVV process examined the authority-path code specifically (eil.py, ksi.py, lifecycle.py, server.py) and its results are in the preserved evidence records.
- One documented-vs-observed nuance for reviewers: uvicorn's own access log exists in the workspace but does not cover static-file serving (static requests terminate at the dev server) — relevant to the separate publication incident (EIL-PUB-2026-10-08-01), which is tracked in the project evidence tree, NOT in this export.

## Can a complete independent reconstruction be made from this export?

**Confirmed**: the full application source, static data, docs, tests, and lockfiles are present with verified hashes; the app can be reconstructed and run against a separate MongoDB with the documented environment variables; the 74-component registry, constitution, evidence ladder, and all enforcement code are included.
**Cannot be reconstructed from the export**: the live datastore contents (intentionally excluded); AI-assistant functionality without an Emergent LLM key (or a substitute OpenAI-compatible key wired via emergentintegrations); the public preview URL/edge behavior; the six supplied external-review documents and incident materials (preserved separately in the project; available to the owner).
**Assumptions/unresolved**: none about the source itself (hashes verify); the runtime behavior of a clone under different infrastructure (OS, MongoDB version, network) is untested by this export — verification against a clone is the owner's separate exercise.
