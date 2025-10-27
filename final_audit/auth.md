## Auth Flow — Gaps Identified

1. **JWT Runtime Errors** – `auth.middleware` still imports `jwt.JWTError`, but PyJWT ≥2.9 exposes exceptions under `jwt.exceptions`. On a fresh environment this raises `AttributeError`, returning 401 even when dependency overrides inject a user.  
   *Fix*: switch to `from jwt import exceptions as jwt_exceptions` and catch `jwt_exceptions.PyJWTError`.

2. **SQLite Test Setup** – `pytest` fixtures create only `users`, `user_sessions`, and `audit_logs`, but other auth paths (e.g., audit logging or MFA) rely on additional tables and seed data that aren’t present. Devs can log in with the seeded user, yet features like rate limiting or session revocation aren’t exercised.  
   *Fix*: provide a portable seed script (or fixture) that builds the full auth schema and inserts representative roles/permissions.

3. **Password Hashing Consistency** – The seeded password in `test_auth.py` uses `hash_password`, but the front-end login flow still expects to post credentials to `/api/v1/auth/login`. Without a migration/seed path that inserts hashed passwords into the real database, manual testing fails.  
   *Fix*: include a CLI/management command to create dev users with properly hashed passwords.

4. **Dev Bypass Lifecycle** – `DEV_AUTH_BYPASS` code path returns a fabricated user but skips permission checks. Several routers (marketing/social/CMA) expect role-specific access. In bypass mode those checks are silently skipped, masking authorization bugs.  
   *Fix*: have the fake user include realistic roles/scopes, and log when protected endpoints are reached via the bypass.

5. **Frontend Token Storage** – `aura-client/src/store/authStore.ts` still assumes a JWT + refresh flow, but we do not seed refresh tokens or expose `/auth/refresh` locally. When the browser refreshes, the user is logged out.  
   *Fix*: either seed a long-lived static access token for dev or expose a deterministic refresh implementation in the backend.
