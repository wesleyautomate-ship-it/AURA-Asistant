

**Overall goal:**
Make the Contacts feature fully end-to-end with a real FastAPI backend while preserving the existing mock mode. Use the smallest viable set of backend routes and switch the frontend to those routes when `VITE_USE_REAL_API=true`. Maintain existing UI styling and component organization.

---

### 0) Ground rules (follow strictly)

1. **Search before creating**: if a file already exists with similar logic, **modify it**, do not create duplicates.
2. **Keep mock mode**: do not delete existing mocks—guard real calls behind `VITE_USE_REAL_API`.
3. **Follow the existing structure & style**:

   * Frontend: keep components in their current folders (`components/contacts`, `components/ai`, etc.).
   * Backend: add small route modules under `backend/app/routes/` and include them in `app/main.py`.
4. **Type safety & UX**: add loading, empty, and error states where missing; keep spacing/paddings consistent with current screenshots.
5. **Activity refresh**: when a follow-up is saved/scheduled, the Activity timeline should show it immediately (optimistic update or refetch).
6. **No breaking changes**: all new code should be additive and guarded by flags.

---

### 1) Backend – add minimal routes (only if missing)

**Inspect first**: search `backend/app` for any existing contacts/followups/ai routes and reuse if present.

* Create/verify `backend/app/routes/contacts.py` with:

  * `GET /contacts` → brief list (id, name, temperature/status, lastActivityAt, avatarUrl?).
  * `GET /contacts/{contact_id}` → detail (notes, intentScore, signals).
  * `GET /contacts/{contact_id}/activity` → list of timeline items (id, type: `call|email|ai|whatsapp|meeting`, at ISO string, text).
  * Use a small **in-memory store** (dict/lists) for now. Add TODO about replacing with DB later.

* Create/verify `backend/app/routes/followups.py` with:

  * `GET /followups?contactId={id}` → list.
  * `POST /followups` → create; body includes: `id`, `contactId`, `channel`, `dueAt`, `notes?`, `createdAt`.
  * Append to in-memory list and return created item.

* Create/verify `backend/app/routes/ai_contacts.py` with:

  * `POST /ai/followup` → returns `{ draft: string }`. Accept `{ contactId, tone, goal }`.
  * `POST /ai/summarize` → returns `{ summary: string }`.
  * `GET /ai/next-best-action?contactId=` → returns `{ title, detail }`.
  * `GET /ai/recommend?contactId=` → returns `{ items: Array<{id,title,area,price,route}> }`.
  * For now, return deterministic mock data; later can call orchestrator.

* Wire routes in `backend/app/main.py`:

  ```python
  from .routes import contacts, followups, ai_contacts
  app.include_router(contacts.router)
  app.include_router(followups.router)
  app.include_router(ai_contacts.router)
  ```

* If CORS is not already enabled for the frontend origin, add permissive CORS middleware for dev.

* Ensure `GET /healthz` and `GET /version` stay intact.

**Acceptance checks (backend):**

* `uvicorn app.main:app --reload` boots with no import errors.
* Hitting `/contacts` returns 200 JSON list.
* Hitting `/ai/followup` with a body returns a draft string.

---

### 2) Frontend – HTTP helper & env gate

**Inspect first**: look for an existing HTTP client or env flags. If present, extend it instead of creating a new file.

