Implement a complete, production-ready Brochure flow (create → pick template → edit content/branding with live preview → render PDF → download/share), using the provided “Brochure template example.pdf” as the visual model. Maintain the app’s existing visual style, spacing, and component patterns from the codebase/screenshots.

🔎 Very important rule: Before adding ANY new file, search the repo for similar logic or existing helpers and extend/edit them if reasonable. Reuse established patterns (routing, API layer, components, state, toasts, loaders, typography, shadows, spacing). Only create a new file if there is no suitable place to add code.

0) Conventions & Pre-flight

Search-first: Do a repo-wide search for existing items that match these names/purposes and reuse:

API client wrappers (e.g., api/*, services/*, lib/http.ts, useApi.ts).

Design system primitives (e.g., Button, Card, SectionHeader, Input, Textarea, Tabs/Stepper, Toast/Notifier, Skeleton).

State management (React Query / Zustand / Redux). Match whatever the app already uses.

Routing pattern (React Router, file routes, etc.).

Backend patterns (FastAPI routers in app/routers, models in app/models, Pydantic schemas in app/schemas, services in app/services, S3/GCS client, PDF/HTML rendering utilities).

Existing asset upload/presign endpoints.

Style: Match existing CSS/tokens and UX flows. Use the same spacing, shadows, rounded radii, fonts, and button sizes. If there’s a component for titles/subtitles/section headers, use it.

Fix obvious breaking errors while you’re here:

In AIActionBar.tsx (or similar), if onScheduleFollowUp is used, provide a safe default:

const AIActionBar = ({ onScheduleFollowUp = () => {} , ...props}) => { ... }


Any “open contact” null/undefined path should be guarded (check router params exist before dereferencing; show empty state otherwise).

1) Backend — Brochure Draft CRUD + Render

Search-first: Look for existing patterns for CRUD resources (e.g., properties, CMA, templates). If a similar router/scheme exists, extend it. If not, add the following with the app’s naming conventions.

1.1 Models & Schemas

File (edit existing if similar): backend/app/models/brochure.py

SQLAlchemy model: BrochureDraft

id: UUID (pk)

data: JSONB — stores the whole draft (see schema below)

status: String in {"draft"|"rendering"|"ready"|"error"}

download_url: String | None

created_at, updated_at

File (edit existing if similar): backend/app/schemas/brochure.py

Pydantic models: BrochureDraftCreate, BrochureDraftUpdate, BrochureDraftOut

Draft JSON structure (store in data):

{
  "templateKey": "passo-building-v1",
  "propertyId": null,
  "hero": { "title": "", "subtitle": "", "image": { "key": "", "url": "" } },
  "about": { "heading": "", "body": "", "gallery": [] },
  "whyInvest": { "bullets": [], "sideQuote": "", "interiorImage": { "key": "", "url": "" } },
  "paymentPlan": { "items": [ { "label": "", "date": "", "percent": 0 } ], "blurb": "" },
  "amenities": {
    "sections": [ { "title": "", "text": "" }, { "title": "", "text": "" }, { "title": "", "text": "" } ],
    "features": [],
    "bgImage": { "key": "", "url": "" }
  },
  "collections": {
    "groups": [
      { "name": "Wellness Collection", "bullets": [], "image": null },
      { "name": "Residences Collection", "bullets": [], "image": null },
      { "name": "Elite Collection", "bullets": [], "image": null },
      { "name": "Penthouses", "bullets": [], "image": null },
      { "name": "Beach Mansions", "bullets": [], "image": null }
    ]
  },
  "agent": { "name": "", "about": "", "phone": "", "website": "", "company": "", "photo": null },
  "branding": { "primary": "", "secondary": "", "fontHead": "", "fontBody": "", "logo": null },
  "meta": { "lastEdited": "", "status": "draft" }
}

1.2 Router (CRUD & Render)

File (edit existing if similar): backend/app/routers/brochures.py

POST /brochures → create new draft; body: BrochureDraftCreate.

GET /brochures/{id} → fetch one.

PATCH /brochures/{id} → partial update (BrochureDraftUpdate merges into data).

POST /brochures/{id}/render → set status="rendering", enqueue job, return { renderId }.

GET /brochures/{id}/download → 302/temporary redirects to download_url (signed URL).

Register this router in backend/app/main.py the same way as existing routers.

1.3 Rendering Service

Search for any existing HTML→PDF/Puppeteer/WeasyPrint utilities; reuse if present.

If none:

File: backend/app/services/render_service.py

Function: render_brochure_to_pdf(draft: dict) -> str returns download_url.

Use headless Chromium (Puppeteer via node service or pyppeteer) or WeasyPrint.

The render should load a single HTML template that mirrors the final layout; inject draft.data and branding.

File: backend/app/templates/passo-building-v1.html (or Jinja2/React SSR path per existing stack) that matches the PDF structure (see section 3.3 for the layout).

If project uses a queue/worker, enqueue rendering; otherwise do it in-process with a spinner on the client.

1.4 Assets

Search-first for existing upload endpoints (e.g., /assets, /upload, presigned S3).

If none, add POST /assets/presign (or similar) to obtain presigned URL; client uploads directly; returns { key, url }.

2) Frontend — Pages, Sections, Divs, and Exact Placement

Routing pattern: Follow the app’s established routing. The screens live under a Brochure feature.

2.1 AI Workflow Screen (existing)

Do not redesign. Add the following behaviors:

The Brochure card navigates to /brochure/templates.

“Recent Drafts” list items navigate to /brochure/{draftId}/review.

Floating “+” opens a creation modal (if this modal pattern already exists). Else, clicking “+” navigates to /brochure/templates.

2.2 Templates Screen — BrochureTemplates

File: reuse existing page if present; else aura-client/src/features/brochure/pages/BrochureTemplates.tsx

Page structure (top to bottom):

Div: PageHeader

Left: h1 “Brochure Templates”

Subtext: “Choose a template to start”

Div: TemplateList (vertical stack of Card components)
Each TemplateCard contains:

Div: Thumbnail (placeholder or generated)

Div: Body

h3 template name (e.g., “Clean Minimal”, “Passo Building”)

p tagline

Right-aligned Check icon when selected

Card click toggles selection; selected card has highlighted border (use existing selected styles).

Div: StickyFooter (bottom, inside safe area)

Left: Secondary Button: “Start from Blank”

Right: Primary Button: “Use Template” (disabled until a card is selected)

Behavior:

On “Use Template”: POST /brochures with { templateKey } then route to /brochure/{id}/property.

2.3 Editor Screen — BrochureEditor

File: reuse if present; else aura-client/src/features/brochure/pages/BrochureEditor.tsx
URL: /brochure/:id/:tab where :tab ∈ {property,content,branding,review}

Overall page layout (two-column split):

Div: PageHeader

Left: h1 “Brochure Editor”

Subtext: “Step X of 4”

Div: StepperTabs (existing tab/segment component) with 4 tabs.

Div: Body (grid) → LeftPane (inputs) | RightPane (live preview)

LeftPane (Inputs Column)

Property tab

Section: SearchBox (existing Input search)

Section: PropertyList (existing list style)

Section: CTAFooter (sticky within column)

Primary Button “Next →” (disabled until a property is selected)

Content tab (group by PDF pages):

Section: About

Fields: heading (Input), body (Textarea), gallery[0..1] (Image upload)

Section: Why Invest

Repeater: bullets (3–5, Input per line), sideQuote (Textarea), interiorImage (Image upload)

Section: Payment Plan

Table-like list: {label,date,percent} rows with add/remove

Small note (help text): sum to ~100%

Section: Amenities

Three mini blocks: sections[0..2].{title,text}

Features: multi-select/tag input

Section: Collections

5 grouped bullet lists (name locked, bullets editable), optional image per group

Section: Agent

name, about, phone, website, company, photo upload

SectionFooter: “Back” (secondary) | “Next →” (primary)

Branding tab

Section: Colors (Primary/Secondary color pickers)

Section: Typography (fontHead, fontBody using existing font selector if any)

Section: Logo (image upload)

SectionFooter: “Back” | “Next →”

Review tab (LeftPane)

Section: Render Actions

Primary: “Render PDF”

Secondary: “Download Latest” (enabled when download_url exists)

Link: “Copy Share Link”

Section: Status

Show current status chip: Draft / Rendering… / Ready / Error (with message)

RightPane (Live Preview Column)

Div: PreviewHeader — “Live Preview”

Div: PreviewCanvas — render the same layout component used for server render; scrollable; scales to fit width; light page shadows.

Behavior: re-render on each edit (debounced 250–500ms)

Autosave & Feedback:

On any LeftPane change → local draft update → debounced PATCH to /brochures/:id (500–1000ms).

When a PATCH completes → show subtle “Saved ✓” toast or inline status label.

When clicking Render PDF:

Set status to rendering, call /brochures/:id/render, show toast “Generating your PDF…”

Poll (or refetch) the draft until status="ready" and download_url present → toast “PDF ready — Download”.

2.4 Components & Files (search-first, reuse names)

aura-client/src/features/brochure/api/brochure.ts

createDraft, getDraft, updateDraft, renderDraft, getDownloadUrl

aura-client/src/features/brochure/hooks/useBrochureDraft.ts

Encapsulate loading by id, autosave (debounced), and status polling.

aura-client/src/features/brochure/components/PreviewPane.tsx

Accepts draft and renders the template layout.

aura-client/src/features/brochure/templates/passo-building-v1/Layout.tsx

Exactly mirrors final PDF pages (see mapping below).

All typography/spacing via existing design tokens; no ad-hoc styles unless necessary.

3) Template Layout — Explicit Page/Section Mapping

Use one React layout component with clear page sections (divs). This same structure should be used both in the RightPane (live preview) and by the backend renderer (SSR/HTML export). The structure below matches the PDF.

Layout.tsx structure:

<div data-brochure="passo-v1">
  {/* Page 1: Cover / Hero */}
  <section data-page="1" data-role="hero">
    <div className="hero-image" />  {/* uses draft.hero.image */}
    <div className="hero-overlay">
      <h1>{hero.title}</h1>
      <p>{hero.subtitle}</p>
      {/* brand logo if provided, aligned per design */}
    </div>
  </section>

  {/* Page 2: About */}
  <section data-page="2" data-role="about">
    <header><h2>{about.heading}</h2></header>
    <div className="about-body">
      <p>{about.body}</p>
      <div className="about-gallery">
        {/* exactly two image slots; draw empty placeholders if absent */}
      </div>
    </div>
  </section>

  {/* Page 3: Why Invest */}
  <section data-page="3" data-role="why-invest">
    <aside className="side-quote">{whyInvest.sideQuote}</aside>
    <ul className="bullet-list">{/* 3–5 bullets */}</ul>
    <div className="interior-image" />
  </section>

  {/* Page 4: Payment Plan */}
  <section data-page="4" data-role="payment-plan">
    <header><h2>Payment Plan</h2></header>
    <div className="plan-grid">{/* each item: percent big, label/date small */}</div>
    <p className="plan-blurb">{paymentPlan.blurb}</p>
  </section>

  {/* Page 5: Amenities & Lifestyle */}
  <section data-page="5" data-role="amenities">
    <div className="amenities-bg" />
    <div className="amenities-sections">{/* three text blocks */}</div>
    <ul className="amenities-features">{/* feature chips/list */}</ul>
  </section>

  {/* Pages 6–7: Collections */}
  <section data-page="6" data-role="collections-1">
    {/* Wellness, Residences, Elite */}
  </section>
  <section data-page="7" data-role="collections-2">
    {/* Penthouses, Beach Mansions */}
  </section>

  {/* Page 8: Agent */}
  <section data-page="8" data-role="agent">
    <div className="agent-card">
      <div className="agent-photo" />
      <div className="agent-info">
        <h3>{agent.name}</h3>
        <p>{agent.about}</p>
        <p>{agent.phone} • {agent.website}</p>
        <p>{agent.company}</p>
      </div>
      <div className="brand-logo" />
    </div>
  </section>
