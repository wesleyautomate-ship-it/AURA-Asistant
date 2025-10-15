# Realtor Assistant Changelog

## 2025-10-14 Phase 3.2.1 - Placeholder Routes

### Frontend
- Added placeholder pages and routes for Marketing, Contacts, and Properties so dashboard navigation no longer triggers missing route warnings.

## 2025-10-14 Phase 3.2 – Brochure Generator Activation

### Frontend
- Enabled the dashboard “Generate Brochure” quick action with a streaming preview modal that mirrors the spacing and typography in `screenshots/dashboard_baseline.png` and `screenshots/command_center_baseline.png`.
- Added a Property Brochure layout inside the Content Viewer, including two-column details plus print/PDF actions aligned to `screenshots/tasks_baseline.png`.

### API & Services
- Extended `intelligenceApi` with `generateBrochure` and SSE logging so brochure tasks reuse the Command Center progress pipeline.
- Saved generated brochures into the intelligence store using the new mapper for `PROPERTY_BROCHURE` content.

### QA
- Captured a manual Playwright scaffold (`tests/ui_brochure.spec.ts`) describing the brochure generation walkthrough.

### Documentation
- Noted the baseline screenshot set from `/screenshots/` as the alignment reference for the activated UI.


All notable changes to the PropertyPro AI workspace are documented in this file. Dates use YYYY-MM-DD.

## 2025-10-02 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Workspace Unification & CI Hardening

### Frontend
- Replaced the legacy `frontend` roots with a npm workspace structure (`client/package.json`) containing `apps/web`, `apps/mobile`, and shared packages.
- Web app now re-exports shared modules for marketing, transactions, strategy, and document flows from `@propertypro/features` and `@propertypro/ui` (see `client/apps/web/src/components/MarketingView.tsx`, `client/apps/web/src/components/DocumentManager.tsx`).
- Added a guarded login view that calls `@propertypro/services/userService` to obtain JWTs before loading feature stores (`client/apps/web/src/components/LoginView.tsx`).
- Marketing view now consumes live property data via shared store hooks and surfaces a seeded-listing helper when environments start empty (`client/packages/features/src/marketing/MarketingView.*`).
- Playwright smoke scenarios updated with accessible selectors that exercise the marketing workflow (`client/apps/web/tests/e2e.spec.ts`).
### Mobile
- Expo app updated to source Marketing, Strategy, and Transactions screens from shared feature modules (`client/apps/mobile/src/screens`).
- Transaction and document components proxy the shared UI package to keep parity with the web experience (`client/apps/mobile/src/components/TransactionTimeline.tsx`, `TransactionTemplates.tsx`).
- Harmonized config stubs (`client/apps/mobile/src/config.ts`) so both runtimes resolve the same API base.

### Shared Packages & Services
- Introduced `client/packages/features` with `.web`/`.native` variants for marketing, strategy, and transaction experiences.
- Added `client/packages/ui` for transaction-focused primitives and `client/packages/services` for API wrappers, marketing services, and the new `aiCoordinator.ts`.
- Normalized state management in `client/packages/store`, including REST-backed property/client stores and persisted auth sessions.

### Platform & Tooling
- Expanded CI workflow to run backend pytest, Alembic dry-run, web lint/type-check/build, and Playwright smoke tests (`.github/workflows/ci.yml`).
- Documented the Alembic migration workflow (`backend/app/alembic/README`) and aligned progress tracking in `docs/progress/ci-migration-plan.md`.
- Added a reusable sample-property seeding script (`scripts/seed_sample_property.js`) and wired CI to publish pytest coverage plus Playwright HTML artefacts.
### Documentation
- Archived superseded documentation and introduced the handbook-based structure under `docs/handbook` plus progress trackers in `docs/progress`.
- Updated roadmap and content guides (`docs/PROPERTYPRO_AI_ROADMAP.md`, `docs/CONTENT_GENERATION_GUIDE.md`) to reflect the new architecture.

## 2025-09-24 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ React Native Migration Foundations
- Established shared theming, spacing, and typography primitives for cross-platform UI (`client/packages/theme`).
- Migrated marketing, dashboard, and tasks flows into modular components and screens, paving the way for `.native` variants.
- Captured refactor manifests and lint results to baseline quality before the workspace split.

## 2025-09-15 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ Initial Consolidation & Audit
- Merged the separate mockup, mobile, and web directories into a single codebase for assessment.
- Produced audit reports and migration plans to guide design system unification and backend hardening (`audit_report.md`, `frontend_unification_plan.md`).
- Staged initial CI diagnostics and documented outstanding risks for follow-up.

## v3.x.x - Dashboard AI Workflows Section

- Added unified AI Workflows section on Smart Dashboard.
- Moved Property Brochure into AI Workflows (removed from hero area).
- Added placeholders for CMA Report and Social Post with click handlers.
- Kept card styles, spacing, and responsiveness consistent with baseline.
