# Target Architecture Blueprint

## Component Responsibilities

| Component | Responsibilities | Notes |
| --- | --- | --- |
| **Web Client (Vite/React)** | Intent capture, plan + status visualisation, document previews, accessible controls, offline drafts | Use TanStack Query + SSE for long-running tasks; keep business logic thin. |
| **Gateway (FastAPI)** | HTTP/JSON API, SSE streaming, auth/RBAC enforcement, request logging, orchestration hand-off | Split routers by domain (`contacts`, `brochures`, `cma`), share DI dependencies. |
| **Task Orchestrator** | Plan execution graph, manage background jobs, idempotent retries, status updates | Backed by Redis/Queue; publishes updates over channels consumed by SSE. |
| **Domain Services** | CRM service (contacts/follow-ups), Documents (brochure/CMA), Intelligence (AI calls), Timeline service | Expose service interfaces with transactions + telemetry. |
| **Storage Layer** | Postgres (CRM, audit, workflow), Object store (PDF/HTML), Vector index (optional) | Use SQLAlchemy models and Alembic migrations; signed URLs via object store. |
| **Observability Stack** | Prometheus metrics, structured logs, audit logs, tracing | Provide dashboards for SLA (p95 latency), job backlog, failure rates. |

## API Matrix (Target vs Current)

| Domain | Endpoint (Target) | Current Status | Action |
| --- | --- | --- | --- |
| Contacts | `GET /api/v1/contacts?limit&offset&search` | Exists but falls back to mock | Enforce DB response, add filters |
| Contacts | `PATCH /api/v1/contacts/{id}` | Missing | Implement note/tag updates |
| Activities | `GET /api/v1/contacts/{id}/activity` | Exists with fallback | Remove mock path, expand pagination |
| Follow-ups | `POST /api/v1/followups` | Exists, mock fallback | Require auth, persist status |
| Brochures | `POST /api/v1/brochures` | Exists | Validate template, return job id |
| Brochures | `POST /api/v1/brochures/{id}/render` | Inline render | Move to async job + polling |
| Templates | `GET /api/v1/templates` | Empty without seed | Seed defaults + caching |
| CMA | `POST /api/v1/cma/reports` | Stub only | Wire to orchestrator job |
| CMA | `GET /api/v1/cma/reports/{taskId}/status` | Returns placeholder | Connect to job store |
| Export | `POST /api/v1/export/html-save` | No auth | Require signed auth + validation |
| Health | `/health`, `/healthz`, `/version` | Present | Add `/metrics`, `/status` |

## Data Model Targets

- **contacts** table replacing legacy `clients` naming; columns for `temperature`, `intent_score`, `last_activity_at`, indexes on `(last_activity_at DESC)`.
- **contact_notes** and **activities** to include `created_by`, `request_id` for traceability (`backend/app/domain/listings/enhanced_real_estate_models.py:260`).
- **followups** add status, outcome, and unique constraint `(contact_id, due_at, channel)` to prevent duplicates.
- **brochure_templates / brochure_drafts** link to `contacts` for attribution; store render job id + checksum of content.
- **comps** table required for CMA: `{id, property_id, source, price, sqft, sold_at, adjustments}` with indexes on `(property_id, sold_at)` and `(area, property_type)`.
- **audit_logs** must capture event_type `brochure.render`, `cma.generate`, `followup.create` referencing request IDs (`backend/app/core/models.py:159`).

## Contracts & SLAs

- **Contacts read**: p95 < 300 ms under 100k rows; stale tolerance 1 minute; pagination required.
- **Brochure render**: Queue job start < 5 s, completion within 2 minutes; retry on failure with exponential backoff; notify UI via SSE.
- **CMA report**: Async job with SLA 5 minutes; partial status updates at each sub-step (comps fetch, valuation, doc render).
- **Export downloads**: Signed URL expiry ≤ 24 hours; ability to revoke from admin UI.
- **Availability**: `/healthz` 99.9%; include dependency checks (DB, Redis, object store).

## Integration Expectations

- **AI Providers**: Wrap Gemini/OpenAI clients with timeout (10 s) + circuit breaker; mockable interface for testing.
- **External MLS**: Use background sync jobs to refresh comps nightly; fallback to last known comps.
- **Notifications**: Provide hook service (email/SMS) via queue; ensure data residency compliance.
- **Frontend Config**: Ship environment contract (`VITE_API_BASE_URL`, `VITE_USE_REAL_API`, `VITE_AURA_MOCK_MODE`) documented in runbook; default to real API in staging/prod.
