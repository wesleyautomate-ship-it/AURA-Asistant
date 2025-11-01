# Aura Execution Checklist

Progress tracker derived from the recent audit findings, with the “why” and “what good looks like” captured for each workstream. Check items off as work completes to keep delivery focused and visible.

---

## Core Data & API Flow

**Context:** The mobile UI attempts to load contacts from `/api/v1/contacts`, but the backend currently mounts those routers without the `/api/v1` prefix. That’s why the dashboard shows “Failed to load contacts” and we see 404s in DevTools. Additionally, the client runs in mock mode by default (`VITE_USE_REAL_API=false`), so even once the route works, we still ingest mock data unless the flag is flipped.

- [x] Mount contacts/follow-ups routers under `/api/v1` in `backend/app/main.py` and confirm `/api/v1/contacts` loads without 404 (TestClient smoke on 2025-10-29 returned HTTP 200 with an empty list; seed data still pending).
- [x] Enable real backend usage in the client (`VITE_USE_REAL_API=true`) and verify contacts, templates, and draft endpoints return live data by smoking the UI and curl-ing the endpoints (confirmed `.env`, `.env.development`, and `.env` already true; `.env.local` retains optional overrides).
- [x] Seed sample contact records (via `seed_sample_clients`) so `/api/v1/contacts` returns real data; verified TestClient response now includes five EnhancedClient entries from `clients` table (propertypro_dev.db).
- [x] Point the React client at the running backend by setting `VITE_API_BASE` to `http://localhost:8000/api/v1` (both `.env` and `.env.development`), fixing the “Failed to load contacts” UI error caused by the previous relative `/api/v1` base path.
- [x] Align `.env.local` with the real backend (enable `VITE_BACKEND_ENABLED` and set `VITE_API_BASE*` to `http://localhost:8000/api/v1`) so local overrides no longer redirect requests to the Vite dev server root.

---

## Brochure Workflow

**Context:** The brochure flow leans on seeded listings (`DEFAULT_LISTINGS`) and mock draft persistence. Draft list API calls always return empty, the editor saves to local state, and the render step polls forever because the backend never flips status outside of mock mode. We need real listing data, persistence, and storage for assets.

- [ ] Replace seeded listing fallbacks with live listing data in `PropertyBrochureService`, wiring to the listings table or CRM data rather than hard-coded Dubai mock records.
- [ ] Persist drafts in the database via `/api/v1/brochures` so the editor can reload state across sessions; verify `GET /brochures/{id}` reflects updates made from the UI.
- [ ] Ensure brochure status updates propagate to the editor preview (poll `/brochures/{id}` until `status=ready`, display `download_url`, surface errors).
- [ ] Hook template selection and draft listing metadata to actual uploads/storage (use file-processing endpoint for photos, store logo URLs) instead of base64 blobs inside Zustand.

---

## Command Center Tasking

**Context:** The command center UI is rich (voice/text, progress tracker, follow-ups) but currently keeps everything client-side. Requests never travel through the new intelligence API, tasks aren’t written to `ai_tasks`, and the Tasks screen reads from local Zustand history. This blocks end-to-end flow and audit trails.

- [ ] Route command center submissions through `intelligenceApi.generateContentWithProgress` so every request creates a backend task.
- [ ] Persist resulting task/content IDs server-side (`ai_tasks`, `intelligence_content` tables) and confirm they’re retrievable via `/api/v1/intelligence/status/{task_id}`.
- [ ] Populate `/tasks` UI from backend data (convert to use `requestsApi` or a new endpoint) instead of relying on local storage only.
- [ ] Record audit trail entries when tasks complete (brochure, CMA, follow-ups) so contact timelines and compliance logs stay accurate.

---

## Agentic Chat

**Context:** The agentic chat endpoint streams canned text, only simulating retrieval and tool invocation. It creates tasks but never waits for results, doesn’t run RAG, and the front-end’s knowledge panel is empty because no real data is returned. To match the product vision we need real responses and tool output.

- [ ] Swap canned SSE responses for real retrieval + generation using `EnhancedRAGService` and `ai_content_generator` (Gemini/OpenAI), populating the retrieval event with excerpts.
- [ ] Handle tool invocations by awaiting orchestrator results and streaming actual progress/final content instead of mock chunks.
- [ ] Persist conversation turns in `chat_messages` and expose an endpoint the UI can poll to reload threads.

---

## CMA & Analytics

**Context:** CMA flows are flagged as “Fail” in `docs/FEATURE_FLOWS.md`. The wizard shortcuts to `/requests`, the backend doesn’t emit usable reports, and no download/export pipeline exists. Analytics cards on the dashboard show static metrics or placeholders.

- [ ] Finish the CMA API pipeline: submit tasks through `cma_reports_router`, ensure status polling works, generate a downloadable PDF/HTML, and attach the result to the originating contact.
- [ ] Wire the CMA UI to display status chips, show progress, and surface the download button once finished.
- [ ] Backfill analytics tiles with real metrics (`analytics_router` endpoints) or remove placeholders until the data exists.

---

## Media & Storage

**Context:** Branding logos and listing photos stay in local component state as data-URIs. There is a file processing router ready to ingest assets, and backend storage writes to `/uploads`. Without hooking into that pipeline we cannot build real brochures or reuse assets in CMA decks.

- [ ] Point branding/photo uploads to the file processing API, store returned URLs/IDs on the draft, and verify files land in the configured storage bucket or directory with correct permissions.
- [ ] Implement retention/signed URLs if files need to be shared externally.

---

## Intelligence Layer Parity

**Context:** Documentation for v3.3 lays out memory service, validation pipeline, quality scoring, and audit logging. In reality, generated content skips these steps—`ai_content_generator` returns mock data, memory tables stay empty, and the UI has no quality signal. We need parity before calling the system “Intelligent Content Brain”.

- [ ] Persist generated artifacts to the memory service tables (`memory_records`, `artifact_store`) as part of task completion.
- [ ] Invoke the validation pipeline before marking content `export_ready`; fail the task if checks do not pass, surface reasons in UI.
- [ ] Capture quality scores and display them in Tasks and Command Center cards for quick health checks (UI badge / tooltip).
- [ ] Add audit log entries referencing memory IDs for traceability.

---

## Environment & Secrets

**Context:** Many of the “real” code paths depend on external LLM providers (Gemini, OpenAI). Without properly configured API keys (`GOOGLE_API_KEY`, `GEMINI_API_KEY`, etc.) the system silently falls back to mocks.

- [ ] Configure required API keys in `.env` and the deployment environment so `ai_content_generator` and `PropertyBrochureService` can call real models.
- [ ] Add guardrails/error logging if keys are missing to avoid silent mock fallbacks.

---

Keep this file open while implementing. When a task is completed, change `[ ]` to `[x]` and add brief release notes if needed. This will become the single source of truth for our execution sprint.
