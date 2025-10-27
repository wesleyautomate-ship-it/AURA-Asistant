# Dev Auth Bypass (local only)

Use this guard rail to debug auth flows without a full login. It only works when the backend is running in a local development environment **and** you explicitly opt in.

## Enable locally
- Backend: `ENV=development DEV_AUTH_BYPASS=true uvicorn backend.app.main:app --reload`
- Frontend: create or update `aura-client/.env.local` with `VITE_DEV_AUTH_BYPASS=true`, then run `pnpm dev`
- Hit `http://localhost:8000/_dev/whoami` (no auth header) to confirm you receive the fake user payload and see the `DEV AUTH BYPASS ENABLED — ...` warning in the API logs

## Disable / normal behaviour
- Stop exporting `DEV_AUTH_BYPASS` or set it to `false`; the backend will go back to requiring real tokens
- Remove `VITE_DEV_AUTH_BYPASS` (or set to `false`) and the SPA will redirect unauthenticated sessions to `/login` again

## Remove when finished
- Delete the DEV_AUTH_BYPASS checks (`maybe_get_dev_user` usage and the `/ _dev/whoami` route)
- Drop the `VITE_DEV_AUTH_BYPASS` guard in `aura-client/src/services/http.ts`
- Clean up any local env files you added

This feature is dev-only. Do **not** ship with the bypass enabled.
