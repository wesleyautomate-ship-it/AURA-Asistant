# CI and Migration Initiative Tracker

Created October 2025 to tighten continuous integration coverage and formalize database migration discipline.

## Objectives
1. Provide automated feedback on every push/PR covering backend pytest, frontend lint/type checks, and smoke E2E runs.
2. Enforce Alembic-based schema migrations for any database change.
3. Track ownership, status, and follow-up tasks for CI and migration work.

## Milestones
| Milestone | Status | Owner | Notes |
| --- | --- | --- | --- |
| Baseline CI workflow committed (`.github/workflows/ci.yml`) | Complete | Platform Engineering | Backend pytest, Alembic dry run, and frontend pipeline wired. |
| Backend test suite stabilization | In Progress | Backend Team | Increase coverage, reduce flaky tests caught by CI. |
| Frontend linting/test automation | Complete | Frontend Team | ESLint, TypeScript `--noEmit`, and Playwright smoke suite run on CI. |
| Alembic migration checklist template | Complete | Data/Backend | Workflow documented in `backend/app/alembic/README` and PR template. |
| Automated migration verification step in CI | Complete | Platform Engineering | Alembic dry-run job blocks merges on migration errors. |

## Action Items
- [x] Document PR checklist requiring `alembic revision` for schema changes.
- [x] Expand CI to run Playwright smoke suite and frontend lint/type checks.
- [x] Add coverage reporting from pytest/Playwright to CI artifacts (`pytest-coverage`, `playwright-report`).
- [x] Schedule Alembic onboarding workshop for the wider team (2025-10-07 09:00 GST, Platform & Data co-hosts).
- [ ] Monitor CI runtimes and tune caching to keep wall-clock < 10 minutes.

Update this tracker as milestones progress and link supporting evidence (CI runs, docs) into the notes column.
