# Frontend Architecture Deep Dive

> Web client root: `client/apps/web`
> Mobile client root: `client/apps/mobile`
> Shared packages root: `client/packages`
> Toolkit: React 18, Vite, TypeScript, Zustand, Expo, Playwright

---

## 1. Overview
1. The PropertyPro AI frontend stack consists of a monorepo workspace with shared packages powering both web (Vite + React) and mobile (Expo/React Native) applications.
2. Shared services, state stores, features, UI components, and theme tokens are published via `@propertypro/*` workspace aliases to ensure consistency across platforms.
3. The web client focuses on agent productivity dashboards, AI assistant interactions, property management, marketing automation, and analytics views.
4. The mobile client delivers core functionality optimized for on-the-go usage, reusing shared logic while adapting UI to native components.
5. Build tooling is centralized around Vite for web and Expo for mobile, with TypeScript project references enabling shared code validation.
6. Testing currently relies on Playwright for E2E coverage; unit and component test frameworks should be introduced to enhance quality.

---

## 2. Directory Map — Web Client (`client/apps/web`)
1. `App.tsx` — Root component orchestrating router setup, layout shells, global providers, and error boundaries.
2. `index.tsx` — Entry file bootstrapping React app, rendering `<App />` into DOM, and initializing service workers if configured.
3. `src/components` — Library of feature components (CommandCenter, ChatView, ContactManagementView, etc.) reused across screens.
4. `src/components/analytics` — Specialized components for charts, KPI cards, and analytics widgets.
5. `src/screens` — Route-level views combining multiple components into full workflows (Dashboard, Clients, Properties, etc.).
6. `src/services` — Web-specific service facades (currently `api.ts` re-exporting shared services) for HTTP communication.
7. `src/store` — Composition layer hooking shared Zustand stores into the web app (hydration, persistence, selectors).
8. `src/theme` — Web presentation layer customizing shared theme tokens for responsive breakpoints and typography.
9. `src/utils` — Helper functions (formatting, validation, feature toggles) used across components.
10. `src/compat` — Compatibility shims bridging shared logic with web-specific implementations.
11. `tests` — Playwright E2E tests (`e2e.spec.ts`) validating critical user journeys.
12. `docs` — Local documentation for web app (if present under `client/apps/web/docs`).
13. `vite.config.ts` — Vite bundler configuration, alias mapping, plugin definitions.
14. `playwright.config.ts` — Playwright test runner configuration with environment setup.
15. `tsconfig.json` — TypeScript compiler options and path aliases for workspace packages.

