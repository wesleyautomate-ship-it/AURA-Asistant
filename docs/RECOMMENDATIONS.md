# Recommendations & Acceptance Criteria

## Prioritised Fixes

| # | Recommendation | Owner | Evidence | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| 1 | Enforce DB-backed contacts/follow-ups and remove mock fallbacks | Backend | `backend/app/api/v1/contacts_router.py:168`, `backend/app/api/v1/followups_router.py:87` | API returns 500 on DB failure, integration test covers SQLite + Postgres, follow-ups persist in DB and surface in timeline |
| 2 | Complete CMA workflow (frontend + orchestrator) | FE/BE | `aura-client/src/pages/CMAReport.tsx:42`, `backend/app/api/v1/cma_reports_router.py:135` | Submitting CMA returns task id, status polling updates UI, generated PDF stored + linked in contact history |
| 3 | Secure export & uploads pipeline with auth + signed URLs | Security/BE | `backend/app/api/v1/export_router.py:119`, `backend/app/domain/ai/file_storage_service.py:88` | Upload endpoints require JWT, saved files accessible only via signed URL, security scan passes (ZAP baseline) |
| 4 | Harden brochure render error handling and async offload | Backend | `backend/app/api/v1/brochures_router.py:105`, `backend/app/api/v1/brochures_router.py:142` | Render job enqueues background task, job status transitions tracked, clients receive ready/error updates |
| 5 | Seed brochure templates & align env flags | BE/FE | `backend/scripts/seed_brochure_templates.py:18`, `aura-client/src/features/brochure/api/brochure.ts:29` | Templates endpoint returns ≥3 records, frontend toggles real API in staging/prod, template cache invalidates on upload |
| 6 | Trim and pin dependency matrix (Python 3.11, extras) | Infra | `backend/requirements.txt:17`, `python --version` | Requirements split into `base`/`extras`, CI installs on 3.11, dependency scan clean |
| 7 | Fix pytest path + CI workflow layout | QA/Infra | `pytest.ini:2`, `.github/workflows/ci.yml:110` | `pytest` runs locally/CI without ModuleNotFound, workflow uses `aura-client` scripts and passes |
| 8 | Lock down dev auth bypass | Security | `backend/app/core/dev_auth_bypass.py:32` | Dev tokens only issued when `DEV_AUTH_ALLOW=1`, log warning with host info, staging/prod refuse bypass |
| 9 | Add `comps` table + indexes for CMA | Backend/DB | `backend/app/domain/listings/enhanced_real_estate_models.py:336` | Alembic migration adds `comps`, indexes exist, queries use ORM with pagination |
| 10 | Instrument history/audit for key actions | BE/FE | `backend/app/core/models.py:159`, `aura-client/src/pages/contacts/[id].tsx:233` | Creating follow-up/brochure/CMA writes audit log, UI reflects event with request id |

## Acceptance Checklists

### Contacts Flow
- [ ] `GET /contacts` surfaces DB data with pagination and filtering.
- [ ] Notes PATCH endpoint persists and returns updated content.
- [ ] Follow-up creation updates DB + timeline; audit log entry created.
- [ ] UI handles network failure retry + shows toast on persistence errors.

### Brochure Flow
- [ ] Template listing returns seeded data; UI toggles real API in staging.
- [ ] Draft autosave handles network errors (retry/backoff) and surfaces status message.
- [ ] Render job runs asynchronously and updates status via SSE/polling.
- [ ] Download link uses signed URL; audit log entry created.

### CMA Flow
- [ ] Submitting request creates orchestrated task and returns task id.
- [ ] Status endpoint reflects each step (comps fetch, valuation, render).
- [ ] Generated PDF stored in object storage and linked to contact.
- [ ] UI displays progress, handles errors, and allows retry/revision.
