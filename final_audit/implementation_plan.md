## Implementation Plan

### Phase 0 – Orientation & Baseline
- Inventory the running parts (service layout, test suites) and record current failing tests.
- Run targeted suites (`pytest app/tests/test_*`, `tests/test_aura_integration.py`, `tests/test_contacts_api.py`, `tests/test_status_endpoints.py`) to catalog missing dependencies.
- Validate `dev_data/load.py`; extend it with reset options if needed.

### Phase 1 – Brochure Flow (Single Feature Green)
- Align database/API for brochure data (`EnhancedProperty`, `PropertyPhoto`, `BrochureDraft`, `BrochureTemplate`).
- Seed canonical brochure data; ensure `/api/v1/templates` and `/api/v1/brochures` work end-to-end.
- Keep auth/login stable; extend `DEV_AUTH_BYPASS` user with realistic roles.
- Sync the front-end brochure pages with backend responses.
- Tests: pass `app/tests/test_brochure_*`, `test_brochure_generation.py`, `test_brochure_simple.py`.
- Update `final_audit/brochure.md`; log fixes in `final_audit/fix/brochure.md`.

_Verification checkpoint (2025-10-25)_:
- `python -m pytest app/tests/test_brochure_routes.py` ✅ routes, templates, and render/download flow covered by FastAPI test client.
- `python -m pytest test_brochure_generation.py test_brochure_simple.py` ❌ fails because SQLAlchemy cannot resolve `TeamPerformance` when importing `EnhancedProperty` and because `_detect_content_type` never returns `PROPERTY_BROCHURE`.
- `python test_brochure_acceptance.py` ❌ fails early: SQLite lacks the `enhanced_properties` table, `AIContentGenerator.generate_content` signature changed (no `user_id` kwarg), and fixture payloads miss `listing_id/price/location/description`.
- `python dev_data/load.py` ❌ cannot create tables because `audit_logs.contact_id` points at a `clients` table that is never imported into `models.Base`.
- `node test_brochure.js` ❌ intent parsing succeeds but orchestration aborts once `src/services/http.ts` reads `import.meta.env` (no Vite runtime when running under Node).

### Phase 2 – Marketing Automation (Templates & Campaigns)
- Add local `MockMarketingEngine` and `MockTaskOrchestrator` for dev mode.
- Seed/migrate marketing tables (templates, campaigns, assets, approval workflow).
- Ensure responses match front-end expectations.
- Tests: cover `/api/v1/marketing/templates`, `/campaigns`, `/campaigns/full-package`.
- Document resolutions in `final_audit/marketing.md` and `final_audit/fix/marketing.md`.

### Phase 3 – CMA & Market Insights
- Seed comparable sales/property data; enable mock trend/forecast output when AI is unavailable.
- Standardize response payloads for `/api/v1/cma/reports`, `/valuation/quick`, `/market/snapshot`.
- Tests: extend coverage; ensure integration tests return 200.
- Update `final_audit/cma.md` and `final_audit/fix/cma.md`.

### Phase 4 – Social Media & Analytics
- Seed social templates/campaigns; stub AI content for captions/hashtags.
- Seed analytics dashboard data or provide JSON stubs; add in-process cache fallback.
- Sync front-end dashboards with mocked data.
- Tests: social router and analytics tests pass.
- Update `final_audit/social.md`, `final_audit/analytics.md`, and related fix logs.

### Phase 5 – Workflows & Task Orchestration
- Seed workflow/package tables; create synchronous mock orchestrator with SSE playback.
- Ensure `/api/v1/workflows` and `/api/v1/orchestration` simulate status transitions.
- Tests: `tests/test_aura_integration.py::TestWorkflowsRouter` and SSE suites.
- Document in `final_audit/workflows.md` and `final_audit/fix/workflows.md`.

### Phase 6 – Contacts & Status Endpoints
- Seed `EnhancedClient`, `ContactNote`, `ContactActivity`, `FollowUp` data.
- Update `/readyz` to leverage new mocks/seeds for healthy status.
- Tests: `tests/test_contacts_api.py` and `tests/test_status_endpoints.py`.
- Update `final_audit/auth.md` (RBAC exercised) and create `final_audit/fix/auth.md`.

### Phase 7 – Full Suite & Documentation
- Run full `pytest`; resolve remaining warnings/errors.
- Update each `final_audit/*.md` with “problem / fix / seeding instructions”.
- Maintain per-feature changelog in `final_audit/fix/`.
- Summarize dev workflow in `final_audit/README.md` (seed script, mock toggles, test commands).

### Ongoing Maintenance
- Add CI hook or dev script to seed (`python dev_data/load.py`) before tests.
- Keep mocks behind explicit dev flags.
- Append entries to `final_audit/fix/` whenever features change.
