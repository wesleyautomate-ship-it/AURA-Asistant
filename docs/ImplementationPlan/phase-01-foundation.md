# Phase 01 — Foundation (Historical Reference)

> Archived note: The milestones below capture the original foundation plan. The current state and guidance live in `docs/PROPERTYPRO_AI_ROADMAP.md` and `docs/handbook/backend.md`.

Scope: Establish secure, scalable fundamentals to support subsequent feature work.

## Objectives
- Authentication and session lifecycle (JWT access + refresh).
- Baseline domain entities (User, Role, Permission, UserSession).
- Initial infrastructure: DB (PostgreSQL), migrations (Alembic), settings/env, CORS, logging.
- Health, readiness, and basic monitoring endpoints.

## Deliverables
- FastAPI app skeleton under `backend/app/` with clean architecture layers.
- Alembic migrations for auth and RBAC tables.
- `.env` and `app/core/settings.py` without hard-coded secrets.
- API versioning under `/api/v1`.
- Mobile app (Expo) baseline screens + API client wiring (no protected data yet).

## Data Model (Initial)
- `User(id, email, password_hash, first_name, last_name, role, is_active, created_at, updated_at)`
- `UserSession(id, user_id, session_token, refresh_token, ip_address, user_agent, expires_at, is_active)`
- `Role(id, name, is_default)` M:N `Permission`
- `Permission(id, name, resource, action)`

## APIs
- `POST /api/v1/auth/login` â†’ access + refresh
- `POST /api/v1/auth/refresh` â†’ new access
- `GET /api/v1/health` â†’ liveness/readiness

## Non-Functional
- Rate limiting defaults.
- Structured logging + request IDs.
- Basic error handling and consistent error envelope.

## Acceptance Criteria
- Login flow returns valid JWTs and enforces password hash (bcrypt) verification.
- Protected routes reject missing/invalid tokens; accept valid ones.
- Migrations can bootstrap a fresh DB end-to-end.
- Mobile app can authenticate and store tokens securely (local secure storage).

## Risks & Mitigations
- Password resets and email verification: design but defer mailer integration to Phase 2.
- Secrets handling in local dev: `.env` + `.env.example` and `env_loader` verified.

## Milestones
- M1: DB + migrations + settings in place.
- M2: Auth endpoints + tests.
- M3: Mobile login UI + API integration.

---

## Detailed Implementation Plan

### 1) Repository Consolidation (Backend)
- Make `backend/app/` the canonical backend. Ensure `app/main.py` only mounts `/api/v1` routers.
- Archive/retire duplicate root-level routers under `backend/` that overlap with `app/api/v1/`.

### 2) Environment & Settings
- Ensure `.env` supports: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_REFRESH_TOKEN_EXPIRE_DAYS`, `BCRYPT_ROUNDS`, `OPENAI_API_KEY` (future use).
- In `backend/app/core/settings.py`:
  - Confirm `PORT=8000` (done).
  - Remove any hard-coded API keys and dev bypass.
  - CORS: allow localhost in dev; restrict in staging/prod.

### 3) Database & Alembic
- Add Alembic to `backend/app` with a clear migration path.
- Create baseline and Phase 01 migration for:
  - `users`, `user_sessions`, `roles`, `permissions`, `user_roles`, `role_permissions`, `audit_logs` (optional in Phase 1, recommended).
- Indices:
  - `users.email (unique)`, `user_sessions.session_token (unique)`, `user_sessions.refresh_token (unique)`.
- Remove any production calls to `Base.metadata.create_all()`; use Alembic exclusively.

### 4) Data Model (Phase 01)
- `User(id, email, password_hash, first_name, last_name, role, is_active, email_verified, created_at, updated_at)`
- `UserSession(id, user_id, session_token, refresh_token, ip_address, user_agent, expires_at, is_active, created_at, last_used)`
- `Role(id, name, description, is_default, created_at, updated_at)` â†” `Permission(id, name, resource, action, description, created_at)` (M:N)
- Optional: `AuditLog(id, user_id, event_type, event_data, ip_address, user_agent, success, error_message, created_at)`

### 5) API Surface (Phase 01)
- Base path: `/api/v1`
- Auth
  - `POST /auth/login`
  - `POST /auth/refresh`
- Health
  - `GET /health` (liveness + optional readiness details)

### 6) DTOs (Request/Response Schemas)

Auth
```json
// POST /api/v1/auth/login (request)
{
  "email": "agent@example.com",
  "password": "Secret123!"
}

// 200 OK (response)
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "agent@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "agent"
  }
}

// POST /api/v1/auth/refresh (request)
{
  "refresh_token": "<jwt>"
}

// 200 OK (response)
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Health
```json
// GET /api/v1/health (response)
{
  "status": "ok",
  "version": "v1",
  "uptime_seconds": 12345,
  "dependencies": {
    "database": "ok"
  }
}
```

### 7) Security & Policies
- Passwords: hash with bcrypt (`BCRYPT_ROUNDS` from env).
- JWT: HS256 with `SECRET_KEY`; access token 30 minutes, refresh 7 days (from env).
- Token storage: sessions table stores refresh token + session token metadata (IP, UA, expiry).
- Rate limiting: apply per-IP and per-user sensible defaults on auth endpoints.
- Error envelope: consistent JSON errors `{ "error": { "code": "...", "message": "..." } }`.
- Logging: structured logs with correlation IDs; log auth successes/failures to `AuditLog` (if enabled).

### 8) Validation Rules
- Email must be unique and syntactically valid.
- Password minimum length 8; enforce complexity policy via validation.
- Deny login if user is inactive or locked.

### 9) Acceptance Tests (Phase 01)
- Auth
  - Successful login returns access+refresh and user profile.
  - Invalid password â†’ 401 with standard error envelope.
  - Inactive user â†’ 403.
  - Refresh with valid refresh token returns new access token.
  - Refresh with invalid/expired token â†’ 401.
- Health
  - `/api/v1/health` returns `status=ok` when DB reachable.
  - Returns `status=degraded` if DB ping fails (optional readiness logic).
- Migrations
  - `alembic upgrade head` on a clean DB succeeds; indices and FKs exist.

### 10) Task Breakdown (Milestone A)
- Backend consolidation to `backend/app/`; retire legacy routers.
- Configure Alembic; create baseline + Phase 01 migration; remove `create_all` from runtime.
- Implement `/api/v1/health` with DB ping and version info.
- Implement `/api/v1/auth/login`:
  - Validate credentials, bcrypt check, issue tokens, persist session metadata, emit audit log.
- Implement `/api/v1/auth/refresh`:
  - Validate refresh token, issue new access token, update session last_used.
- Add request logging middleware and consistent error handler.

### 11) Deliverables Checklist
- [ ] Alembic configured with baseline and Phase 01 migration committed.
- [ ] Auth endpoints implemented with unit/integration tests.
- [ ] Health endpoint implemented and documented.
- [ ] `.env.example` updated; `.env` used locally; no hard-coded secrets.
- [ ] Logging, error envelopes, and basic rate limits in place.

---

## References to Spec
- Target Tech Spec sections: 1.2 (System Overview), 2.2.1 (User Authentication), 5.x (Security, API, Monitoring)
- Contracts also reflected in `docs/ImplementationPlan/api-contracts-v1.md`
