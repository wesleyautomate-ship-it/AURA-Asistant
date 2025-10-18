Root: AURA-Asistant

Frontend: aura-client

Backend: backend

Database: SQLAlchemy + Alembic or similar (SQLite/Postgres)

Related folders: aura-client/src/components/brochure/**, aura-client/src/services/brochureApi.ts, backend/app/routes/brochure.py, backend/app/services/pdf/**, backend/app/templates/**

0) Rules

Audit first, code second – only write new code if a feature is missing.

Reuse existing logic before adding anything new.

Respect existing design/UX (containers, tiles, buttons, etc.).

Keep mock mode (for demo PDFs) but ensure the real pipeline works when VITE_USE_REAL_API=true.

Include database, backend, frontend, and tests.

All tests must pass locally with SQLite and in CI.

1) Inventory

Scan and list every file relevant to brochure creation:

Frontend:
src/components/brochure/**, src/pages/**, src/services/brochureApi.ts, src/hooks/useBrochure.ts, src/state/**

Backend:
app/routes/brochure.py, app/services/pdf/**, app/templates/**, app/models/**

Database:
models/tables dealing with brochures, templates, assets

Assets:
check static/templates, media/uploads, or similar folders.

Output ? audit-results.json.INVENTORY.brochure

2) Database Audit & Plan

If DB models exist:

List tables, columns, relationships, indexes.

Verify foreign keys (brochure.contact_id, brochure.template_id).

Identify missing constraints, indexes, soft-delete flags, etc.

If not:

Scaffold models and Alembic migrations for:

brochure_templates (
  id UUID/PK,
  name TEXT NOT NULL,
  description TEXT NULL,
  file_path TEXT NOT NULL,        -- PDF or base HTML
  created_at TIMESTAMPTZ DEFAULT now()
);

brochures (
  id UUID/PK,
  contact_id FK -> contacts.id,
  template_id FK -> brochure_templates.id,
  status TEXT CHECK(status IN ('draft','generating','ready','failed')),
  pdf_url TEXT NULL,
  metadata JSONB NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


Include seed script inserting 2-3 sample templates.

Output ? audit-results.json.DB_AUDIT.brochure

3) Backend Routes & Services Audit

Discover all endpoints:

/brochures ? GET list, POST create (trigger generation)

/brochures/{id} ? GET detail

/brochures/{id}/download ? GET PDF file

/templates ? GET available templates

/brochures/{id}/status ? GET generation progress (if async)

Verify:

File creation uses correct PDF library (e.g., reportlab, weasyprint, pdfkit).

Template engine merges data correctly (property info, images, etc.).

Storage – PDFs saved to /media/brochures or S3; URL accessible to frontend.

Error handling for invalid template or missing data.

CORS allows dev frontend.

If missing, stub minimal FastAPI routes and PDF generator that outputs dummy PDFs.

Output ? audit-results.json.BACKEND_AUDIT.brochure

4) Frontend Audit

Inspect UI flow & data contracts:

Entry point: Which page or tile launches brochure creation (e.g., “Request Brochure”)?

Flow:

Template selector

Data preview / property merge

“Generate” button ? progress ? download link

History / list of generated brochures

Service calls:

getTemplates(), createBrochure(), getBrochureStatus(), downloadBrochure()

Env flags:

VITE_USE_REAL_API, VITE_API_BASE_URL

UX resilience:

Loading/success/failure states

Progress indicators (e.g., spinner, % bar)

Disable “Generate” button while running

Output ? audit-results.json.FRONTEND_AUDIT.brochure

5) Contract Alignment

Compare every frontend service call with backend route:

method + URL match?

payload/response shapes compatible?

missing or extra fields?
List discrepancies in audit-results.json.CONTRACTS_MISMATCH.brochure.

6) Automated Tests
6a) Backend (pytest)

Write tests under backend/tests/test_brochure_routes.py:

GET /templates ? 200 + templates list

POST /brochures ? 201 + new record + background PDF generation

Poll /brochures/{id}/status until ready ? assert file exists

GET /brochures/{id}/download ? 200 PDF content-type

Negative tests: invalid template, permission, missing contact.

Use tmpdir or SQLite DB fixture. Mock actual PDF writing for speed.

6b) Frontend (Vitest)

Add tests for:

Template selection list renders correctly.

Generate button triggers API call and disables while loading.

Success path shows “Download” link.

Error path shows toast or inline message.

Files:

aura-client/src/__tests__/BrochureFlow.spec.tsx
aura-client/src/__tests__/BrochureService.spec.ts

6c) E2E (Playwright)

Drive through real backend with mock contacts:

Open Brochure tab ? select template ? click “Generate”.

Wait for status ? “Ready”.

Click “Download” ? verify PDF blob header.

Reload ? brochure appears in list/history.

Save under aura-client/e2e/brochure.e2e.spec.ts.

6d) Contract Tests

Generate TS types from /openapi.json, assert type compatibility for brochure endpoints.

7) Seed & Runbook

Add to RUN.md:

how to run PDF generator locally (fonts, wkhtmltopdf if used)

alembic upgrade head

python backend/scripts/seed_brochure_templates.py

test commands (pytest, pnpm test, pnpm exec playwright test)

8) CI

Extend GitHub Actions to include:

Run Alembic migrations

Run backend & frontend tests

Upload generated PDF as artifact for inspection

9) Acceptance Matrix
Scenario	Contracts	Works Mock	Works Real	UX States	Perf
List Templates					
Generate Brochure					
Poll Status					
Download PDF					
Error Handling					

Populate with ?/??/? in audit-results.json.ACCEPTANCE_MATRIX.brochure.

10) Output

Produce:

audit-results.json with sections for brochure feature

Tests, seeds, and migrations if missing

TOP_5_FIXES.brochure (short bullet list)

0 failing tests on local run with SQLite