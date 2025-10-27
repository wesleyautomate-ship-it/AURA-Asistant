## Analytics & Reporting — Audit

### 1. Data Sources
- `/api/v1/analytics/*` endpoints query `performance_metrics`, `campaign_stats`, etc., which are absent in the dev SQLite file. Every request returns 500 (“no such table”).

**Action**: Introduce migrations/seeds for analytics summary tables or switch to mock JSON responses in dev mode.

### 2. Caching/Redis Dependence
- Routers use `cache_manager` to memoize results. With Redis unavailable the manager logs warnings and falls back to DB queries, but repeated requests still attempt to connect, slowing tests.

**Action**: Provide a no-op cache backend in dev that stores data in-process instead of hitting Redis each time.

### 3. Front-End Expectations
- Dashboards expect normalized metrics (`totalCampaigns`, `conversionRate`). Returned payloads contain raw SQL rows. The Vue store reshapes them, but when the response is `{ "detail": "Service unavailable" }`, the UI ends up blank.

**Action**: Define stable DTOs on the backend and ensure dev mode returns sample metrics.

### 4. Auth Scopes
- Analytics endpoints require admin access, but dev bypass doesn’t include `roles=["admin"]`, so most requests fail 403 when bypass is off.