---
## 3. Component Library (`client/apps/web/src/components`)
1. `ActionButton.tsx` — Configurable CTA button with stateful styles, integrates with theme tokens.
2. `ActionCenter.tsx` — Aggregates quick actions for agents, linking to AI triggers and property workflows.
3. `ActionGrid.tsx` — Displays grid of shortcuts to features like report generation or campaign creation.
4. `BottomNav.tsx` and `BottomNav.mobile.tsx` — Responsive navigation components adapting to viewport size.
5. `ChatView.tsx` — AI assistant chat experience with conversation transcript, streaming responses, and actionable suggestions.
6. `ClientDetail.tsx` — Detailed view for a single client, including preferences, activity timeline, and AI insights.
7. `CommunicationHistory.tsx` — Timeline component showing emails, calls, and AI interactions with clients.
8. `CommandCenter.tsx` — Dashboard hub combining metrics, tasks, and quick actions for agents.
9. `ContactManagementView.tsx` — CRM table with filters, segmentation, and bulk actions.
10. `DashboardView.tsx` — Primary dashboard layout for desktop with widgets, charts, and AI cards.
11. `DashboardView.mobile.tsx` — Mobile-optimized dashboard view.
12. `DocumentManager.tsx` — Interface for uploading, tagging, and reviewing documents processed by backend.
13. `FeatureView.tsx` — Highlights premium features or upcoming releases, toggled via feature flags.
14. `Footer.tsx` — Footer with help links, legal information, and contact details.
15. `Header.tsx` — Top navigation bar showing user info, notifications, and quick links.
16. `LeadScoring.tsx` — Visualization for lead scoring metrics, pulling data from shared store.
17. `LoginView.tsx` — Authentication form integrating with shared `userStore` for login.
18. `MarketingView.tsx` — Overview of marketing campaigns, performance charts, and AI suggestions.
19. `MilestoneTracker.tsx` — Tracks progress of workflows (onboarding, transaction steps) with status indicators.
20. `PackageBuilder.tsx` — UI for constructing AI workflow packages from templates and custom steps.
21. `PackagesView.tsx` — Lists existing packages with execution status, linking to detailed logs.
22. `PackageTemplates.tsx` — Gallery of predefined workflow templates.
23. `PlatformConnections.tsx` — Manages integrations (CRM, social platforms) with connection status display.
24. `PlaywrightTestView.tsx` — Dedicated view for verifying end-to-end tests and scenarios.
25. `PostScheduler.tsx` — Scheduler interface for social media posts including calendar and channel selection.
26. `ProfileView.tsx` — Displays agent profile, performance stats, and configuration options.
27. `PropertyCard.tsx` — Card component showing property details, price, key metrics.
28. `PropertyDetail.tsx` and `PropertyDetail.mobile.tsx` — Detailed property view with tabs for data, documents, history.
29. `PropertyForm.tsx` — Form component for creating/editing property data, integrating validation and image upload.
30. `PropertySearch.tsx` — Search panel for filtering properties by criteria and invoking backend search endpoints.
31. `RequestCard.tsx` — Displays AI requests with status and actions.
32. `RequestsView.tsx` — Lists outstanding AI or workflow requests awaiting action.
33. `SocialCampaigns.tsx` — Provides analytics and controls for active social campaigns.
34. `SocialMediaView.tsx` — Comprehensive marketing UI with content library, scheduling, and analytics.
35. `SocialTemplates.tsx` — Template manager for social posts with editing capabilities.
36. `StrategyView.tsx` — Presents strategic AI recommendations for agents.
37. `TaskItem.tsx` — Represents individual task with status toggles and due dates.
38. `TasksView.tsx` — Kanban-style or list-based task management interface.
39. `TransactionsView.tsx` — Presents transaction list, statuses, and quick filters.
40. `TransactionTemplates.tsx` — Template set for transaction workflows and document bundles.
41. `TransactionTimeline.tsx` — Visual timeline for transaction events.
42. `ViewHeader.tsx` — Shared header component for screens, supporting breadcrumbs and actions.
43. `WaveformVisualizer.tsx` — Audio waveform visualization for voice features.
44. `WorkflowMonitor.tsx` — Displays workflow progress, step status, and live updates from backend.

---

## 4. Screen Architecture (`client/apps/web/src/screens`)
1. Screens act as routing endpoints composed of multiple components and data fetching hooks.
2. Common pattern: use Zustand selectors to pull data, call `apiGet` for initial load, display skeleton states.
3. Screens include `Dashboard`, `Clients`, `Properties`, `Transactions`, `Marketing`, `AIStudio`, `Documents`, `Workflows`, etc.
4. Each screen should encapsulate route-specific layout, breadcrumbs, and side navigation state.
5. Screens coordinate modals and overlays (e.g., new property modal, campaign wizard) triggered by child components.
6. Use React Router (or analogous library) configured in `App.tsx` to map routes to screen components.
7. Persist query params using hooks to maintain filter states when navigating back.
8. Provide consistent loading/error handling via shared components (e.g., `LoadingState`, `ErrorBoundary`).
9. Implement responsive design using CSS modules or styled components with theme tokens.
10. Align screen metadata (title, description) with analytics tracking for page views.

---
## 5. Shared Services Package (`client/packages/services/src`)
1. `api.ts` — Central HTTP client providing `apiGet`, `apiPost`, `apiPut`, `apiPatch`, `apiDelete`, and `apiRequest` functions that auto-attach JWT tokens from `useUserStore`.
2. `api.ts` handles network errors, attempts JSON parsing, and triggers logout on HTTP 401 responses.
3. `aiCoordinator.ts` — Coordinates AI chat flow, streaming updates, concurrency control, and message queueing for UI components.
4. `audioService.ts` — Manages audio recording/playback utilities shared between web and mobile.
5. `marketingService.ts` — Encapsulates marketing-specific endpoints (campaigns, templates, analytics) for reuse across apps.
6. `socialMediaApi.ts` — Interfaces with backend social endpoints, exposing functions for scheduling, status retrieval.
7. `userService.ts` — Provides user profile fetch/update, password management, and authentication helpers.
8. `workflowEngine.ts` — Controls AI package operations, retrieving package definitions, starting/resuming workflows.
9. `config.ts` — Defines base API URL and environment-specific settings consumed by service functions.
10. `index.ts` — Re-exports modules for easier consumption from applications.

