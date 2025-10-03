# Frontend Unification Plan

- [x] Stage 1: Discovery & Planning
  - Audit `.claude` design guidance (claude.md, related files)
  - Review `frontend/docs` for product context
  - Inventory existing `frontend` and `mobile` codebases, capturing overlaps/gaps
  - Define success criteria aligned with PropertyPro AI principles

- [x] Stage 2: Structural Unification
  - Propose target directory structure for a unified frontend (web + mobile considerations)
  - Identify shared components/services to migrate or abstract
  - Outline required tooling/config updates (build, lint, assets, testing)
  - Prepare checklist of files to migrate vs deprecate

- [ ] Stage 3: Implementation & Cleanup
  - Execute migrations, updating imports and ensuring builds/tests pass
  - Remove or archive misaligned assets
  - Run mandated visual validation (Playwright workflow)
  - Document outcomes and provide follow-up recommendations

## Stage 1 Findings
- **Design guidance:** `.claude/claude.md`, `context/design_principles.md`, and `agents/design-reviewer.md` reinforce PropertyPro AI identity (blue/green/orange palette, voice-first controls, responsive 4/8/16 spacing, Playwright visual QA).
- **Product context:** `frontend/docs/PROJECT_CONTEXT_FOR_AGENTS.md` highlights the S.MPLE framework gaps (Marketing, Analytics, Social, Strategy, Packages, Transactions) and mandates mobile-first, AI-assisted workflows with React 19 + React Native Web foundation.
- **Codebase inventory:**
  - `frontend/src` contains rich desktop-first views plus some `.mobile.tsx` variants (e.g., `CommandCenter.mobile.tsx`, `DashboardView.mobile.tsx`, `PropertyDetail.mobile.tsx`).
  - `frontend/src/theme` holds tokens slated for rollout; stores/services live under `store/` and `services/`.
  - `mobile/src` mirrors high-level features with Expo/React Native components (e.g., `screens/DashboardScreen.tsx`, `components/DocumentManager.tsx`, `components/TransactionTimeline.tsx`).
  - Overlaps: Command Center, Document Manager, Transaction flows, BottomNav, analytics views; gaps include unified theme usage, shared audio/AI services, consistent navigation patterns.
- **Success criteria:** Unified experience must ship PropertyPro branding, voice-first surface parity, mobile/responsive coverage, shared data/services layer, Playwright validation baked into CI, and zero regressions to MarketingView, TransactionsView, and voice pipelines.

## Stage 2 Architecture Decisions
- **Target directory structure:**
```
client/
  apps/
    web/          # Vite React app (existing frontend/src migrated here)
    mobile/       # Expo/React Native app (existing mobile/src migrated here)
    preview/      # Storybook/Playwright visual review harness
  packages/
    ui/           # Cross-platform components (CommandCenter, Navigation, Cards)
    features/     # Domain modules (marketing, transactions, analytics)
    services/     # Shared API, voice, analytics, storage clients
    store/        # Zustand stores and hooks consumable by both apps
    theme/        # Tokens, typography, spacing, color system, theming helpers
  tooling/
    configs/      # tsconfig bases, eslint, metro/vite, jest/playwright configs
    scripts/      # Build/test/dev orchestration (turbo, npm scripts)
```
  - Monorepo managed via `npm workspaces` (existing root package.json) with dedicated `client/package.json` orchestrating workspace scripts.
- **Shared components/services to migrate:** Consolidate `frontend/src/components/*` and `mobile/src/components/*` into `packages/ui` with platform-specific subfolders (`/web`, `/native`), migrate cross-cutting logic like `CommandCenter`, `DocumentManager`, `TransactionTimeline`, `BottomNav`, `WaveformVisualizer`, and analytics widgets. Centralize voice + AI services (`frontend/src/services/audioService.ts`, `voiceService.ts`, `aiCoordinator.ts`) under `packages/services/voice`. Move Zustand stores (`frontend/src/store/*`) into `packages/store` for reuse; align constants/types from both apps into `packages/features/[domain]`.
- **Tooling & config updates:**
  - Create base TypeScript config in `tooling/configs/tsconfig.base.json`, extend per app with platform-specific module resolution.
  - Align ESLint/Prettier rules in `tooling/configs/eslint.config.js`; ensure React Native and web share alias maps.
  - Update build scripts: `apps/web` uses Vite; `apps/mobile` retains Expo/Metro with shared workspace dependencies; add Turborepo or npm scripts for parallel builds/tests.
  - Unify testing: reposition Playwright config in `client/apps/web/playwright.config.ts`; add Detox/Expo tests under `apps/mobile/tests`; share mock data via `packages/services/mocks`.
  - Centralize assets (icons, fonts, voice prompts) in `client/packages/assets` with platform-specific entry shims.
- **Migration / deprecation checklist:**
  - [x] Move `frontend/src/theme/*` to `client/packages/theme` and ensure tokens export platform-agnostic variants.
  - [ ] Relocate shared feature views (`frontend/src/components/MarketingView.tsx`, `TransactionsView.tsx`, `StrategyView.tsx`) into `client/packages/features/*` with web/mobile entrypoints.
  - [x] Extract voice + AI services (`frontend/src/services/audioService.ts`, `voiceService.ts`, `aiCoordinator.ts`) into `client/packages/services/voice` for unified consumption.
  - [x] Port `frontend/src/store/*` to `client/packages/store` and update both apps to consume workspace package.
  - [x] Replace duplicated mobile components (`mobile/src/components/DocumentManager.tsx`, `TransactionTimeline.tsx`, `TransactionTemplates.tsx`) with shared implementations under `client/packages/ui` using platform adapters.
  - [x] Sunset `frontend/legacy` and redundant `.mobile.tsx` duplicates after migrating to shared package imports.
  - [x] Align environment/config files (e.g., `frontend/src/config.ts`, `mobile/src/config.ts`) into `client/packages/services/config`.

## Stage 3 Preview
Implementation sequencing will follow the checklist above, pairing each migration with Playwright validation and Expo smoke tests before removing legacy assets.

## Stage 3 Implementation Progress
- Created `client/` workspace with `apps/web` (Vite) and `apps/mobile` (Expo) plus npm workspace orchestration under `client/package.json` and updated root workspaces.
- Extracted core tokens, Zustand stores, and service layer into `@propertypro/theme`, `@propertypro/store`, and `@propertypro/services`, wiring both apps through TS path aliases and lightweight re-export shims.
- Published shared data contracts in `@propertypro/features` and unified transaction UI via `@propertypro/ui` with `.web/.native` variants for DocumentManager, TransactionTimeline, and TransactionTemplates.
- Removed stale `frontend` / `mobile` roots and the `legacy` directory, replacing mobile/web config entrypoints with package-based re-exports.
- Outstanding: migrate feature views (Marketing/Transactions/Strategy) into `@propertypro/features`, regenerate workspace lockfiles, and run Playwright + Expo smoke validations before marking Stage 3 complete.


