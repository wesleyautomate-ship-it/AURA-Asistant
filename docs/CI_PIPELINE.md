# CI Pipeline Proposal

## Stage Overview

1. **Setup**
   - Checkout repo.
   - Determine changed directories to scope jobs.
2. **Backend Lint & Type**
   - `ruff` (or `flake8`), `black --check`, `mypy`.
3. **Backend Tests**
   - `pytest` with `PYTHONPATH=backend`, coverage report, SQLite in-memory DB.
4. **Database Checks**
   - `alembic upgrade head --sql` (dry run) once Alembic ready.
5. **Frontend Quality**
   - `npm run lint`, `npm run typecheck`, `npm run build`.
6. **Frontend Tests**
   - Component/unit tests (Vitest/Jest).
   - Optional Playwright smoke (tagged).
7. **Security Scans**
   - `pip-audit`, `bandit` (low severity allowed), `npm audit --omit=dev`.
8. **Artifacts**
   - Upload coverage, build bundles, lighthouse report.
9. **Perf Smoke (Optional)**
   - Run `k6` smoke vs staging URL on nightly schedule.

## Reference Workflow Snippet

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:

jobs:
  backend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pip install ruff black mypy pytest pytest-cov pip-audit
      - run: ruff check backend/app
      - run: black --check backend/app
      - run: mypy backend/app
      - run: |
          PYTHONPATH=backend \
          pytest backend/tests --cov=backend.app --cov-report=xml
      - run: pip-audit -r backend/requirements.txt
      - uses: actions/upload-artifact@v4
        with: { name: backend-coverage, path: coverage.xml }

  frontend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm', cache-dependency-path: aura-client/package-lock.json }
      - working-directory: aura-client
        run: npm ci
      - working-directory: aura-client
        run: npm run lint
      - working-directory: aura-client
        run: npm run typecheck
      - working-directory: aura-client
        run: npm run build
      - working-directory: aura-client
        run: npm audit --omit=dev
      - uses: actions/upload-artifact@v4
        with: { name: aura-client-dist, path: aura-client/dist }
```

## Best Practices

- Cache `~/.cache/pip` and node modules per lockfile hash.
- Fail fast on lint/format errors before running heavier stages.
- Gate Playwright only on labelled builds to reduce time.
- Publish test reports to GitHub summary.
- Run nightly job with `scripts/lighthouse.mjs` + `k6` to capture regressions.

## Pipeline Outputs

- Coverage trend (backend + frontend).
- Dependency scan results.
- Static asset bundle artefact for preview deployments.
- Performance budgets (Lighthouse JSON) stored alongside build.