---

## 6. Shared Store Package (`client/packages/store/src`)
1. Store architecture uses Zustand with typed stores for domain entities.
2. `userStore.ts` — Manages auth tokens, user profile data, login/logout actions, persisted to storage.
3. `clientStore.ts` — Stores client list, filters, selected client, and actions to fetch/update data via services.
4. `propertyStore.ts` — Maintains property collection, search filters, sorting, and detail caching.
5. `transactionStore.ts` — Tracks transactions, statuses, and computed metrics for dashboards.
6. `uiStore.ts` — Keeps UI preferences (theme mode, layout), panel visibility, modals state.
7. `types.ts` — Shared types and interfaces for store shapes and actions.
8. `index.ts` — Aggregates exports for easy import into apps.
9. Stores leverage selectors to minimize re-renders and support cross-app usage.
10. Persistence is typically implemented using Zustand middleware (localStorage for web, AsyncStorage for mobile) once configured.

---

## 7. Shared UI & Theme Packages
1. `client/packages/ui` — Common UI components (buttons, cards, forms, modals) for cross-platform design consistency.
2. `client/packages/theme` — Design tokens (colors, spacing, typography, shadows) exposed as TypeScript modules.
3. `client/packages/theme` integrates with styled-system (if present) or custom theme provider consumed by both apps.
4. Ensure new UI components rely on theme tokens instead of hardcoded values for portability.
5. Maintain component documentation (Storybook recommended) to align on usage patterns.
6. `client/packages/assets` — Stores icons, images, and static assets referenced by UI.
7. `client/packages/features` — Advanced feature modules (property comparisons, campaign builders) shared between apps.
8. Adopt consistent naming and file structure within packages to ease discovery.
9. Update package `README` files to document components and usage guidelines.
10. Consider publishing packages privately if other repositories need to consume them.

---

## 8. Web Build & Tooling
1. `vite.config.ts` configures path aliases (`@propertypro/services`, etc.), env variables, build output directory (`dist`), and plugins.
2. Vite dev server supports hot module reload for rapid development; ensure environment variables prefixed with `VITE_` when needed.
3. `tsconfig.json` extends base config from workspace, defines JSX settings, path mappings.
4. `package.json` (web) includes scripts: `dev`, `build`, `preview`, `lint`, `test` (if configured).
5. Playwright integrated via `playwright.config.ts` with test directory `tests/` and HTML reporter.
6. Use ESLint and Prettier (configure at root) to maintain code style.
7. Web assets built into `dist/`, served by static hosting or integrated into backend.
8. Integrate environment-specific configs via `.env` files (e.g., `.env.development`, `.env.production`).
9. Consider using Vite plugin for PWA if offline features required.
10. Ensure build pipeline includes type checking (`tsc --noEmit`) for catch errors before deployment.

---

## 9. Mobile Build & Tooling (`client/apps/mobile`)
1. `App.tsx` registers navigation stacks, global providers, error boundaries, and root screens for Expo app.
2. `app.json` and `app.config.js` define Expo configuration (app name, icon, permissions).
3. `src/components` mirrors web components but uses React Native primitives.
4. `src/screens` provides mobile-specific screen compositions (Dashboard, Chat, CRM) using React Navigation.
5. `src/services` reuses shared service functions, adding mobile-specific integrations (voice, push notifications).
6. `config.ts` sets API base URL, feature toggles tailored for mobile context.
7. `constants.ts` / `types.ts` align with shared TypeScript types for parity with web.
8. `tsconfig.json` configures path aliases identical to web for shared packages.
9. Mobile CLI commands: `npm run start --workspace @propertypro/mobile` to launch Expo dev server.
10. For native builds, integrate EAS or bare React Native pipeline; document prerequisites (Xcode, Android Studio).

