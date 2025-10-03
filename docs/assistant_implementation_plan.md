# Assistant Implementation Plan (Beta Hardening)

## Objectives
- Restore end-to-end authentication so workspace apps can talk to FastAPI securely
- Replace stubbed marketing flows with real AURA endpoints to demonstrate AI value
- Align shared services/stores with backend contracts to prevent 4xx regressions
- Enable reliable smoke validation (API + UI) through Docker so the team can certify builds quickly

## Completed Foundations
1. **Authentication bridge**
   - Login surface in `client/apps/web` now authenticates against `/api/v1/auth/login`
   - JWT + profile persisted via `useUserStore`; UI shell gated until a session exists
   - Command center and property/client fetches only initialize when authenticated
2. **Shared API client hardening**
   - `@propertypro/services/api.ts` exposes typed GET/POST/PUT/PATCH/DELETE helpers with unified error handling and auth header injection
   - `_method` hacks removed; 401 responses trigger a local logout for graceful recovery
3. **Store + feature alignment**
   - Property, client, and transaction stores now speak the canonical `/api/v1/...` endpoints, normalize payloads, and refresh UI state on each mutation
   - Property form collects backend-required description/location/property type fields so creates succeed without manual patching
4. **Marketing workflow integration**
   - Dedicated marketing service fetches live templates and triggers `POST /api/v1/marketing/campaigns/full-package`
   - Marketing view surfaces template selection, package results, and auto-seeds a demo listing when inventory is empty

## Outstanding Work
1. **Dockerized end-to-end environment**
   - Resolve frontend image build for monorepo (`@propertypro/*` packages not available inside standalone app build)
   - Expose workspace packages during Docker build (copy `client/packages` and install via workspaces or prebundle shared libs)
   - Re-run `docker compose -f docker-compose.smoke.yml up` to confirm API + frontend come up cleanly
2. **Smoke flow execution**
   - Once containers are healthy: exercise login ? property CRUD ? marketing package path via UI/API
   - Capture API and frontend logs for the run; document any discrepancies (e.g., missing seed data)
3. **Automated visual regression**
   - With frontend containerized, run Playwright against the containerized host (`http://frontend:80`) using `playwright.docker.config.ts`
   - Archive HTML report + screenshots for stakeholders
4. **Workspace relocation** (after moving out of OneDrive)
   - Rebuild Docker images to avoid Windows permission artifacts (`?rw-rw-rw-` warnings)
   - Regenerate `node_modules` outside of cloud-sync folders to keep builds deterministic
5. **Future enhancements**
   - Add health-check scripts to seed baseline data (admin + sample listing) automatically in Docker
   - Extend transaction store once backend milestone endpoints land

## Validation Plan
- Local `npm run build` (completed)
- Containerized build + smoke flow (blocked until Docker workspace fix lands)
- Playwright visual suite (queued after container success)

## Dependencies & Risks
- Workspace packages must be present during Docker build; otherwise Vite cannot resolve `@propertypro/*`
- Running from OneDrive introduces non-POSIX permissions causing tar errors; relocating to a local path is recommended before the next attempt
- Backend relies on environment keys; placeholder values (`dummy-key`) are acceptable for the smoke run but real keys are required for AI features
