# Security Posture

## Authentication & Authorization

- JWT auth with RBAC models is defined but many routes (contacts, follow-ups, export) do not enforce dependencies, so requests succeed without tokens (`backend/app/api/v1/contacts_router.py:63`, `backend/app/api/v1/export_router.py:119`).
- Development bypass toggles allow automatic token issuance whenever `ENVIRONMENT` is not `production` or `DISABLE_AUTH` is true (`backend/app/core/dev_auth_bypass.py:32`). Harden by:
  - Failing fast if bypass detected outside localhost.
  - Logging explicit warnings and requiring `DEV_AUTH_ALLOW=1` for opt-in.

## CORS & Transport

- Development CORS allows wildcards such as `http://*.ngrok.io` (`backend/app/core/settings.py:51`). Restrict to known domains per environment and enforce HTTPS in staging/prod.
- Add middleware to redirect HTTP to HTTPS when `IS_PRODUCTION`.

## Secrets Handling

- `.env` is present in repo; ensure production secrets are injected via environment or secret manager. Remove defaults for `SECRET_KEY`, `GOOGLE_API_KEY` in production builds.
- Recommend `dotenv` usage only in dev and fail startup when critical secrets missing (currently prints warning with mojibake at `backend/app/core/settings.py:36`).

## File Upload & Download

- `FileStorageService` writes directly to disk and exposes files via static `/uploads` mount without auth (`backend/app/domain/ai/file_storage_service.py:60`, `backend/app/main.py:521`). Introduce:
  - Signed URLs with expiry.
  - MIME validation and size enforcement (already in settings but not applied before writes).
  - Background cleanup for orphaned files.
- Export endpoints accept arbitrary HTML and publish it verbatim (`backend/app/api/v1/export_router.py:119`). Sanitize inputs or move to PDF-only pipeline.

## Data Protection

- PII (emails, phone numbers) returned without redaction. Ensure role-based scopes (agent vs admin) filter data.
- Add encryption-at-rest for sensitive documents if stored long term.

## Dependency Risk

- Python stack includes large ML libraries prone to CVEs; pin and separate extras (`backend/requirements.txt:17`).
- Frontend uses React 19 RC and lucide bleeding-edge versions (`aura-client/package.json:18`); monitor for security patches.
- Add `pip-audit` and `npm audit --production` to CI (see `docs/CI_PIPELINE.md`).

## Logging & Audit

- Request logging provides request IDs but sensitive data may leak into logs via debug prints (e.g., `print` statements in models). Use structured logger with redaction.
- Ensure every brochure/CMA/follow-up action writes to `AuditLog` table for compliance (`backend/app/core/models.py:159`).

## Recommended Actions

1. Enforce auth dependencies on all business-critical routes; add integration tests that require valid tokens.
2. Replace public `/uploads` with object storage + signed URLs and scrub the current directory.
3. Restrict CORS per environment and require HTTPS for production origins.
4. Introduce automated dependency/secret scanning in CI.
5. Instrument audit logging with request IDs for all CRM mutations.
