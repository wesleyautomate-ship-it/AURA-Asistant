# UI Notes

## 2025-10-14 - Brochure Quick Action Alignment
- Dashboard quick action modal mirrors card spacing from `screenshots/dashboard_baseline.png` and `screenshots/command_center_baseline.png`.
- Content Viewer brochure layout reuses BottomDock actions and matches the two-column structure in `screenshots/tasks_baseline.png`, adding print and PDF affordances.

## 2025-10-14 - Placeholder Route Cards
- Marketing, Contacts, and Properties placeholders reuse dashboard gradients and centered cards so interim screens stay aligned with `screenshots/dashboard_baseline.png`.

# Smart Dashboard — AI Workflows

Overview
- Introduced a unified "AI Workflows" section under the core CRM cards.
- Property Brochure moved here; no longer surfaced in the hero carousel.
- Added placeholders: CMA Report and Social Post. Both use the same card style, hover, and spacing as CRM tiles.

Layout
- Order: Hero Carousel → CRM Modules (Properties, Contacts, Requests, Marketing) → AI Workflows.
- AI Workflows uses a Tailwind grid: `grid-cols-1 sm:grid-cols-2`, keeping gap `gap-4 sm:gap-6`.
- Section title uses `text-lg font-semibold text-gray-800`; subtitle uses `text-sm text-gray-600`.

Interactions
- Property Brochure: triggers existing `handleGenerateBrochure()` pipeline.
- CMA Report: placeholder `handleGenerateCMA()` (Phase 3.3).
- Social Post: placeholder `handleGenerateSocialPost()`.

Screenshots
- Baseline reference: `screenshots/dashboard_baseline.png`.
- New: `screenshots/dashboard_aiworkflows.png` (capture after running the dev server).