* If not present, add `aura-client/src/services/http.ts`:

  ```ts
  const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const USE_REAL = (import.meta.env.VITE_USE_REAL_API === 'true');

  export const api = {
    enabled: USE_REAL,
    async get<T>(path: string, signal?: AbortSignal): Promise<T> {
      const r = await fetch(`${BASE}${path}`, { signal, headers: { 'Authorization': `Bearer ${import.meta.env.VITE_DEV_AUTH_TOKEN || 'dev'}` } });
      if (!r.ok) throw new Error(await r.text());
      return r.json() as Promise<T>;
    },
    async post<T>(path: string, body: any): Promise<T> {
      const r = await fetch(`${BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${import.meta.env.VITE_DEV_AUTH_TOKEN || 'dev'}` },
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error(await r.text());
      return r.json() as Promise<T>;
    },
  };
  ```

* Update `.env.example` (and your local `.env`) to include:

  ```
  VITE_API_BASE_URL=http://localhost:8000
  VITE_USE_REAL_API=true
  VITE_AURA_MOCK_MODE=false
  VITE_DEV_AUTH_TOKEN=dev
  ```

---

### 3) Frontend – services: prefer real API when enabled

**Inspect first**: open these files if they exist and modify in place; if files differ, adapt paths accordingly.

* `aura-client/src/services/contactsApi.ts`
  Add gated calls:

  ```ts
  import { api } from './http';
  import type { Contact, ContactDetail } from '../types/contacts'; // reuse existing types if present

  export async function getContacts(signal?: AbortSignal): Promise<Contact[]> {
    if (api.enabled) return api.get<Contact[]>('/contacts', signal);
    // fallback to existing mock
  }

  export async function getContactDetail(id: string, signal?: AbortSignal): Promise<ContactDetail> {
    if (api.enabled) return api.get<ContactDetail>(`/contacts/${id}`, signal);
    // fallback mock
  }

  export async function getActivity(id: string, signal?: AbortSignal) {
    if (api.enabled) return api.get(`/contacts/${id}/activity`, signal);
    // fallback mock/empty
  }
  ```

* `aura-client/src/services/aiClient.ts`

  ```ts
  import { api } from './http';

  export async function generateFollowUp(contactId: string, opts?: { tone?: string; goal?: string }) {
    if (api.enabled) return (await api.post<{draft:string}>('/ai/followup', { contactId, ...opts })).draft;
    // fallback existing mock
  }

  export async function summarizeNotes(contactId: string) {
    if (api.enabled) return (await api.post<{summary:string}>('/ai/summarize', { contactId })).summary;
    // fallback
  }

  export async function recommendProperties(contactId: string) {
    if (api.enabled) return (await api.get<{items:any[]}>(`/ai/recommend?contactId=${contactId}`)).items;
    // fallback
  }

  export async function nextBestAction(contactId: string) {
    if (api.enabled) return api.get<{title:string; detail:string}>(`/ai/next-best-action?contactId=${contactId}`);
    // fallback
  }
  ```

* `aura-client/src/services/schedulesApi.ts`

  ```ts
  import { api } from './http';
  export interface FollowUpItem { id: string; contactId: string; channel: 'call'|'email'|'whatsapp'|'meeting'; dueAt: string; notes?: string; createdAt: string; }

  export async function listFollowUps(contactId: string, signal?: AbortSignal): Promise<FollowUpItem[]> {
    if (api.enabled) return api.get(`/followups?contactId=${contactId}`, signal);
    // fallback to localStorage implementation
  }

  export async function createFollowUp(item: FollowUpItem): Promise<FollowUpItem> {
    if (api.enabled) return api.post('/followups', item);
    // fallback to localStorage
  }
  ```

---

### 4) Frontend – wire UI states & activity refresh

**Inspect first**: locate the Contact Detail page (commonly `src/pages/contacts/[id].tsx` or similar). Update there:

* **AI Actions**: Ensure:

  * `onGenerateFollowUp` calls `generateFollowUp(contactId)` and fills the draft textarea.
  * `onScheduleFollowUp` calls `createFollowUp({...})`.

* **Loading / Empty / Error**:

  * For Recommendations and Next Best Action cards, add:

    * skeleton when loading,
    * “No recommendations yet” empty state when arrays are empty and not loading,
    * inline error state if fetch fails.

* **Activity timeline refresh**:

  * After `createFollowUp`, do either:

    * **Optimistic insert** into the Activity list with the same shape as `/contacts/{id}/activity`, or
    * `await refetch()` of `getActivity(contactId)`.
  * Keep item visuals consistent (icon by type, relative time like “3h ago”).

* **Back label**:

  * In the contact header component, add subtle text next to the chevron: “Back to Contacts”.

* **FAB behavior**:

  * Keep the FAB but ensure its click opens the contextually correct composer. Add an aria-label like `"Add follow-up"` for accessibility.

---

### 5) Run & test (must pass)

1. **Backend**: `cd backend && uvicorn app.main:app --reload`
2. **Frontend**: `cd aura-client && pnpm dev` (or yarn/npm) with `VITE_USE_REAL_API=true`.
3. **Manual QA**:

   * Contacts list loads from `/contacts`.
   * Click a contact → detail loads `/contacts/{id}`.
   * **Follow-Up** → draft from `/ai/followup` → **Save** → POST `/followups` and timeline updates.
   * **Schedule** (any channel) → creates follow-up → timeline shows without full page reload.
   * **Summarize Notes** → `/ai/summarize` populates bottom sheet with “Summarizing…” progress then content.
   * **Recommend Properties** → `/ai/recommend` card list displays; empty state is graceful.
   * **Next Best Action** → `/ai/next-best-action` card displays with title + detail.
   * Toggle `VITE_USE_REAL_API=false` → app falls back to mocks without errors.

---

### 6) Deliverables (create/update this checklist in `docs/contacts-e2e.md`)

* [ ] Routes added & included in `backend/app/main.py`
* [ ] Real API client + env flag in `aura-client/src/services/http.ts`
* [ ] `contactsApi.ts`, `aiClient.ts`, `schedulesApi.ts` gated to real API
* [ ] Loading/empty/error states added to AI cards
* [ ] Activity refresh on create follow-up
* [ ] Smoke test passed with real backend
* [ ] Mock mode still works when re-enabled

---

### 7) Notes

* If any file paths differ in this repo, **adapt to existing structure** instead of forcing new ones.
* Keep code concise and idiomatic (TypeScript strict, FastAPI pydantic models).
* Ensure all new modules are lint-clean and build passes.