---
## 10. Data Flow & State Management
1. Components fetch data through service functions returning promises; results stored in Zustand stores for reuse.
2. Use `useEffect` hooks to trigger data fetch on mount; ensure cleanup for subscriptions (WebSocket, event listeners).
3. UI components subscribe to store slices via selectors to minimize re-renders.
4. Actions within stores encapsulate API calls and state updates, handling loading/error states internally.
5. For derived data (e.g., aggregated metrics), use memoized selectors to avoid expensive recomputation.
6. Persist critical state (auth tokens, preferences) using storage middleware; implement hydration on app start.
7. For WebSocket streams (chat, ML), integrate event listeners updating store state incrementally.
8. Maintain normalized data structures (maps keyed by ID) for clients/properties to speed lookups.
9. Use optimistic updates for quick UI feedback, rolling back on API failure.
10. Document store contracts (actions, selectors) to guide component usage.

---

## 11. API Integration Pattern
1. All HTTP calls funnel through `apiRequest` in `client/packages/services/src/api.ts`, ensuring consistent headers and error handling.
2. For multipart uploads, pass `FormData`; `apiRequest` removes `Content-Type` to let browser set boundary.
3. Handle error responses by catching thrown Error instance, display user-friendly messages via toast/snackbar.
4. Use async thunks (within store actions) to sequence API call -> state update -> notification.
5. Web app should maintain global error boundary to capture unhandled exceptions.
6. For streaming AI responses, integrate fetch streaming or WebSocket messages into component state updates.
7. Implement request cancellation (AbortController) for long-running fetches when component unmounts.
8. Align API route paths with backend docs to avoid discrepancies; maintain TypeScript enums for endpoint constants.
9. For analytics instrumentation, log API successes/failures to monitoring service for frontend reliability insights.
10. Add integration tests verifying API contract using MSW (Mock Service Worker) once unit tests introduced.

---

## 12. Theming & Styling
1. Shared theme tokens define color palette (primary, secondary, status), typography scales, spacing, radii.
2. Web uses CSS-in-JS or CSS modules referencing tokens via `theme` utilities.
3. Mobile uses styled components or StyleSheet referencing the same tokens for visual parity.
4. Maintain dark mode support by toggling theme values via `uiStore` preference.
5. Ensure accessibility (contrast ratios, font sizes) across components; include guidelines in package docs.
6. Provide consistent spacing grid; components adhere to baseline spacing units.
7. Use responsive breakpoints defined in theme for layout adjustments (desktop/tablet/mobile).
8. Document design system updates in `client/packages/ui` README and align with design team specs.
9. Introduce Storybook/Expo Storybook for component previews and regression testing.
10. Use CSS variables or theme context to support runtime theming adjustments.

---

## 13. Frontend Testing Strategy
1. Current coverage: Playwright E2E test (`client/apps/web/tests/e2e.spec.ts`) hitting marketing dashboard scenario.
2. Expand Playwright suite to cover login, property CRUD, AI chat flows, campaign scheduling, and document upload.
3. Introduce component tests using React Testing Library with Jest or Vitest, mocking API responses via MSW.
4. Add unit tests for Zustand stores to verify state transitions under various scenarios.
5. Implement regression screenshot tests for critical UI components (command center, dashboards).
6. For mobile, adopt Detox or Expo E2E harness to validate navigation and core flows.
7. Add lint/test scripts to CI; fail pipeline on test failure or lint errors.
8. Maintain test data fixtures mirroring backend schema to catch contract misalignments.
9. Use accessibility testing tools (axe) to ensure UI meets WCAG guidelines.
10. Document testing matrix and coverage goals in repository README or dedicated doc.

---

## 14. Performance Optimization Guidelines
1. Utilize code splitting (dynamic imports) for heavy screens to reduce initial bundle size.
2. Memoize components (`React.memo`) and values (`useMemo`, `useCallback`) when props cause unnecessary re-rendering.
3. Use virtualization (e.g., `react-window`) for large tables/lists (client list, property list).
4. Cache API responses using SWR/React Query (consider addition) or manual caching in stores.
5. Optimize images via responsive sources, lazy loading, and asset compression.
6. Monitor bundle size using Vite's build output; track increases over time.
7. Avoid unnecessary rerenders by using Zustand selectors instead of subscribing to entire state slices.
8. Defer non-critical API calls until after first paint to improve perceived performance.
9. Implement skeleton loaders and progressive enhancement for AI streaming responses.
10. Profile mobile app using React Native debugger to catch performance bottlenecks on lower-end devices.

---

