# Aura Content Templates Reference

This directory provides reference layouts, tone, and structural examples for AI-generated content in Aura.

Each file here represents a **content archetype** used by the Template Orchestrator (`templateOrchestrator.ts`) and Workflow API (`workflowApi.ts`).

---

## 📊 1. Competitive Analysis (`1 competitive analysis.pdf`)
Use for:
- Market insights or investor research summaries
- CMA and analytics-based reports
Structure:
- Executive Summary
- Competitor Comparison Table
- Visual Market Insights
- Recommendations

---

## 🏡 2. Brochure Template (`Brochure template.pdf`)
Use for:
- Property listings, promotional materials
- Quick, visually appealing client handouts
Structure:
- Hero image or property visual
- Tagline & CTA
- Property highlights, pricing, contact info

---

## 💼 3. Investor Pitch Deck (`investor pitch deck.pdf` / `(1).pdf`)
Use for:
- AI-generated real estate investment decks
- Client proposals and business presentations
Structure:
- Title / Problem / Market Opportunity
- Team & Product Vision
- Financial Summary & CTA
Formatting:
- Slide-based, 8–10 pages
- Professional tone, minimal text, high visual density

---

## 📰 4. Newsletters (`Newsletter 1.pdf`, `Newsletter 2.pdf`)
Use for:
- Automated weekly updates, client communications
Structure:
- Headline & greeting
- Market update
- Featured listings or insights
- Closing CTA
Tone:
- Conversational, informative, brief (2–3 paragraphs max)

---

## 🧠 How to Use These Templates

1. When generating content via `templateOrchestrator.ts`, reference this folder as a **style and structure guide**.
2. Use `query` or `intent` type (e.g., `CMA_REPORT`, `PITCH_DECK`, `NEWSLETTER`) to determine which PDF structure to emulate.
3. When rendering in the frontend (`CMAReport.tsx`, `DeckBuilder.tsx`), use section titles and layout order inspired by these examples.
4. For exports (PDF/HTML), match the typography hierarchy and visual balance observed here.

---

## 🔗 Integration with Build Phases
These files are referenced in:
- Phase 3.1: Content Generation System
- Phase 3.2: Report Rendering & Export Pipeline
- Phase 4: AI Narrative Enhancement and Visual Design
