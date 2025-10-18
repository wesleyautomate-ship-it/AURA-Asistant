

You are auditing **AURA**, an end-to-end **AI assistant for real-estate operators** (agents, brokers, admins). Its goal is to make everyday workflows **faster, safer, and higher-quality** by combining structured CRMs, LLM reasoning, tool use, and document/PDF generation.

#### A→Z Vision of the AI Assistant (capability map)

1. **Natural Input** (text or voice):

   * User can type or speak tasks (“Create a CME/CMA for 52 XYZ Drive”, “Follow up with Alex about Palm properties”, “Summarize this lead’s intent”, “Draft a brochure for Orla 3BR”).
   * Voice goes through **ASR (speech-to-text)**, then unified parsing.
2. **Intent Understanding & Planning**:

   * Orchestrator parses the request, resolves entities (contact, property, area), selects the workflow (CME/CMA, brochure, follow-up, summary, recs), composes a **multi-step plan** with tool calls.
   * **LLM (e.g., Gemini)** performs: intent classification → info gaps check → asks for clarifications if needed → plans tool calls (DB/MLS/search/vector/doc gen).
3. **Tool Use & Data Access**:

   * **Data layer**: Postgres (dev may be SQLite), ORM models for contacts, activities, followups, brochure_templates, brochure_drafts, properties, comps.
   * **Search & Retrieval**: property/comp lookups, document snippets (vector DB optional), MLS/portal APIs (if configured).
   * **Document Generation**: brochure & CMA/CME generation to PDF (WeasyPrint/wkhtmltopdf or ReportLab fallback).
   * **Scheduling & Notifications**: follow-ups saved, timelines updated; optional email/WhatsApp draft output.
4. **Safety, Observability & Governance**:

   * Guardrails (role, scope, PII), rate limits, structured audit logs, request IDs.
5. **Result Presentation (Frontend)**:

   * Reliable UI flows with **loading/empty/error** states; clearly shows plan steps, intermediate results and final artifacts (PDF links, summaries, recommendations).
   * History & traceability per contact/property/work request.
6. **Feedback & Iteration**:

   * User can refine (e.g., “include newer comps”, “change tone to professional”, “schedule for tomorrow 9am”).
   * Assistant learns preferences (templates, tones, areas of interest).

> Note: “CME” above is used as requested (industry often says “CMA” — Comparative Market Analysis). Treat “CME/CMA” synonymously in the audit.

---

### 1) What we’re actively building now (Current Focus)

* **Contacts**: CRM views, AI actions (follow-ups, summaries, recommendations, next-best action), activity timeline, scheduling.
* **Brochure Generation**: template selection → data merge → PDF render → download/history.
  (These features should be **vision-aligned**: callable via natural prompts, instrumented, with strong UX states and testing.)

---

### 2) What to Produce (Artifacts)

Create/update the following **docs** in `/docs/` (create the folder if missing):

* `SUMMARY.md` — Executive summary of findings & Top 10 fixes.
* `VISION_ARCHITECTURE.md` — **High-level architecture** we aspire to (Mermaid diagrams), capability map, end-to-end assistant flows (text + voice).
* `AUDIT.md` — Deep audit of **frontend, backend, database, infra, security, performance, UX**.
* `FEATURE_FLOWS.md` — Exact **A→Z flows** for each feature (Contacts, Brochure, and **CME/CMA**), with:

  * Inputs → orchestration steps → tools → data retrieval → doc/PDF generation → UI rendering → history/traces.
  * **For each step**: what exists today vs. what’s missing, with pass/fail checks.
* `ARCHITECTURE_TARGET.md` — Target system (components, services, queues, data models, APIs), required contracts, SLAs/SLOs.
* `RUNBOOK.md` — Local vs Docker instructions, env variables, migrations, seeds, troubleshooting.
* `SECURITY.md` — CORS/authn/authz posture, secrets, PII handling, upload/download safety, dependency scan summary.
* `PERFORMANCE.md` — k6/Lighthouse results, p95 targets, bottlenecks & fixes.
* `RELIABILITY.md` — health/version, retries/timeouts, logging/metrics, background processing.
* `CI_PIPELINE.md` — Proposed CI stages (lint/type/test/e2e/build/scan/artifacts).
* `TEST_STRATEGY.md` — Unit/integration/contract/E2E matrix, data seeding, non-flaky patterns.

Also generate if missing (non-intrusive helpers):