## 15. Accessibility & UX Considerations
1. Provide keyboard navigation across interactive elements (tab order, focus states).
2. Add ARIA labels to icons and non-text buttons for screen readers.
3. Ensure color contrast meets accessibility guidelines; rely on theme tokens tested for contrast.
4. Provide alt text for images, especially property photos and icons conveying meaning.
5. Support adjustable font sizes; respond to browser zoom and system accessibility settings.
6. For AI chat, provide text-to-speech and speech-to-text toggles with accessible controls.
7. Validate forms with inline error messages and screen reader-friendly cues.
8. Ensure modals focus trap, return focus to trigger on close, and support ESC closing.
9. Document accessibility testing steps and include them in QA checklists.
10. Gather accessibility feedback from users and incorporate into backlog.

---
## 16. Environment Configuration
1. Web app expects base API URL provided via Vite env variable or `client/packages/services/src/config.ts` default.
2. Mobile app reads environment from `config.ts`; ensure values align with backend environment (dev/staging/prod).
3. API base should point to backend host accessible from browser/mobile (handle CORS for web, proper host for mobile).
4. Configure feature flags via shared config or future feature flag service for consistent toggling across clients.
5. Secure storage of tokens: web uses localStorage/sessionStorage; mobile uses secure storage (expo-secure-store) when integrated.
6. Provide `.env` files for each workspace documenting expected keys; avoid committing secrets.
7. Document environment setup steps for QA/staging (API endpoints, credentials).
8. Handle environment-specific asset loading (logos, colors) via configuration.
9. Manage analytics instrumentation keys per environment to avoid mixing data streams.
10. Document CORS requirements and ensure `app/core/settings.py` includes web origins for each environment.

---

## 17. Release Workflow (Frontend)
1. Align releases with backend readiness; ensure API changes deployed before frontend expecting them.
2. Update version numbers in `package.json` (web/mobile) and shared packages when publishing.
3. Run `npm run lint` and relevant tests before creating release candidate.
4. Build web app (`npm run build --workspace @propertypro/web`) and upload artifacts to hosting platform (S3/CloudFront/etc.).
5. For mobile, run Expo build pipeline (EAS) producing iOS/Android binaries; follow store submission guidelines.
6. Update release notes referencing new features, bug fixes, and documentation updates.
7. Smoke test production build with critical user journeys (login, property search, AI chat, campaign creation).
8. Monitor frontend logs and analytics post-release to detect regressions.
9. Rollback plan: maintain previous build artifacts and ability to deactivate features via flags.
10. Update `docs/progress/release-readiness.md` with frontend readiness evidence (build logs, test reports).

---

## 18. Analytics & Telemetry
1. Capture page views and user interactions (buttons, forms) using analytics SDK integrated in `App.tsx`.
2. Track AI chat usage (messages sent, response latency) from frontend to complement backend metrics.
3. Monitor marketing campaign creation/edit frequency to inform UX improvements.
4. Log performance metrics (TTFB, CLS, LCP) to analytics for real user monitoring (RUM).
5. Ensure analytics events include context (user role, tenant) while respecting privacy policies.
6. Provide opt-in/out mechanisms for analytics tracking to comply with regulations.
7. Align event naming conventions across web and mobile for unified dashboards.
8. Document analytics schemas and dashboards for product stakeholders.
9. Use analytics to drive feature adoption strategies (tooltips, guided tours).
10. Integrate error tracking (Sentry) to capture frontend exceptions with stack traces.

---

## 19. Voice & Audio Integration
1. `client/packages/services/src/voiceService.ts` handles audio capture, streaming to backend voice endpoints, and playback of responses.
2. `audioService.ts` offers lower-level controls (start/stop recording, encode audio) shared across components.
3. Web uses Web Audio API; ensure microphone permissions requested gracefully.
4. Mobile leverages Expo AV module; request runtime permissions for microphone on iOS/Android.
5. Visual feedback via `WaveformVisualizer.tsx` indicates active recording; ensure accessible alternative text.
6. Handle network latency/resilience by buffering audio and retrying upon failure.
7. Provide fallback text input for users unable to use voice features.
8. Secure voice data transmission using HTTPS and short-lived tokens.
9. Document storage/retention policies for recorded audio to satisfy compliance.
10. Monitor voice feature usage for improvements to transcription accuracy.

---

