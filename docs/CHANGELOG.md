# Realtor Assistant Changelog

All notable changes to the PropertyPro AI workspace are documented in this file. Dates use YYYY-MM-DD.

## 2025-10-02 Ã¢â‚¬â€œ Workspace Unification & CI Hardening

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

## 2025-09-24 Ã¢â‚¬â€œ React Native Migration Foundations
- Established shared theming, spacing, and typography primitives for cross-platform UI (`client/packages/theme`).
- Migrated marketing, dashboard, and tasks flows into modular components and screens, paving the way for `.native` variants.
- Captured refactor manifests and lint results to baseline quality before the workspace split.

## 2025-09-15 Ã¢â‚¬â€œ Initial Consolidation & Audit
- Merged the separate mockup, mobile, and web directories into a single codebase for assessment.
- Produced audit reports and migration plans to guide design system unification and backend hardening (`audit_report.md`, `frontend_unification_plan.md`).
- Staged initial CI diagnostics and documented outstanding risks for follow-up.
