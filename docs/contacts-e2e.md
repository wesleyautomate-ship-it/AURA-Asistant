Contacts E2E Integration Checklist

- [x] Routes added & included in `backend/app/main.py`
- [x] Real API client + env flag in `aura-client/src/services/http.ts`
- [x] `contactsApi.ts`, `aiClient.ts`, `schedulesApi.ts` gated to real API
- [x] Loading/empty/error states added to AI cards
- [x] Activity refresh on create follow-up
- [ ] Smoke test passed with real backend
- [x] Mock mode still works when re-enabled

Notes

- Backend uses simple in-memory stores for contacts, activity, and follow-ups. Replace with DB later.
- Endpoints exposed at: `/contacts`, `/contacts/{id}`, `/contacts/{id}/activity`, `/followups`, and `/ai/*`.
- Frontend prefers real API when `VITE_USE_REAL_API=true`; otherwise falls back to existing mocks/localStorage.