## 20. Collaboration & Design Handoff
1. Sync with design team on Figma updates; map design tokens to theme package promptly.
2. Document component API (props, expected usage) in `client/packages/ui` README or Storybook.
3. Maintain changelog for shared packages to inform downstream consumers.
4. Provide preview deployments (Vercel/Netlify) for web to gather stakeholder feedback quickly.
5. For mobile, share Expo preview builds with testers via Expo Go links.
6. Keep backlog of UX debt items (accessibility, responsiveness) and prioritize regularly.
7. Include designers in code reviews for major UI changes to ensure alignment.
8. Use design review scripts (`design-review-dashboard.js`) to generate visual diffs where applicable.
9. Document cross-team dependencies (backend endpoints, data availability) for new features.
10. Capture UX research findings in `docs/business` and reference from frontend roadmap.

---
## 21. Component & Store Cross-Reference
1. `CommandCenter.tsx` -> consumes `clientStore`, `propertyStore`, `transactionStore` for aggregated stats.
2. `ContactManagementView.tsx` -> interacts with `clientStore` actions (`fetchClients`, `updateClient`).
3. `PropertyForm.tsx` -> uses `propertyStore` for state, `apiPost` for create, `apiPut` for update.
4. `TasksView.tsx` -> relies on `uiStore` for filter state and `workflowEngine` for task operations.
5. `MarketingView.tsx` -> calls `marketingService` functions (`getCampaigns`, `launchCampaign`), updates `uiStore` toggles.
6. `ChatView.tsx` -> uses `aiCoordinator` to stream messages, persists transcripts in `session` state slices.
7. `Analytics` components -> fetch data from `apiGet('/analytics/summary')`, store results in `uiStore` or local state depending on reuse.
8. `SocialMediaView.tsx` -> uses `socialMediaApi` for scheduling, `marketingService` for templates.
9. `DocumentManager.tsx` -> interacts with `documents` slice (planned), uses `apiPost` for uploads.
10. `LoginView.tsx` -> dispatches `userStore.login(email, password)` which calls backend and stores tokens.
11. `DashboardView.tsx` -> aggregates multiple selectors to display combined analytics.
12. `WorkflowMonitor.tsx` -> polls `workflowEngine.getPackageStatus` and updates local state.
13. `WaveformVisualizer.tsx` -> listens to `voiceService` events for amplitude data.
14. `ProfileView.tsx` -> uses `userService` to update profile details, toggles `uiStore` theme settings.
15. `RequestsView.tsx` -> queries `task_orchestration` endpoints via `workflowEngine` functions.

---

## 22. Navigation & Routing
1. Configure React Router routes in `App.tsx` mapping URLs (`/dashboard`, `/clients`, `/properties`, `/ai`, `/marketing`, `/reports`, `/settings`).
2. Use nested routes for subsections (e.g., `/marketing/campaigns`, `/marketing/social`).
3. Implement guard routes requiring authentication; redirect to login if tokens missing.
4. Preserve scroll position per route when navigating via `ScrollRestoration` or custom hooks.
5. Provide deep linking support for specific records (e.g., `/properties/:propertyId`).
6. Maintain navigation state in `uiStore` to highlight active menu items.
7. Use React Router `Loader` or custom data prefetch for heavy pages.
8. For mobile, use React Navigation stacks/tabs with consistent route names and parameters.
9. Document route map for QA to design test cases.
10. Handle 404 route gracefully with branded error page linking to key sections.

---

## 23. Error Handling & Notifications
1. Centralize notifications using context (e.g., `ToastProvider`) to deliver success/error messages.
2. Catch API errors in store actions, log to console in development, and show user-friendly message.
3. Provide fallback UI for major sections when data fails to load (retry button, support link).
4. Use error boundaries around large sections (AI chat, property forms) to prevent entire app crash.
5. Log errors to monitoring service (Sentry) with user/tenant context.
6. On token expiration, redirect to login with message preserving navigation target for after login.
7. Document standard error codes and copy in design guidelines for consistency.
8. Ensure mobile app handles offline/poor network gracefully with offline banners and queued actions.
9. Provide instrumentation to track error frequency for prioritizing bug fixes.
10. Add developer mode toggles to enable verbose logging in non-production builds.

---

## 24. Internationalization & Localization (Future)
1. Current copy is English; plan i18n integration using libraries (react-intl, i18next) as market expands.
2. Extract strings into translation files; provide keys for components/screens.
3. Ensure date/number formatting uses locale-aware functions.
4. Support RTL layout adjustments for languages like Arabic.
5. Adjust font stack to support multilingual character sets.
6. Provide translation context to AI prompts to match user language preference.
7. Coordinate with backend to return localized data where applicable.
8. Document translation workflows for localization team.
9. Add language switcher in UI once multiple locales supported.
10. Include localization tests verifying formatting and layout adjustments.

