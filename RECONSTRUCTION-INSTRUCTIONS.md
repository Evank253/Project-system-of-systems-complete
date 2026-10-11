# RECONSTRUCTION INSTRUCTIONS — KETCHUM SOS (isolated clone)

Goal: reconstruct the exported application in a SEPARATE environment with its OWN datastore. Nothing here connects to, modifies, or deploys over the original application. (Original relative paths are preserved in the export root.)

## 1. Prerequisites
- Python 3.11+ (the workspace image is `fastapi_react_mongo_shadcn_base_image_cloud_arm`)
- Node.js 18+ and yarn
- A MongoDB instance YOU control (local `mongod`, Docker, or Atlas) — do NOT point the clone at any Emergent-managed datastore
- For AI features only: an Emergent LLM key (or an OpenAI-compatible key wired through `emergentintegrations`)

## 2. Unpack and install
```
unzip KETCHUM-SOS-SOURCE-EXPORT-2026-10-09.zip
cd KETCHUM-SOS-SOURCE-EXPORT/backend
pip install -r requirements.txt
# NOTE: emergentintegrations installs from Emergent's package index:
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

cd ../frontend
yarn install          # uses the included yarn.lock for pinned versions
```

## 3. Configure environment (names only — supply values out-of-band)
Create `backend/.env` (copy `backend/.env.example`, which contains NAMES and purposes only):
- `MONGO_URL` — your OWN MongoDB connection string, e.g. `mongodb://localhost:27017` (NEVER the original application's)
- `DB_NAME` — database name (use a fresh, disposable name for the clone)
- `CORS_ORIGINS` — allowed origins for the clone
- `EMERGENT_LLM_KEY` — only if you want AI features; omit to run everything else
- `AI_MODEL_SOL`, `AI_MODEL_LUNA`, `AI_RATE_LIMIT_PER_MIN` — AI model ids and rate limit

Create `frontend/.env` (copy `frontend/.env.example`):
- `REACT_APP_BACKEND_URL` — the clone's own backend base URL (e.g. `http://localhost:8001`)
- `WDS_SOCKET_PORT`, `ENABLE_HEALTH_CHECK` — dev-server settings (as in the example file)

Never copy environment VALUES from the original application. The clone must not reference the original datastore or credentials.

## 4. Start the clone
```
# Terminal 1 — backend (mirrors the workspace: 0.0.0.0:8001)
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001

# Terminal 2 — frontend (CRA dev server, port 3000)
cd frontend && yarn start
```
The application creates its MongoDB collections at runtime — there are no migrations to run (none exist in the project).

## 5. Run the existing tests (against the CLONE, not the original)
```
python tests/run_acceptance.py http://localhost:8001
python tests/run_adversarial.py http://localhost:8001
python tests/run_eil_adversarial.py http://localhost:8001
```
These write real records into the CLONE's datastore (that is their function). Expect approximately: acceptance 17/17, adversarial 7/7, EIL adversarial 18 PASS + 3 NOT_MEASURED + 0 FAIL — results are the clone's own; they verify the reconstruction, not the original.

## 6. Verify the API and health endpoints
- `GET http://localhost:8001/api/inspect?format=md` — full state dump
- `GET /api/eil/constitution` — should report the frozen constitution hash `89f0e26d077626eebfa6c7bbbaa1c53b1a728b37f4d3bc4e60f006ccbd4381ab`
- `GET /api/eil/authority-ledger` — starts empty (or with test-created records); the original's 79-record history is NOT included and must not be imported
- `GET /api/evidence/verify`, `GET /api/ksi`, `GET /api/docs/external-tevv-package`

## 7. What will NOT work without extra configuration
- AI assistant endpoints (Ask the System / Explain) — need `EMERGENT_LLM_KEY` (or a substitute key via emergentintegrations)
- All external system connectors (KCN, MANIFEX, KSI, TEVV, ARENA, Witness) — intentionally `NOT_CONFIGURED`; there are no real endpoints to configure yet
- Public preview URL/edge behaviors (Cloudflare bot management, preview ingress) — platform services, not part of the source
- The original application's live data — deliberately NOT included; the clone starts with an empty datastore

## 8. Isolation rules (from the owner)
- The clone never connects to the original application's live datastore or credentials.
- No migrations or data imports from the original.
- The original application remains the preserved source of truth; the export is a fixed reconstruction baseline.
