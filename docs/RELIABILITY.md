# Reliability Notes

## Health & Telemetry

- `GET /health` reports static metadata but does not verify dependent services (DB, Redis, object store) (`backend/app/main.py:559`). Extend to include connectivity checks and surface build SHA.
- `GET /healthz` is lightweight and suitable for Kubernetes liveness; add `/readyz` for readiness once DB migrations applied.
- No `/metrics` endpoint exposed; add Prometheus exporter (Starlette middleware or `prometheus-fastapi-instrumentator`).

## Logging & Monitoring

- `RequestLoggingMiddleware` adds structured entries with request IDs (`backend/app/core/middleware.py:69`), but logs currently go to stdout. Ship logs to central sink with JSON format.
- Audit events are defined but not emitted for key workflows (contact mutations, brochure renders). Add dependency that writes to `AuditLog`.
- Add tracing for orchestrated jobs (brochure render, CMA generation) with job IDs tied back to request IDs.

## Background Processing

- Long-running operations (PDF render, CMA analysis) execute inline. Introduce job queue (Celery/RQ) with:
  - Visibility timeout handling.
  - Retry policies (e.g., 3 attempts with exponential backoff).
  - Dead-letter logging on failure.
- SSE/WS updates should publish job progress, not final state only.

## Resilience Patterns

- Wrap external service calls (Gemini, MLS) with timeouts and `tenacity` retries; provide circuit breaker to protect orchestrator.
- Add database connection retries with exponential backoff during startup.
- Rate limiter exists but not applied to sensitive endpoints; enforce to prevent abuse.

## Disaster Recovery

- Plan nightly backups for Postgres (dump + WAL) and object store snapshots for deliverables.
- Validate ability to rebuild search/vector indexes from source data.
- Document runbooks for failed render queue, stuck jobs, or corrupted uploads.

## Alerts

- Set alerts for:
  - 5xx rate > 1% on critical endpoints.
  - Brochure/CMA job failure rate > 5% over 15 m.
  - Queue delay exceeding SLA thresholds.
  - Disk usage for uploads > 80%.
