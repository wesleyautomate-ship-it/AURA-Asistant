## CMA Reports — Audit

### 1. Missing Comparable Data
- `app/api/v1/cma_reports_router.py` queries comparables via `marketing_campaigns`/`EnhancedProperty` join logic, but no sample comparables exist in the dev DB. The router catches `SQLAlchemyError` and returns 500, so front-end CMA flows display “Service unavailable.”

**Action**: Seed a minimal set of comparable listings with sale dates, prices, and amenities covering multiple property types.

### 2. AI Task Orchestrator Coupling
- CMA endpoints enqueue tasks with `AITaskOrchestrator.submit_intelligence_task`. Without Redis/worker infrastructure, the call raises `ConnectionRefusedError`. Current try/except only logs the error and returns 500.

**Action**: Introduce a dev stub orchestrator (similar to marketing) that returns canned CMA analysis synchronously or store the job in SQLite for polling.

### 3. Forecasting/Trends
- `include_market_trends` and `include_forecasting` flags assume data in `market_trends` tables, but the models are commented out. The router silently skips those sections, leading to incomplete reports.

**Action**: Either fully revive the `market_trends` tables (with migrations/seeds) or hide the flags in the UI when data is unavailable.

### 4. Auth Flow
- CMA endpoints require agent/admin roles via `require_roles(["agent", "admin"])`, yet the dev bypass returns a user without roles. Tests currently patch `get_current_user`, masking RBAC violations.

**Action**: Align dev bypass with production RBAC and add integration tests asserting 403 for unauthorized users.

### 5. Front-End Expectations
- The front-end expects `/api/v1/cma/reports` to return a `report_id` plus `status` so it can stream updates. Present implementation returns the raw orchestrator payload, which is `None` when the orchestrator fails—leading to `TypeError` in the UI.

**Action**: Standardize the response contract (queue ID + immediate summary) and update the store to display offline data when AI is disabled.