* `perf/k6/contacts-smoke.js`, `perf/k6/brochure-smoke.js`, `perf/k6/cma-smoke.js`.
* `scripts/lighthouse.mjs` (run against built frontend).
* `.github/workflows/ci.example.yml` (commented template with all steps).
* (Optional) `Makefile` with common targets (comment out if repo doesn’t use Make).

Finally, output a concise `docs/AUDIT_RESULTS.json` with versions, endpoint probes, DB tables detected, scans, perf summaries, and a list of critical blockers.

---

### 3) Repository Auto-Discovery (Read-Only First)

* Detect actual paths for:

  * **Frontend** (Vite/React/TS): pages/routes; `src/features/{contacts,brochure,cma}/**`; `src/services/**`; `src/types/**`; tests (`__tests__`, e2e).
  * **Backend** (FastAPI): `app/main.py`, `app/api/**`, `app/core/**` (db, settings, models), `app/services/**` (render, ai/orchestrator), `app/schemas/**`, `app/alembic/**`, `scripts/**`.
  * **Infra**: `Dockerfile*`, `docker-compose*`, workflows, lint configs, `.env*`.
* Produce an **Inventory** table (path, purpose, key exports). Add to `AUDIT.md`.

---

### 4) Vision-Aligned Target Architecture (Author First, Then Audit Against It)

Write `VISION_ARCHITECTURE.md` with **Mermaid diagrams**:

* **Component Map**: frontend, backend API, orchestrator, LLM (Gemini), DB, vector store (optional/flagged), PDF renderer, object storage, message/worker (optional), observability (logs/metrics), CI.
* **Data Flow** for **voice/text → plan → tools → results**.
* **ERD** for `contacts`, `contact_notes`, `activities`, `followups`, `brochure_templates`, `brochure_drafts`, `properties`, `comps`.
* **API Surface** we aspire to (paths, verbs, payloads) for Contacts, Brochure, CME/CMA.

---

### 5) End-to-End Feature Flows (How it SHOULD Work) — then Audit Reality

In `FEATURE_FLOWS.md`, define A→Z steps, expected contracts, and UI states for:

#### 5.1 Voice/Text Command: “Create a CME/CMA for XYZ property”

1. **Input**: voice or text.

   * Voice → **ASR** → transcript.
   * NLU extracts: property address/ID, target date range, bedrooms/baths, comp radius, etc.
2. **Planner (LLM)**: build plan with tool calls:

   * Resolve property → fetch details from DB/MLS.
   * Fetch comps (filters, date range).
   * Compute metrics (avg price/ft², adjustments).
   * Generate CMA doc (HTML → PDF).
   * Save record (history) + provide **Download** link.
3. **Execution**:

   * Tool calls to DB/MLS; errors handled with retries/timeouts; partial results logged.
   * PDF generation service writes to `/uploads` (dev) and returns URL.
4. **Frontend Presentation**:

   * Show progress (planner steps → resolved entities → comp set → draft metrics).
   * Final: CMA card with **Download PDF**, **Share**, **Revise**.
5. **Audit Checks**:

   * Endpoint existence, types, response times; tests; UI loading/error states; doc stored; history visible.

#### 5.2 Contacts: AI Follow-Up / Summary / Recommendations / NBA

* A→Z with expected endpoints (`/contacts`, `/ai/*`, `/followups`), record activity timeline, refresh behavior, UX states.

#### 5.3 Brochure Generation

* A→Z with expected endpoints (`/api/v1/templates`, `/api/v1/brochures`, `/download`, status polling), templates DB, render pipeline, history, UX states.

For **each** step above: define **“Expected vs Found”**, **Pass/Fail checks**, and **Fix suggestions**.

---

### 6) Environment & Build Health

* Detect Python version (flag **3.14** incompatibility; recommend **3.11.x**).
* Recommend compatible matrix (example):

  ```
  fastapi 0.115.* / starlette 0.37.* / httpx 0.27.* / pydantic 2.8.* / sqlalchemy 2.0.* / alembic 1.13.*
  ```
* Check `requirements.txt` for PDF libs (`reportlab`, `weasyprint`/system deps) and optional vector DB (`chromadb`) — ensure **lazy import gating** if disabled by env.
* Frontend: check Node/PNPM versions, tsconfig strictness, build passes.

Add findings to `AUDIT.md` and concrete **pin suggestions** to `RECOMMENDATIONS.md`.

---

### 7) Database Audit

