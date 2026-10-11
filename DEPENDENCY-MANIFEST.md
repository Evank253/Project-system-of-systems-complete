# DEPENDENCY MANIFEST — KETCHUM-SOS-SOURCE-EXPORT-2026-10-09

## Backend (Python — pinned in backend/requirements.txt, included in export)

| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.110.1 | Web framework / API |
| uvicorn | 0.25.0 | ASGI server |
| motor | 3.3.1 | Async MongoDB driver (primary datastore access) |
| pymongo | 4.6.3 | MongoDB driver (motor dependency) |
| pydantic | >=2.6.4 | Request/response models |
| emergentintegrations | 0.2.2 | **Emergent-managed LLM integration library** (AI assistant; installs from Emergent's package index `https://d33sy5i8bnduwe.cloudfront.net/simple/`) |
| python-dotenv | >=1.0.1 | .env loading |
| bcrypt / passlib / PyJWT / python-jose | 4.1.3 / >=1.7.4 / >=2.10.1 / >=3.3.0 | Crypto/auth utilities present in the dependency set |
| requests | >=2.31.0 | Outbound HTTP (test kits, connectors) |
| pytest / pytest-xdist | >=8.0.0 / >=3.6.0 | Test runners |
| pandas / numpy | >=2.2.0 / >=1.26.0 | Data utilities (present in requirements) |
| black / isort / flake8 / mypy | latest-pinned | Tooling |
| boto3, requests-oauthlib, cryptography, email-validator, tzdata, python-multipart, jq, typer | as pinned | Supporting libraries |

## Frontend (JavaScript — pinned in frontend/package.json + yarn.lock, both included)

| Package | Version |
|---|---|
| react / react-dom | 19.0.0 |
| react-router-dom | 7.18.4 |
| framer-motion | 11.18.0 |
| tailwindcss | 3.4.17 (dev) |
| Build toolchain | Create React App via craco (`craco start/build/test`) |
| shadcn/ui components | vendored in frontend/src/components/ui (radix-based) |
| sonner | toast notifications |

## Platform-managed dependencies (NOT in the source — configure separately)

| Dependency | Provided by | Environment variable (NAME only) |
|---|---|---|
| MongoDB datastore | Emergent workspace (in original); clone supplies its OWN | `MONGO_URL`, `DB_NAME` |
| Emergent LLM universal key (AI features) | Emergent platform | `EMERGENT_LLM_KEY` |
| CORS configuration | Workspace .env | `CORS_ORIGINS` |
| AI model ids + rate limit | Workspace .env | `AI_MODEL_SOL`, `AI_MODEL_LUNA`, `AI_RATE_LIMIT_PER_MIN` |
| Frontend backend URL / dev-server config | Workspace .env | `REACT_APP_BACKEND_URL`, `WDS_SOCKET_PORT`, `ENABLE_HEALTH_CHECK` |
| Public hosting, TLS, ingress, Cloudflare bot management | Emergent platform + Cloudflare edge | (platform service — no env var) |
| Process supervision | supervisor (backend :8001, frontend :3000) | (platform service) |

## External service connectors (source included — all NOT_CONFIGURED by design)

kcn.py, manifex.py, ksi.py, tevv.py, arena.py, witness.py (+ base.py, app_selftest.py) — no real endpoints exist yet; the application reports them NOT_CONFIGURED and blocks on them honestly.

## Secret handling in this export

No `.env` values were exported. The two `.env.example` files contain variable NAMES and documented purposes only. A secret-pattern scan (key/token/password prefixes) over all exported source found no hardcoded credentials.