</div>


Branding tokens: map branding.primary/secondary/fontHead/fontBody/logo to CSS variables at the root of this layout (--brand-primary, etc.) so both preview and server render look identical.

4) Data Hydration From Property

When a property is selected in the Property tab:

Prefill:

hero.title = property title

hero.subtitle = location / short pitch

about.heading = property or building name

about.body = a few sentences from property description (truncate safely)

about.gallery = 1–2 property photos

If property has milestones/payment info, map to paymentPlan.items

Show an inline note: “We’ve prefilled from your property — adjust anything you like.”

5) UX Polish & States

Autosave: debounce 500–1000ms, show subtle “Saved ✓” inline (top-right of LeftPane header) and/or toast on the first save.

Loaders: Use existing Skeleton while fetching draft and property list.

Toasts:

Save success/fail

Render start (“Generating your PDF…”)

Render success (“PDF ready — Download now”)

Render error (show message and “Try again”)

Buttons enablement:

“Next” disabled until current step is complete (e.g., property selected).

“Render PDF” enabled only if required fields are present (About heading/body at minimum).

Error handling: Guard every null path in preview; show tasteful placeholders rather than crashing.

6) Tests / Acceptance

Create a simple manual QA checklist (README section under client/features/brochure and backend/app/routers/brochures.md):

Create draft → select template → choose property → edit content/branding → render → download.

Refresh the page mid-edit; ensure autosaved content returns.

Break network mid-render; see error toast and recover.

Verify final PDF typography/spacing are consistent with template.

No console errors, no unhandled promise rejections.

7) Deliverables Summary (only if no existing equivalents)

Backend

models/brochure.py, schemas/brochure.py, routers/brochures.py, services/render_service.py, templates/passo-building-v1.html (or SSR equivalent). Wire to main.py.

Frontend

features/brochure/pages/BrochureTemplates.tsx

features/brochure/pages/BrochureEditor.tsx

features/brochure/components/PreviewPane.tsx

features/brochure/templates/passo-building-v1/Layout.tsx

features/brochure/api/brochure.ts

features/brochure/hooks/useBrochureDraft.ts

Note: If similar files already exist, extend them instead of creating duplicates and keep imports/paths consistent with the rest of the application.

