# Runbook

## Quickstart

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload --port 8000
```

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
export PYTHONPATH=backend
uvicorn app.main:app --reload --port 8000
```

## Prerequisites

- Python 3.11.x (repo ships `.python-version` targeting 3.11.9) with `pip` and `venv`.
- Node.js 20.x (LTS) with `npm` or `pnpm`.
- PostgreSQL 15+ for persistent data (SQLite supported for local smoke).
- Redis (optional) for rate limiting / background jobs.
- `k6` CLI (for perf smoke) and `lighthouse` (Chrome + Node) if running diagnostics.

## Feature Flags

- `ENABLE_PDF_WEASYPRINT` (default `0`): enable WeasyPrint-based PDF exports once the dependency is installed.
- `ENABLE_VECTOR_CHROMA` (default `0`): enable Chroma vector indexing features.
- `DEV_AUTH_ALLOW` (default `0`): opt-in development auth bypass; when `1` the backend logs `DEV AUTH BYPASS ENABLED  FOR DEVELOPMENT ONLY`.
- `CORS_ALLOWED_ORIGINS`: comma-separated list of origins allowed by the backend CORS middleware; defaults to `http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173`.

## Environment Variables

Create `.env` files based on `env.example`.

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | DB connection string | `sqlite:///./propertypro_dev.db` |
| `ENVIRONMENT` | `development`/`staging`/`production` | `development` |
| `GOOGLE_API_KEY` | Gemini key for AI features | _required_ |
| `SECRET_KEY` | JWT signing secret | change in non-dev |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:8000` |
| `VITE_USE_REAL_API` | Enable live API calls in UI | `true` for integration |
| `DISABLE_AUTH` | Dev-only auth bypass | leave unset |

## Local Backend Setup

```powershell
cd backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
set PYTHONPATH=backend
uvicorn app.main:app --reload --port 8000
```

> Need deep-learning toolkits? Install them separately with `pip install -r backend/extras-ml.txt` to keep base env lightweight.

### Database

```powershell
python -m app.core.database  # optional connectivity check
python scripts/setup_db.py   # creates tables if needed
python scripts/seed_brochure_templates.py
python scripts/seed_contacts.py
```

- For Postgres, ensure the database exists before running seeds.
- Alembic config pending: once added, run `alembic upgrade head`.

## Local Frontend Setup

```powershell
cd aura-client
npm install
npm run dev -- --host
```

Set `VITE_USE_REAL_API=true` in `.env.development` to exercise live endpoints once the backend runs.

## Docker (reference)

- `docker-compose.dev.yml` runs FastAPI + Postgres + frontend. Update env overrides in `docker-compose.dev.yml` to point at valid API keys and disable auth bypass.
- For production, prepare hardened compose profile (`docker-compose.secure.yml`) with TLS termination and object storage mounts for `/uploads`.

## Testing

```powershell
cd backend
set PYTHONPATH=backend
pytest -q

cd ..\aura-client
npm run typecheck
npm run lint
```

Add `pytest-pythonpath` to allow `python_paths` usage or remove the option from `pytest.ini`.

### Phase-1 Smoke

```bash
curl http://localhost:8000/health
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl http://localhost:8000/version
```

Note: `/readyz` can be used by your process manager/K8s readiness probes.

### CI snapshot

The `ci` workflow (Python 3.11) exports `PYTHONPATH=backend` for backend tests, builds `aura-client`, and uploads both `coverage.xml` and the compiled `dist/` artifacts.

## Performance & Accessibility

- Run `k6 run perf/k6/contacts-smoke.js` once the backend is live (scripts generated in `perf/k6/`).
- Build the frontend (`npm run build`) then `node scripts/lighthouse.mjs http://localhost:4173` to capture metrics.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `ModuleNotFoundError: backend.app` | Ensure `PYTHONPATH=backend` or install package with editable mode |
| Brochure render stuck at `rendering` | Confirm `weasyprint`/`reportlab` installed; inspect logs for `row.data` errors |
| `/api/v1/contacts` returns mock data | DB connection failing silently; remove fallback and inspect logs (`backend/app/api/v1/contacts_router.py`) |
| Frontend shows local mocks | Verify `VITE_USE_REAL_API=true` and backend reachable under `CORS` origins (`backend/app/core/settings.py:51`) |
| Auth bypass active unexpectedly | Check `DISABLE_AUTH` and `ENVIRONMENT`; never set to `production` when bypassing |
