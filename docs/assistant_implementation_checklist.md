# Implementation Checklist

- [x] Implement login screen + route guard in `client/apps/web/App.tsx`
- [x] Persist auth token/profile via `useUserStore` on successful `/api/v1/auth/login`
- [x] Refactor `@propertypro/services/api.ts` to expose GET/POST/PUT/PATCH/DELETE helpers with shared error handling
- [x] Update property/client/transaction stores to use new helpers and correct `/api/v1/...` endpoints
- [x] Ensure property create/update/delete flows refresh UI and handle errors gracefully
- [x] Wire Marketing view to fetch templates and trigger `POST /api/v1/marketing/campaigns/full-package`
- [x] Provide sample-property bootstrap when backend inventory is empty
- [ ] Smoke test login -> property CRUD -> marketing package path and record results
