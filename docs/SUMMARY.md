# AURA Audit Summary

- Backend routes for contacts, follow-ups, and export flows currently mask database or auth failures by falling back to mocked data, which hides broken persistence and leaves sensitive exports unauthenticated.
- CMA workflows are only partially implemented: the frontend renders locally cached data while the backend issues raw SQL against unseeded tables, so end-to-end assistants cannot generate or retrieve a real report.
- Tooling and pipelines are brittle; Python paths, dependency pins, and CI workflow assumptions block automated validation and leave security/performance testing unexecuted.
- Recommended runtime matrix is Python 3.11 / Node 20 with slimmed dependencies and explicit optional extras instead of the current 3.13 runtime and monolithic requirements list (tensorflow, torch, prophet, etc.).

## Top 10 Fixes

1. **Require real persistence for contacts & follow-ups (BE)** – Remove blanket `except Exception` fallbacks and align models (`clients` vs `contacts`) so API errors surface and data truly persists (`backend/app/api/v1/contacts_router.py:168`, `backend/app/api/v1/followups_router.py:87`, `backend/app/domain/listings/enhanced_real_estate_models.py:224`).
2. **Finish CMA orchestration (FE/BE)** – Wire the frontend to call `/api/v1/cma/*`, add polling, and harden backend task orchestration so report creation no longer depends on mock store state (`aura-client/src/pages/CMAReport.tsx:42`, `backend/app/api/v1/cma_reports_router.py:135`).
3. **Lock down export endpoints (Sec/BE)** – Require auth + content-type validation for `/api/v1/export/html-save` and `/api/v1/export/brochure-mock`, move outputs to signed URLs, and strip arbitrary HTML writes served from `/uploads` (`backend/app/api/v1/export_router.py:119`, `backend/app/api/v1/export_router.py:535`).
4. **Stabilise brochure rendering pipeline (BE)** – Guard against `None` data blobs before mutating `row.data["meta"]`, persist render job status, and surface errors back to the client (`backend/app/api/v1/brochures_router.py:105`, `backend/app/api/v1/brochures_router.py:142`).
5. **Provide brochure templates via data seeding (BE/FE)** – Seed `brochure_templates`, expose read-only API, and ensure the frontend switches `VITE_USE_REAL_API` when the backend is reachable (`backend/scripts/seed_brochure_templates.py:10`, `aura-client/src/features/brochure/api/brochure.ts:29`).
6. **Rationalise Python dependencies & version pinning (Infra)** – Trim heavyweight ML packages into optional extras and standardise on Python 3.11 to avoid ABI drift seen on 3.13 (`backend/requirements.txt:1`, `backend/requirements.txt:17`).
7. **Repair automated tests & pytest config (QA/Infra)** – Replace the unsupported `python_paths` directive with `PYTHONPATH=backend`, add packaging to resolve `ModuleNotFoundError`, and run the current contact/follow-up tests in CI (`pytest.ini:2`, `backend/tests/test_contacts_api.py:8`).
8. **Update CI workflow to match repo layout (Infra)** – Point frontend steps at `aura-client`, gate optional Playwright install, and supply the backend env (DB URL, GOOGLE_API_KEY) needed for real test execution (`.github/workflows/ci.yml:70`, `.github/workflows/ci.yml:110`).
9. **Tighten development auth bypass (Sec)** – Default `DISABLE_AUTH` to false, add env-based guards, and ensure dev tokens are never issued outside local contexts (`backend/app/core/dev_auth_bypass.py:32`, `backend/app/core/dev_auth_bypass.py:86`).
10. **Instrument feature flows with telemetry & history (FE/BE)** – Persist brochure/follow-up actions to activity timelines instead of localStorage mocks and surface request IDs for traceability (`aura-client/src/services/contactsApi.ts:67`, `aura-client/src/services/schedulesApi.ts:31`).

