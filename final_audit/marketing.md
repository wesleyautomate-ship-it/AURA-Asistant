## Marketing Automation — Audit

### 1. API Availability
- `/api/v1/marketing/templates` is registered via `register_ai_router`. When `AI_FEATURES_ENABLED` is false (missing Gemini key), the router is replaced with a 503 stub—manual testing hits an error page.

**Action**: Allow marketing endpoints to run in mock mode even when AI is disabled, by falling back to dev stubs instead of the 503 router.

### 2. Seed Data
- No default templates exist in SQLite. `MarketingCampaignEngine.get_available_templates` executes SQL against `marketing_templates`, which is empty and requires Postgres features (JSON columns). Tests currently stub the engine; real responses return 422 due to validation failing on `[]`.

**Action**: Provide a migration + seed for canonical templates (postcard, email, social) using SQLite-compatible JSON (text stored as JSON).

### 3. Campaign Persistence
- The engine writes to `marketing_campaigns`, `marketing_assets`, etc., but migrations for those tables are absent in the repo. The router catches integrity errors and returns 500. Front-end attempts to render campaigns but receives errors.

**Action**: Reintroduce the marketing migrations or define new SQLAlchemy models + migrations for campaigns/assets/approval workflow.

### 4. Background Task Execution
- `generate_campaign_assets` expects an async task runner with file storage. In dev this raises due to missing storage directories and AI results.

**Action**: Short-circuit asset generation in dev (store placeholder URLs), and ensure `/uploads` is writable (maybe seed placeholder PDFs/images).

### 5. RBAC & Auth
- Marketing endpoints require authenticated agents/admin. With dev bypass lacking scopes, RBAC is untested. UI relies on `marketing/templates` to populate drop-downs even before login, leading to 401 loops.

**Action**: Mirror production scopes in the bypass user, or expose a read-only templates endpoint that doesn’t require auth for dev usage.