* Verify presence & quality of tables:
  `contacts`, `contact_notes`, `activities`, `followups`, `brochure_templates`, `brochure_drafts`, `properties`, `comps`.
* Check FKs, NOT NULLs, enums, indexes (e.g., `idx_activities_contact_time`, `idx_followups_contact_due`, `idx_brochure_drafts_created_at`).
* Alembic lineage (no divergent heads); seeds idempotent.
* Note gaps (e.g., missing `brochure_templates` or missing `contact_id` FK) and propose **migration stubs** (but **do not** change product code in this pass).

Put the comparison (expected vs current) in `AUDIT.md` and ERD deltas in `ARCHITECTURE_TARGET.md`.

---

### 8) Backend API Surface & Contracts

* Crawl routers; list endpoints for Contacts, Brochure, CME/CMA.
* Export `/openapi.json` (if possible) and map to frontend service functions.
* Record **mismatches** (paths, methods, fields, status naming like `rendering` vs `generating`).
* Verify **CORS** for dev.
* Note health/version endpoints.

Write an **API matrix** in `ARCHITECTURE_TARGET.md` and a **mismatch list** in `AUDIT.md`.

---

### 9) Frontend UX & Resilience

* For each screen (Contacts list/detail; Brochure flow; CMA flow if present), check:

  * **Loading/empty/error** states.
  * Abort signals/cancellation, retries, debouncing (e.g., notes autosave).
  * Accessibility basics (labels, focus, aria for FAB and dialogs).
  * Type strictness: no `any` leaks; align unions with backend enums.
* Lighthouse quick check (if built) — record numbers.

Document concrete gaps and **UI fixes** in `AUDIT.md`.

---

### 10) Performance, Reliability, Security (Light but Actionable)

* Create **k6** scripts (contacts/brochure/cma smoke). Run locally if possible; capture p95, error rate.
* Reliability: timeouts/retries on AI & PDF services, structured logs with request IDs, **/healthz** & **/version** working.
* Security: run lightweight dependency and secret scans; review upload safety & download path traversal; check CORS domains.

Summarize in `PERFORMANCE.md`, `RELIABILITY.md`, `SECURITY.md`.

---

### 11) CI/CD & DevEx

* If CI exists, describe coverage; else propose `ci.example.yml` with stages:
  install → lint → typecheck → backend tests → frontend tests → e2e (smoke) → build images → hadolint/trivy → artifacts.
* Add caching and parallelization notes.

Write `CI_PIPELINE.md`.

---

### 12) Prioritized Fix Plan & Acceptance

* Create **Top 10 Fixes** list (impact×effort, owner FE/BE/Infra), with links to evidence.
* Provide **acceptance criteria** checklists for each major workflow (Contacts, Brochure, CMA), including **end-to-end** success signals (e.g., “voice → transcript → plan → comps → PDF → UI download visible → history saved”).

Put in `SUMMARY.md` and `RECOMMENDATIONS.md`.

---

### 13) Non-Disruptive Helpers (optional)

* If needed to measure, generate k6 & Lighthouse scripts in `perf/` and `scripts/` (don’t alter product code unless a trivial one-liner is required to start the app).
* Do **not** attempt to run Docker here; generate instructions and commands into `DOCKER_GUIDE.md` and `RUNBOOK.md`.

---

### 14) Final Output to STDOUT (in addition to files)

Print this JSON:

```json
{
  "docs_created": [
    "docs/SUMMARY.md",
    "docs/VISION_ARCHITECTURE.md",
    "docs/AUDIT.md",
    "docs/FEATURE_FLOWS.md",
    "docs/ARCHITECTURE_TARGET.md",
    "docs/RUNBOOK.md",
    "docs/SECURITY.md",
    "docs/PERFORMANCE.md",
    "docs/RELIABILITY.md",
    "docs/CI_PIPELINE.md",
    "docs/TEST_STRATEGY.md",
    "docs/AUDIT_RESULTS.json"
  ],
  "highlights": {
    "critical_findings_count": "<int>",
    "top_recommendations": ["...", "...", "..."]
  }
}
```

If anything blocks (e.g., app won’t import), still generate docs with a **Blocking Issues** section listing exact remediations.

---

### 15) Guardrails

* Default to **Python 3.11.x**, not 3.14.
* If optional components (e.g., Chroma/vector DB) are disabled by env, ensure the audit doesn’t import them (lazy checks only).
* Be explicit and reference **real file paths** from this repo.
* Prefer detail over brevity. No lorem ipsum. Clear, actionable steps.

