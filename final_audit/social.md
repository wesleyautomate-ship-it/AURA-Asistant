## Social Media Automation — Audit

### 1. AI Dependency
- `social_media_router` relies on `ai_manager.generate_social_post` and `AITaskOrchestrator`. Without Gemini/Redis, the router raises 503 through `register_ai_router`.

**Action**: Provide a synchronous mock generator (prebuilt captions/hashtags) when AI is disabled, and keep the endpoints registered.

### 2. Template/Platform Data
- Router expects `social_templates` / `social_campaigns` tables for persistence, but migrations/seeds are missing. Calls to `/api/v1/social/campaigns` fail with SQL errors.

**Action**: Add migrations & seeds for social templates/campaigns (or store campaigns in memory for dev).

### 3. Front-End Contract
- UI expects the response to include `campaign_id`, `status`, `scheduled_posts`, etc. Current router returns raw orchestrator responses or `None`, causing the client to break.

**Action**: Define a deterministic response schema and update both router and store accordingly.

### 4. RBAC/Audit
- Endpoints are guarded by `require_roles(["agent"])`. The dev bypass should set `roles=["agent"]` to mimic real behavior and ensure analytics logging is exercised.

