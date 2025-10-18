Quick Run Guide

Prereqs
- Python 3.11+
- Node 18+

Backend (API)
- Create/activate venv and install: `pip install -r requirements.txt`
- Configure env (dev defaults ok): ensure `DATABASE_URL` (e.g., `sqlite:///./propertypro_dev.db`), `ALLOWED_ORIGINS=http://localhost:5173`
- Migrate: `cd backend/app && alembic upgrade head && cd ../../..`
- Seed contacts: `python backend/scripts/seed_contacts.py`
- Run API: `uvicorn backend.app.main:app --reload --port 8000`

Brochure Feature
- Ensure `reportlab` installed (included in `requirements.txt`) for PDF fallback.
- Create a brochure draft via UI (AI Workflow → Brochure) or API:
  - `POST /api/v1/brochures { "templateKey": "clean-minimal" }`
  - `POST /api/v1/brochures/{id}/render` then `GET /api/v1/brochures/{id}/download`
- Frontend flags: set `VITE_API_BASE_URL` and `VITE_USE_REAL_API=true` to use live endpoints.
- Uploads served from `/uploads` (saved under `uploads/`).

Frontend (Vite)
- `cd aura-client && npm i`
- Copy `.env.example` to `.env` and set:
  - `VITE_API_BASE_URL=http://localhost:8000`
  - `VITE_USE_REAL_API=true` (set to `false` to use mocks)
  - `VITE_DEV_AUTH_TOKEN=dev`
- Start: `npm run dev`

Notes
- Contacts endpoints are available at `/contacts`, `/contacts/{id}`, `/contacts/{id}/activity`.
- Follow-ups at `/followups` (GET with `?contactId=...`, POST JSON body).
- When DB is unavailable, endpoints gracefully fall back to in-memory mocks.

Tests
- Backend: `pytest -q backend/app/tests/test_brochure_routes.py`
- Frontend (planned): vitest specs under `aura-client/src/__tests__` when added.

Contracts
- Linux/macOS: `./scripts/generate-types.sh`
- Windows (PowerShell):
  - `python scripts/export_openapi_min.py scripts/openapi.json`
  - `npx openapi-typescript scripts/openapi.json --output aura-client/src/types/api.d.ts`
