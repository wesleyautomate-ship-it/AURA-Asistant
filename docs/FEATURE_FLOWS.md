# Feature Flows (A–Z)

## Contacts

| Step | Current Implementation | Gaps / Notes | Status |
| --- | --- | --- | --- |
| Intake | `/contacts` list fetch with abort + loading states (`aura-client/src/pages/Contacts.tsx:13`) | API uses mock data until `VITE_USE_REAL_API` set; no search params passed to backend | Partial |
| Orchestration | Contact detail loads info + follow-ups in parallel (`aura-client/src/pages/contacts/[id].tsx:41`) | No retry/backoff; optimistic timeline inserts only mutate local state | Partial |
| Tools & Data | Backend queries `EnhancedClient` + `ContactActivity` (`backend/app/api/v1/contacts_router.py:120`) | Broad exception fallback to in-memory store hides DB issues | Fail |
| Notes | Notes editor exists but `saveNotes` stub writes nowhere (`aura-client/src/services/contactsApi.ts:60`) | Needs real PATCH endpoint + audit logging | Fail |
| Follow-ups | Creation calls schedules API; backend maps to ORM (`backend/app/api/v1/followups_router.py:97`) | API fallback to in-memory list; UI stores follow-ups in localStorage (`aura-client/src/services/schedulesApi.ts:31`) | Fail |
| AI Assist | AI action bar triggers summarise/follow-up mocks (`aura-client/src/pages/contacts/[id].tsx:90`) | No backend `/ai/...` routes wired; no streaming updates | Fail |
| UI Rendering | Loading/empty/error states implemented (`aura-client/src/pages/Contacts.tsx:25`) | Timeline shows mojibake glyphs (`aura-client/src/components/Dashboard/Contacts/ContactsWorkspaceV2.tsx:88`) | Partial |
| History & Traces | Local timeline displayed, but no backend audit | Missing `AuditLog` writes and timeline persistence | Fail |

## Brochure Generation

| Step | Current Implementation | Gaps / Notes | Status |
| --- | --- | --- | --- |
| Intake | Template selection fetches `/api/v1/templates` when enabled (`aura-client/src/pages/ai-workflow/brochure.tsx:15`) | Templates table often empty; env flag off by default | Partial |
| Draft Create | POST `/api/v1/brochures` seeds default data (`backend/app/api/v1/brochures_router.py:56`) | No auth/validation on template keys | Partial |
| Editing | `useBrochureDraft` autosaves with debounce (`aura-client/src/features/brochure/hooks/useBrochureDraft.ts:10`) | Failed saves silently swallow errors; no offline queue | Partial |
| Data Merge | Service maps JSON to UI model (`aura-client/src/services/brochureDrafts.ts:9`) | Does not sync listing metadata or agent info | Partial |
| Render | Render endpoint writes PDF + download URL (`backend/app/api/v1/brochures_router.py:133`) | Errors corrupt draft meta when `row.data` is `None`; synchronous render blocks | Fail |
| Storage | Files saved to `/uploads/deliverables` (`backend/app/domain/ai/file_storage_service.py:88`) | Public without signing; no retention policy | Fail |
| UI Output | Editor shows toast on save + status banner | No download button until manual refresh; no history entry | Partial |
| History & Audit | Intended to attach to contact timeline | No timeline integration or audit record created | Fail |

## CME/CMA

| Step | Current Implementation | Gaps / Notes | Status |
| --- | --- | --- | --- |
| Intake | CMA wizard UI with template selection (`aura-client/src/pages/ai-workflow/cma.tsx:7`) | "Use Template" routes to `/requests` without creating task | Fail |
| Planning | Backend orchestrator stub constructs quick valuation (`backend/app/api/v1/cma_reports_router.py:197`) | Depends on raw SQL, no error surfacing when comps missing | Fail |
| Data Retrieval | Queries `properties` for comps via SQL text (`backend/app/api/v1/cma_reports_router.py:211`) | No ORM, lacks `comps` table, zero pagination | Fail |
| Document Generation | Should stream SSE + PDF export | No renderer attached; `export` endpoints generic HTML only | Fail |
| UI Rendering | CMA page displays cached `commandStore` data (`aura-client/src/pages/CMAReport.tsx:45`) | Never calls backend status/download endpoints | Fail |
| History & Trace | Command store persists to localStorage (`aura-client/src/store/commandStore.ts:742`) | Multi-user history absent; backend timeline empty | Fail |

### Required Fixes

1. Backfill real CRM persistence and remove mock fallbacks to ensure data parity between UI and DB.
2. Complete CMA workflow with task creation, polling, and document generation that attaches to contact history.
3. Secure brochure export pipeline with async rendering, signed URLs, and audit trails for every deliverable.
