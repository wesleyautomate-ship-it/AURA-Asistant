# Release Readiness Tracker

Use this tracker to record the status of each engineering gate as the platform moves from local validation to production launch. Update the **Status**, **Owner**, and **Evidence** columns during each milestone review.

| Phase | Gate | Status | Owner | Evidence / Link |
| --- | --- | --- | --- | --- |
| Foundation | Backend scaffolding aligned with `backend/app` structure | Complete | Platform Engineering | `docs/handbook/backend.md` |
| Foundation | Frontend workspace bootstrapped (`client/apps/web`, `client/packages`) | Complete | Frontend Team | `docs/handbook/frontend.md` |
| Foundation | Core datasets loaded (`data/`, `backend/schema/database.sql`) | Complete | Data Engineering | `backend/schema/database.sql`, `scripts/setup_database.py` |
| MVP | Authentication and RBAC flows verified (`app/api/v1/auth_router.py`) | In Progress | Backend Team | Pending CI hardening |
| MVP | Property & client CRUD validated end-to-end | In Progress | QA | Playwright scenario backlog |
| MVP | AI assistant happy-path with ChromaDB (`app/domain/ai/rag_service.py`) | In Progress | AI Team | Smoke test coverage pending |
| Beta | Marketing automation and nurturing jobs exercised (Celery worker/scheduler) | Pending | Growth Engineering |  |
| Beta | Web and mobile clients integrated with shared services (`client/packages/services`) | In Progress | Frontend Team | Shared store alignment complete; add regression tests |
| Beta | Monitoring stack deployed (`monitoring/`, `docker-compose.monitoring.yml`) | Pending | Reliability |  |
| Launch | Security review (JWT secrets, `dev_auth_bypass.py` disabled) | Pending | Security |  |
| Launch | Performance baseline recorded (`monitoring/performance_monitor.py`) | Pending | Reliability |  |
| Launch | Regression suite passed (backend + frontend) | Pending | QA |  |
| Growth | Data refresh pipeline rehearsed (`scripts/data_pipeline`) | Pending | Data Engineering |  |
| Growth | Analytics + reporting adoption goals met | Pending | Product Analytics |  |
| Growth | Post-launch support runbook updated | Pending | Support Ops |  |

## Updating the Tracker
1. During each milestone review, update the **Status** column (`Pending`, `In Progress`, `Complete`).
2. Link to validation assets (test runs, dashboards, PRs, meeting notes) in the **Evidence** column.
3. Commit updates alongside the code changes that satisfied the gate to maintain traceability.