---

## 25. Dev Tooling & Productivity
1. Configure ESLint with workspace-aware aliases to avoid false positives.
2. Integrate VS Code settings (`.vscode/settings.json`) to enforce formatting and auto-import behavior.
3. Provide CLI scripts for generating new components/screens with standard template.
4. Document debugging tips (Redux DevTools compatible with Zustand via middleware, React Profiler usage).
5. Use Git hooks (Husky) to run lint/tests on commit once approved.
6. Maintain snippet library for common patterns (API call + store update, skeleton loader, modal structure).
7. Encourage component-driven development via Storybook or Chromatic for UI review.
8. Add stylelint if using CSS modules to enforce consistent rules.
9. Provide instructions for linking local backend and using mock servers when backend unavailable.
10. Document how to update shared packages (bump version, run tests) to avoid breaking apps.

---

## 26. Mobile-Specific Considerations
1. Manage navigation stacks with React Navigation; ensure deep link handling for push notifications.
2. Implement offline caching for key data (client list, property list) using AsyncStorage or SQLite.
3. Optimize images for mobile (progressive loading, caching).
4. Support biometric authentication (Face ID/Touch ID) for quick login once backend supports refresh tokens.
5. Handle push notifications for tasks, AI responses; integrate with Expo Notifications or native providers.
6. Provide accessibility features (VoiceOver, TalkBack) with proper labels and focus management.
7. Monitor performance on low-end devices; avoid heavy animations or large lists without virtualization.
8. Support background sync for tasks requiring timely updates (nurturing actions).
9. Manage app version updates, prompting users to update when backend features require latest client.
10. Document mobile QA process (devices, OS versions, test cases) to ensure coverage.

---

## 27. Future Enhancements (Frontend)
1. Implement design system documentation site with live examples.
2. Introduce advanced analytics dashboards with drill-down interactions and saved views.
3. Add collaboration features (shared notes, mentions) across clients/properties.
4. Integrate guided onboarding tours for new agents leveraging `uiStore` flags.
5. Support offline-first workflows for mobile, syncing when connectivity returns.
6. Add inline AI suggestions in forms (property descriptions, email drafts).
7. Provide customization of dashboards (drag-and-drop widgets) persisted per user.
8. Implement theming for brokerage branding (colors, logos) via dynamic theme overlay.
9. Build extension APIs for third-party integrations in frontend (plugin system).
10. Expand testing infrastructure with visual regression and performance budgets.

---

## 28. Documentation Maintenance
1. Update component descriptions when significant UI changes occur.
2. Maintain mapping between backend endpoints and frontend consumers to ease integration testing.
3. Document cross-browser compatibility considerations noted during QA.
4. Keep mobile device support matrix current (minimum OS versions, tested devices).
5. Log UX research findings influencing UI decisions; link to design documentation.
6. Provide quickstart guides for new frontend contributors referencing this handbook.
7. Archive deprecated components/screens with notes on replacements.
8. Update `CHANGELOG.md` or workspace-specific changelog with every release affecting UI.
9. Sync with backend handbook when API behavior changes to ensure frontend docs accurate.
10. Conduct documentation review quarterly along with codebase audit.

---
## 29. Reference Checklist For Feature Development
1. Confirm backend endpoints exist and documented in API docs.
2. Define data models and update TypeScript interfaces in shared packages.
3. Plan state management strategy (new store slice vs existing slice extension).
4. Create UI design in Figma with responsive breakpoints and accessibility notes.
5. Scaffold components/screens following established folder structure.
6. Implement service functions calling backend endpoints with error handling.
7. Wire components to Zustand stores and ensure loading/error states handled.
8. Write unit tests for stores/components; add Playwright scenario if end-to-end flow impacted.
9. Update documentation (this handbook, changelog, onboarding guides) with new feature info.
10. Coordinate with QA for test plan and regression coverage.

---

