# Performance Assessment

## Current Observations

- Backend endpoints execute synchronous DB queries and synchronous PDF renders; no worker pool isolates CPU-heavy tasks (`backend/app/api/v1/brochures_router.py:133`).
- Contacts list executes two sequential DB queries (contacts + activities) per request and falls back to Python loops; consider window functions and pagination.
- CMA workflow runs raw SQL and data crunching on the request thread; move heavy work to background orchestrator.
- Frontend fetches data without caching or background refresh when API enabled; leverage React Query with stale-time hints.

## Baseline Targets

| Flow | Target p95 | Notes |
| --- | --- | --- |
| Contacts list (`GET /contacts`) | < 300 ms | Index on `last_activity_at`; avoid fallback loops |
| Contact detail (`GET /contacts/{id}`) | < 400 ms | Batch load notes + activity | 
| Brochure render (async job) | < 120 s | Queue job; return immediate 202 + status polling |
| CMA report generation | < 300 s | Multi-step job with progress updates |
| Frontend Largest Contentful Paint | < 2.5 s | Preload hero assets; tree-shake unused code |

## Recommended Tooling

- **k6 smoke suites** (generated in `perf/k6/`) covering contacts, brochure draft/render, and CMA job submission.
- **Lighthouse** via `scripts/lighthouse.mjs` against built UI to capture LCP, TTI, and accessibility regressions.
- **Database**: Enable `EXPLAIN ANALYZE` for CMA queries, add indexes on `followups.due_at`, `activities.occurred_at`, `brochure_drafts.created_at`.
- **Caching**: Introduce Redis caching for template lists and frequently accessed contact summaries.
- **Streaming**: Add SSE heartbeats to avoid idle timeouts and measure drift.

## Known Bottlenecks

1. **Synchronous rendering** – PDF creation blocks request thread; convert to worker (Celery/RQ) and push SSE updates.
2. **Mock fallback** – By skipping DB when errors occur we lose ability to profile real queries; remove fallback to surface performance issues earlier.
3. **Unbounded file writes** – Disk operations not rate-limited; consider async file IO or object storage commit.

## Next Steps

1. Deploy k6 scripts against staging DB snapshot; record baseline p95/p99 and note slow queries.
2. Add OpenTelemetry metrics for request latency, job durations, queue depth, and memory usage.
3. Configure Lighthouse CI (headless Chrome) to track LCP/FID; budget fail if > 2.5 s.
