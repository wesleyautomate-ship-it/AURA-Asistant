# Test Strategy

## Coverage Matrix

| Layer | Scope | Existing | Gaps | Actions |
| --- | --- | --- | --- | --- |
| Unit | Pure functions, serializers, hooks | Limited (`backend/tests/test_contacts_api.py`) | No coverage for brochure render service, CMA planners | Add fast unit tests for `_deep_merge`, `render_brochure_to_pdf` (mock WeasyPrint), cma calculators |
| Integration | API + DB via TestClient | Contacts & follow-ups smoke | No brochure/CMA/task orchestrator tests; no auth coverage | Create fixtures with SQLite + seed scripts; test `/api/v1/brochures` lifecycle and `/api/v1/export/html-save` auth |
| Contract | Ensure frontend types match backend schemas | `src/tests/contract/openapi-types.spec.ts` placeholder | Not generated from live schema | Export `/openapi.json` in CI and validate TypeScript types with `openapi-typescript` |
| E2E | Full workflow through UI | Playwright config referenced but not runnable | No real tests in repo; commands point to `client/` | Stand up minimal flows: create brochure, verify render, schedule follow-up |
| Performance | k6 smoke/perf budgets | None | No baseline | Use generated scripts in `perf/k6`; run nightly against staging |
| Security | Dependency scan, auth tests | None | No automated coverage | Add `pip-audit`, `npm audit`, and ZAP baseline for `/uploads` exposure |

## Data Management

- Use deterministic seed scripts (`backend/scripts/seed_contacts.py`, `seed_brochure_templates.py`) to initialise test DBs.
- Prefer factory functions over static fixtures to avoid stale snapshots.
- For frontend E2E, seed via API calls rather than DB seeding to keep coverage realistic.

## Tooling & Automation

- Enable `pytest` markers (`@pytest.mark.integration`, `@pytest.mark.performance`) to scope runs.
- Adopt `msw` or interceptors for frontend unit tests to simulate API failures.
- Generate test reports (JUnit, HTML) and upload as CI artifacts.

## Non-Functional Checks

- Accessibility: run `axe-core` or Playwright accessibility scans on key flows (Contacts list/detail, Brochure editor).
- Internationalisation: ensure date/number formatting tolerance in tests.
- Regression watch: integrate Lighthouse CI for LCP/CLS budgets; fail build on regression >10%.