## 30. Appendix A — Web Route Table (Illustrative)
1. `/login` -> `LoginView.tsx`
2. `/dashboard` -> `DashboardView.tsx`
3. `/clients` -> `ClientsScreen.tsx`
4. `/clients/:clientId` -> `ClientDetail.tsx`
5. `/properties` -> `PropertiesScreen.tsx`
6. `/properties/new` -> `PropertyForm.tsx`
7. `/properties/:propertyId` -> `PropertyDetail.tsx`
8. `/transactions` -> `TransactionsView.tsx`
9. `/marketing` -> `MarketingView.tsx`
10. `/marketing/campaigns` -> `CampaignsScreen` (compose components)
11. `/marketing/social` -> `SocialMediaView.tsx`
12. `/ai` -> `CommandCenter.tsx` + `ChatView.tsx`
13. `/ai/chat` -> `ChatView.tsx`
14. `/reports` -> `ReportsScreen`
15. `/documents` -> `DocumentManager.tsx`
16. `/workflows` -> `WorkflowsScreen`
17. `/workflows/packages` -> `PackagesView.tsx`
18. `/settings/profile` -> `ProfileView.tsx`
19. `/settings/team` -> `TeamManagementScreen`
20. `/analytics` -> `AnalyticsDashboard`
21. `/voice` -> `VoiceAssistantScreen`
22. `/support` -> `SupportCenter` or knowledge base link
23. `/404` -> `NotFoundPage`
24. Default route -> redirect to `/dashboard` when authenticated.

---

## 31. Appendix B — Mobile Route Table (Illustrative)
1. `DashboardStack` -> `DashboardScreen.tsx`
2. `ClientsStack` -> `ClientsScreen.tsx`, `ClientDetailScreen.tsx`
3. `PropertiesStack` -> `PropertiesScreen.tsx`, `PropertyDetailScreen.tsx`
4. `TransactionsStack` -> `TransactionsScreen.tsx`
5. `ChatStack` -> `ChatScreen.tsx`
6. `MarketingStack` -> `MarketingScreen.tsx`
7. `TasksStack` -> `TasksScreen.tsx`
8. `SettingsStack` -> `SettingsScreen.tsx`, `ProfileScreen.tsx`
9. Modal routes: `CreatePropertyModal`, `ScheduleCampaignModal`, `VoiceInputModal`
10. Tab navigator includes Dashboard, CRM, AI, Marketing, More sections.
11. Deep links: `propertypro://property/:id`, `propertypro://client/:id`, `propertypro://chat/:sessionId`.
12. Handle push notification navigation via linking to appropriate stack and params.

---

## 32. Appendix C — Shared Package Index
1. `@propertypro/services` -> API client, AI coordinator, marketing/social services.
2. `@propertypro/store` -> Zustand stores for user, clients, properties, transactions, UI.
3. `@propertypro/ui` -> Shared UI primitive components.
4. `@propertypro/theme` -> Theme tokens and providers.
5. `@propertypro/features` -> Feature-level logic modules.
6. `@propertypro/assets` -> Icons, illustrations, audio cues.
7. `@propertypro/web` (if present) -> Web-specific utilities.
8. Ensure package versions remain in sync; update workspace dependencies as changes occur.

---

## 33. Appendix D — Testing Backlog
1. Add Playwright test covering AI chat messaging with streaming responses.
2. Add Playwright test for property creation and validation errors.
3. Add Playwright test for marketing campaign scheduling and status update.
4. Add Playwright test for document upload and preview.
5. Create React Testing Library suite for `CommandCenter` aggregations.
6. Create store unit tests for `clientStore` and `propertyStore` update flows.
7. Create voice feature tests simulating microphone input.
8. Implement mobile snapshot tests for key screens to catch layout regressions.
9. Add integration tests verifying shared services handle error scenarios gracefully.
10. Track coverage metrics and display in CI for transparency.

---

## 34. Appendix E — Performance Budget Targets
1. Web initial load bundle: target < 2.5 MB gzipped.
2. Web LCP (Largest Contentful Paint): < 2.5s on median devices.
3. Web TTI (Time to Interactive): < 3s on broadband connections.
4. Mobile app startup: < 2s cold start on modern devices.
5. AI chat response latency: < 2s for initial token streaming with caching.
6. Property list infinite scroll: maintain 60 FPS while scrolling.
7. Voice transcription: < 1s delay between speech segments and text display.
8. Document list load: paginate to avoid API responses >1 MB.
9. Dashboard render: ensure charts load progressively, with skeletons shown < 200ms.
10. Monitor metrics after each release and adjust budgets as features evolve.

---

## 35. Appendix F — Revision Log
1. 2025-10-02 — Extensive frontend documentation generated to align with current monorepo structure.

---
