# Deep Audit

## Backend

- **Monolithic entrypoint**: `backend/app/main.py` pulls in 20+ routers and tool imports at module load, so optional features (Chromadb, WeasyPrint) can break startup without lazy guards (`backend/app/main.py:52`, `backend/app/main.py:334`). Refactor into feature modules with conditional registration.
- **Contacts & follow-ups rely on silent fallbacks**: Broad `except Exception` blocks swallow DB errors and revert to static in-memory stores (`backend/app/api/v1/contacts_router.py:168`, `backend/app/api/v1/followups_router.py:87`). This hides schema or connection issues and prevents operators from noticing persistence failures.
- **Schema mismatch**: The CRM model still stores people in `clients` (`backend/app/domain/listings/enhanced_real_estate_models.py:224`), but the rest of the stack (docs, seeds, expected tables) assumes `contacts`. Reporting and FK references should be aligned before production data lands.
- **CMA orchestration incomplete**: `/api/v1/cma/create` builds quick valuations with raw SQL text queries over `properties` but no ORM models or migrations ensure these tables exist (`backend/app/api/v1/cma_reports_router.py:197`). Downstream endpoints expect background tasks and status polling that never run if no orchestrator is injected.
- **Brochure rendering fragility**: Error handling mutates `row.data["meta"]` without ensuring the JSON blob exists, causing `TypeError` and locking drafts in `rendering` (`backend/app/api/v1/brochures_router.py:105`, `backend/app/api/v1/brochures_router.py:142`). There is no job tracking or retry.
- **Export service security gap**: Both `/api/v1/export/html-save` and `/api/v1/export/brochure-mock` accept arbitrary HTML and write to a publicly served directory without auth or sanitisation (`backend/app/api/v1/export_router.py:119`, `backend/app/api/v1/export_router.py:535`). Attackers could plant hostile scripts and have them hosted through `/uploads`.
- **Dev auth bypass defaults**: `DISABLE_AUTH` toggles allow unconditional bypass even in Docker or staging if `ENVIRONMENT` mis-set (`backend/app/core/dev_auth_bypass.py:32`, `backend/app/core/dev_auth_bypass.py:86`). Force explicit opt-in and log when bypass is active.
- **Dependencies**: `requirements.txt` pulls heavyweight ML stacks (TensorFlow, Torch, Prophet) that are unused in brochure/CMA flows, inflating build size and breaking on Python 3.13 (`backend/requirements.txt:17`). Split optional extras and pin FastAPI ecosystem versions (0.115/0.37/0.27/pydantic 2.8) as recommended.
- **Observability**: Request logging middleware adds request IDs, but there is no metrics export or structured log sink by default (`backend/app/core/middleware.py:69`). Add OpenTelemetry/Prometheus instrumentation and expose `/metrics`.

## Frontend & UX

- **Mock-first API mode**: `api.enabled` defaults to `false`, so contacts, follow-ups, and recommendations stay in localStorage with no persistence (`aura-client/src/services/http.ts:3`, `aura-client/src/services/contactsApi.ts:22`). Operators never exercise real endpoints unless they set env vars.
- **CMA view uses cached store**: The CMA page reads from `commandStore` without hitting the backend (`aura-client/src/pages/CMAReport.tsx:42`). Requests never poll `/api/v1/cma/reports/{taskId}/status`, so actual CMA generation is invisible to users.
- **Scheduling & history**: After creating a follow-up the UI re-fetches the mock store rather than the API, so timelines desynchronise with the backend (`aura-client/src/services/schedulesApi.ts:47`). Activity stream updates rely on optimistic inserts.
- **Accessibility & copy**: Several components embed mojibake (`A` characters) from copy-pasted glyphs (`aura-client/src/components/Dashboard/Contacts/ContactsWorkspaceV2.tsx:88`, `aura-client/src/pages/contacts/[id].tsx:260`). Replace with plain ASCII and add aria labels for long-press/selection controls.
- **Error states**: Contacts list handles loading and empty states, but CMA and brochure templates lack retries/backoff; failing fetch leaves spinners without messaging (`aura-client/src/features/brochure/hooks/useBrochureDraft.ts:15`).
- **Type fidelity**: Types map `Contact['temperature']` but coerce backend `status` strings ad hoc (`aura-client/src/services/contactsApi.ts:25`). Align enums with backend schema to avoid impossible states.

## Database & Migrations

- **Detected tables**: `Base.metadata` includes `clients`, `followups`, `contact_notes`, `properties`, `market_data`, etc. but there is no `comps` table or indexes promised in the spec (`backend/app/domain/listings/enhanced_real_estate_models.py:336`). Add migrations for `comps` and target indexes (`idx_followups_contact_due`, etc.).
- **Alembic gap**: Repo ships raw SQL migration scripts without Alembic heads, and CI calls `alembic upgrade` in `backend/app` even though no Alembic config lives there (`.github/workflows/ci.yml:90`). Replace with managed Alembic environment rooted at `backend`.
- **Seeds**: Multiple seed scripts exist but there is no canonical run order; `seed_brochure_templates.py` expects the ORM schema yet does not handle conflicts (`backend/scripts/seed_brochure_templates.py:18`). Document consistent seeding (templates, contacts, properties) in the runbook.

## Infrastructure & Tooling

- **Runtime matrix**: Local environment runs Python 3.13.9 (`python --version`) whereas FastAPI stack recommends 3.11; third-party wheels (tensorflow, prophet) do not publish 3.13 builds. Node is 22.x but Vite recommends 18/20; lock via `.python-version`/`.nvmrc`.
- **Pytest failures**: Running `pytest` errors with `ModuleNotFoundError` because `PYTHONPATH` lacks `backend` and `python_paths` option is unsupported (`pytest.ini:2`, `backend/tests/test_contacts_api.py:8`). Provide `conftest` fixture or adopt `pytest-pythonpath`.
- **CI mismatch**: Workflow references `client` directory and `lint:web` scripts that do not exist; should point at `aura-client` commands (`.github/workflows/ci.yml:110`). Playwright install runs even for simple builds, slowing CI.
- **Secrets**: `.env` files are committed with sample keys; ensure environment loading defers to `config/` and rotate secrets.

## Performance & Reliability

- **Blocking IO**: Rendering and file writes happen inline on the request thread (`backend/app/api/v1/brochures_router.py:133`, `backend/app/domain/ai/file_storage_service.py:65`). Offload to background jobs or worker pool to protect response latency.
- **Timeouts/Retries**: No HTTP clients set timeouts; recommended to wrap external APIs (Gemini, MLS) in `tenacity` or HTTPX with retries.
- **Health endpoints**: `/health` and `/healthz` respond quickly (`backend/app/main.py:587`), but `/version` still returns static constant; expose git hash/build time.
- **Streaming**: Frontend SSE fallback is implemented, but backend simply streams JSON without heartbeat; add keepalive to avoid idle timeouts.

## UX & Governance

- **Auditability**: Follow-up creation does not write to `AuditLog` or timeline; plan to append to `activities` table and surface in UI (`backend/app/core/models.py:159`, `aura-client/src/pages/contacts/[id].tsx:233`).
- **History**: Command center stores generated content in localStorage (`aura-client/src/store/commandStore.ts:450`), which breaks when multiple agents share devices. Migrate to backend history endpoints.

## Blocking Issues

1. **Contacts/follow-ups persistency** – Without DB-backed operations the assistant cannot claim CRM accuracy.
2. **Export endpoint exposure** – Arbitrary HTML upload served from `/uploads` is a security blocker before launch.
3. **CMA workflow incompleteness** – No end-to-end CMA generation prevents flagship capability from shipping.
