# PropertyPro AI Technical Handbook

> Version: 2025-10-02
> Audience: Backend engineers, frontend engineers, ML engineers, product analysts, DevOps, and technical leadership working on the PropertyPro AI stack.
> Scope: Comprehensive body of knowledge synchronized with the FastAPI backend (`backend/app`), the Vite web client (`client/apps/web`), the Expo mobile client (`client/apps/mobile`), shared TypeScript workspaces (`client/packages`), datasets, background processing, infrastructure, and operational tooling located in this repository.

---

## 1. Executive Summary
1. PropertyPro AI is an intelligent assistant purpose-built for Dubai real estate teams, blending deterministic CRM workflows with retrieval-augmented generation (RAG) and task orchestration.
2. The canonical backend lives under `backend/app`, exposing REST and WebSocket APIs via FastAPI routers, scheduling Celery tasks, and coordinating Postgres, Redis, and ChromaDB.
3. The web (`client/apps/web`) and mobile (`client/apps/mobile`) clients reuse shared packages for services, state, UI components, and theme tokens housed inside `client/packages`.
4. Knowledge assets such as CSV datasets, SQL DDL, and document corpora reside in `data/` and `backend/schema/`, providing the grounding data for AI pipelines and reporting features.
5. Deployment, testing, and monitoring stack definitions exist in root-level Docker Compose files, the `monitoring/` directory, and automation scripts under `scripts/`.
6. This handbook acts as the canonical entry point for engineering-critical information; keep it in sync with code changes to avoid drift.

---

## 2. Product Capabilities At A Glance
1. **Agent Productivity**: Property and client CRUD operations, transaction tracking, and activity logging are centered in `backend/app/api/v1/property_management.py`, `clients_router.py`, and `transactions_router.py`.
2. **AI Assistance**: Conversation, summarization, and document generation flows are powered by `ai_assistant_router.py`, `chat_sessions_router.py`, and domain services in `app/domain/ai`.
3. **Marketing Automation**: Campaign builders, social scheduling, and nurture sequences leverage routers like `marketing_automation_router.py`, `social_media_router.py`, and Celery jobs in `app/infrastructure/queue`.
4. **Reporting & Analytics**: CMA reports, performance dashboards, and analytics exports originate from `cma_reports_router.py`, `report_generation_router.py`, and `analytics_router.py`.
5. **Operations & Monitoring**: Health checks, performance metrics, and human feedback loops are surfaced via `health_router.py`, `performance_router.py`, and `feedback_router.py`.
6. **Multichannel Clients**: The Vite web app supplies desktop tooling, while the Expo mobile app preserves critical workflows for on-the-go agents; both rely on shared state and service layers.

---

## 3. Directory Orientation
1. `backend/` — Python backend with FastAPI application code, auth stack, domain services, infrastructure integrations, and supporting scripts.
2. `backend/app/api/v1/` — Router modules implementing REST endpoints grouped by business capability; see Section 6 for per-file breakdown.
3. `backend/app/domain/` — Business logic abstractions for AI, marketing, workflow automation, and session context.
4. `backend/app/core/` — Infrastructure cross-cuts: settings, database connections, middleware, authentication, rate limiting, and logging utilities.
5. `backend/app/infrastructure/` — Integration points for cache, database migrations, external services, and queue definitions.
6. `backend/services/` — Service layer orchestrators mirroring domain logic for backwards compatibility and batch workflows.
7. `client/apps/web/` — Vite + React application with screens, components, store wiring, service facades, and build configuration.
8. `client/apps/mobile/` — Expo/React Native application with mirrored structure adapted for mobile UX.
9. `client/packages/` — Turborepo-style workspaces exposing shared services, store, UI, theme, features, and assets consumed by both apps.
10. `data/` — Canonical CSV, JSON, DOCX, XLSX, and PDF assets forming the seed dataset for CRM, market analytics, and AI context ingestion.
11. `backend/schema/` — Database DDL (`database.sql`) specifying the relational model consumed by routers and services.
12. `monitoring/` — Prometheus, Grafana, logging, and alerting assets enabling observability and runbook automation.
13. `scripts/` — Utility scripts for deployment, testing, database seeding, data pipeline operations, and environment bootstrap.
14. `tests/` — Integration, performance, and utility test harnesses; complements backend/unit tests under `backend/tests` and frontend Playwright specs.
15. `docs/` — Documentation tree; this handbook resides in `docs/handbook`, progress trackers in `docs/progress`, and historical documents under archival folders.

---
## 4. Backend System Context
1. FastAPI app entry: `backend/app/main.py` wires middleware, registers routers dynamically, and initializes monitoring hooks.
2. Dependency injection: `app/core/database.py` yields SQLAlchemy sessions; `app/core/settings.py` loads environment-based configuration and ensures directories (logs/uploads) exist.
3. Middleware stack: `app/core/middleware.py` defines request logging, authentication helpers (`get_current_user`), and role enforcement (`require_roles`).
4. Authentication & security: Auth flows leverage `app/api/v1/auth_router.py`, `app/core/token_manager.py`, `app/core/role_based_access.py`, and `app/core/rate_limiter.py`.
5. AI orchestration: `app/domain/ai` modules provide retrieval, action planning, and content generation flows for AI endpoints.
6. Celery integration: `app/infrastructure/queue/celery_app.py`, `async_processing.py`, `batch_processor.py`, and `task_manager.py` implement asynchronous processing.
7. Database optimization: `app/infrastructure/db/database_enhancement_optimizer.py` and `database_index_optimizer.py` offer tuning scripts used by `database_enhancement_router.py`.
8. Legacy surface: `backend/models_legacy` retains compatibility for prior data models; evaluate before removal.
9. ML assets: `backend/ml` hosts analytics, embeddings, and classification components consumed by AI services.
10. Tests: `backend/tests/test_aura_integration.py` exercises AI integration; additional coverage is expected via `tests/` root harness.

---

## 5. Frontend System Context
1. Web App structure: `client/apps/web/src` comprises `components`, `screens`, `services`, `store`, `theme`, `utils`, and `compat` directories.
2. Routing & App shell: `App.tsx` sets up global layout, route switching, and context providers referencing stores and services.
3. Components: Domain-specific UI modules (e.g., `CommandCenter.tsx`, `ContactManagementView.tsx`, `PackagesView.tsx`) live under `components/`.
4. Analytics components: `components/analytics/` hosts charts and KPI cards syncing with backend analytics endpoints.
5. Services: Web app proxies all API calls through the shared service package by re-exporting `@propertypro/services` in `src/services/api.ts`.
6. State management: React components import Zustand stores from `@propertypro/store` to manage client, property, transaction, UI, and user data.
7. Styling: Theming pipeline uses `@propertypro/theme` tokens while customizations exist in `src/theme` for responsive breakpoints and typography overrides.
8. Tests: `client/apps/web/tests/e2e.spec.ts` and supporting Playwright configs run end-to-end UI automation; additional root-level test harnesses (e.g., `comprehensive-ui-test.js`) complement this coverage.
9. Build pipeline: `vite.config.ts` defines bundler settings, alias resolution for packages, and plugin hooks; `tsconfig.json` handles path mapping to shared packages.
10. Mobile App structure: `client/apps/mobile/src` mirrors the web architecture but adapts components for React Native; key directories are `components`, `screens`, `services`, and `config.ts`.
11. Shared packages: `client/packages/services`, `client/packages/store`, `client/packages/ui`, `client/packages/theme`, `client/packages/features`, and `client/packages/assets` deliver reusable logic consumed by both apps.

---

## 6. API Router Catalogue (backend/app/api/v1)
1. `admin_knowledge_router.py` — Manages curation of admin knowledge bases, ingesting documents and FAQs for AI consumption.
2. `admin_router.py` — Handles administrative operations such as organization setup, licensing, and feature toggles for staff users.
3. `ai_assistant_router.py` — Exposes endpoints powering conversational AI interactions, bridging user prompts to RAG services.
4. `ai_request_router.py` — Manages asynchronous AI task submissions, enabling long-running job orchestration.
5. `analytics_router.py` — Provides analytics dashboards, pulling aggregate metrics from Postgres and caches.
6. `auth_router.py` — Implements login, refresh, and token validation; integrates with rate limiter and RBAC middleware.
7. `chat_sessions_router.py` — Maintains chat transcripts, session metadata, and WebSocket streaming for real-time AI conversations.
8. `clients_router.py` — CRUD operations for client records, budgets, preferences, and relationships.
9. `cma_reports_router.py` — Generates comparative market analysis reports leveraging property and transaction datasets.
10. `database_enhancement_router.py` — Executes schema optimization routines and index tuning scripts.
11. `data_router.py` — Handles ingestion of datasets, CSV uploads, and structured data refresh flows.
12. `documents_router.py` — Uploads, classifies, and retrieves documents stored in file storage and ChromaDB.
13. `feedback_router.py` — Captures user feedback for AI interactions and platform features.
14. `file_processing_router.py` — Processes user-uploaded files (PDF, CSV, DOCX) and triggers AI-based extraction pipelines.
15. `health_router.py` — Simple liveness and readiness endpoints consumed by container orchestrators.
16. `human_expertise_router.py` — Integrates human-in-the-loop review for AI outputs, routing tasks to experts.
17. `marketing_automation_router.py` — Configures and triggers marketing campaigns, email drips, and social posts.
18. `ml_advanced_router.py` — Hosts advanced ML operations, market predictions, and experimentation endpoints.
19. `ml_insights_router.py` — Serves insights from ML models, such as churn predictions or pricing recommendations.
20. `ml_websocket_router.py` — Supports streaming ML inference results and progress updates over WebSockets.
21. `nurturing_router.py` — Manages lead nurturing sequences, cadence adjustments, and task assignments.
22. `performance_router.py` — Exposes runtime performance metrics, queue statistics, and health snapshots.
23. `phase3_advanced_router.py` — Future-phase features toggled for advanced deployments.
24. `property_detection_router.py` — Handles property recognition tasks, potentially using computer vision or NLP to classify listings.
25. `property_management.py` — Central property CRUD, assignments, tagging, and portfolio operations.
26. `report_generation_router.py` — Coordinates report assembly (PDF/HTML) and distribution.
27. `search_optimization_router.py` — Manages search index updates, boosting strategies, and ranking signals.
28. `social_media_router.py` — Integrates with social APIs to schedule and track campaign posts.
29. `task_orchestration_router.py` — Governs AI and workflow task packaging, queueing, and resumption.
30. `team_management_router.py` — Handles team structure, role assignments, and permissions.
31. `transactions_router.py` — Tracks offers, contracts, closings, and commission workflows.
32. `workflows_router.py` — Manages cross-feature workflows including onboarding, compliance checks, and custom pipelines.

---
## 7. Domain Service Catalogue (backend/app/domain)
1. `ai/action_engine.py` — Orchestrates multi-step AI actions, linking prompts to deterministic follow-ups.
2. `ai/advanced_ml_service.py` — Provides advanced analytics and ML predictions beyond baseline models.
3. `ai/ai_enhancements.py` — Enriches AI responses with contextual metadata and formatting tweaks.
4. `ai/ai_manager.py` — Central manager for AI providers, model selection, and feature flags.
5. `ai/ai_processing_service.py` — Handles queued AI processing jobs, ensuring idempotency and retries.
6. `ai/ai_request_processing_service.py` — Bridges HTTP requests to asynchronous AI workflows.
7. `ai/analytics_service.py` — Aggregates metrics from AI usage for reporting and monitoring.
8. `ai/brand_management_service.py` — Generates brand-aligned content and templates for marketing teams.
9. `ai/brokerage_management_service.py` — Supports brokerage oversight, compliance, and team-level insights.
10. `ai/client_nurturing_service.py` — Drives lead nurturing sequences with personalized AI content.
11. `ai/compliance_monitoring_service.py` — Audits AI outputs against compliance and policy constraints.
12. `ai/developer_panel_service.py` — Surfaces developer tools and diagnostics for AI flows.
13. `ai/document_processing_service.py` — Extracts structured data from documents and stores results.
14. `ai/dubai_data_integration_service.py` — Integrates local market datasets and enriches AI context.
15. `ai/entity_detection_service.py` — Identifies real estate entities within text or documents.
16. `ai/file_storage_service.py` — Manages storage abstraction for AI-generated artifacts.
17. `ai/human_expertise_service.py` — Connects AI workflows with human reviewer pipelines.
18. `ai/hybrid_search_engine.py` — Implements hybrid keyword + vector search for knowledge retrieval.
19. `ai/intelligent_data_sorter.py` — Organizes retrieved data into structured outputs.
20. `ai/intelligent_processor.py` — Core processing harness for AI tasks.
21. `ai/knowledge_base_service.py` — Maintains curated knowledge bases for quick retrieval.
22. `ai/notification_service.py` — Sends notifications triggered by AI events.
23. `ai/package_manager.py` — Handles bundling of AI workflow packages consumed by orchestrators.
24. `ai/property_detection_service.py` — Provides property classification and tagging utilities.
25. `ai/query_understanding.py` — Performs intent detection and query parsing.
26. `ai/rag_service.py` — Implements retrieval-augmented generation, embeddings, and prompt assembly.
27. `ai/reporting_service.py` — Generates AI-driven reports and dashboards.
28. `ai/response_enhancer.py` — Post-processes AI responses for tone and structure.
29. `ai/task_orchestrator.py` — Governs multi-step workflow execution for AI tasks.
30. `ai/voice_processing_service.py` — Manages voice input transcription and synthesis.
31. `ai/workflow_automation_service.py` — Automates complex workflows involving multiple AI services.
32. `feedback` modules — Collect and analyze user feedback loops.
33. `listings` modules — Manage listing evaluation, scoring, and enrichment.
34. `marketing` modules — Encapsulate campaign logic, personas, and marketing assets.
35. `sessions` modules — Maintain conversational state, context windows, and session metadata.
36. `workflows` modules — Provide workflow templates, state machines, and automation steps.

---

## 8. Data Assets & Schema Alignment
1. `backend/schema/database.sql` defines core tables: `properties`, `clients`, `transactions`, `transaction_history`, `ai_tasks`, `package_executions`, `package_steps`.
2. Routers rely on raw SQL queries; ensure changes to `database.sql` are mirrored in router SQL statements and data services.
3. `data/properties.csv`, `data/transactions.csv`, and related files seed the database via `scripts/setup_database.py` and ingestion services.
4. AI knowledge base ingestion consumes `data/documents/*`, `data/market_reports.csv`, and `data/market_trends.json` to populate ChromaDB collections.
5. Data simulation scripts in `data_simulation/` generate synthetic datasets for testing advanced analytics.
6. Document corpora (PDF, DOCX) feed into `document_processing_service.py` for extraction and embedding.
7. Ensure data governance policies are respected when refreshing datasets; reference `data_migration_plan.md` if still relevant.

---

## 9. AI & Automation Overview
1. Retrieval pipeline: `rag_service.py` orchestrates ChromaDB queries, intent detection (`QueryIntent` enum), and prompt construction.
2. Action engine: `action_engine.py` transforms AI results into structured actions (schedule follow-up, update records, generate report) executed via services.
3. Background jobs: Celery worker processes tasks defined in `app/infrastructure/queue/task_manager.py` and `nurturing_scheduler.py`.
4. Voice pipeline: `voice_processing_service.py` integrates with frontend voice features (`client/packages/services/src/voiceService.ts`).
5. Analytics: `ai/analytics_service.py` records usage metrics, accessible through `analytics_router.py`.
6. Human review: `human_expertise_service.py` plus `human_expertise_router.py` provide manual QA on AI outputs.
7. Error handling: Monitoring hooks and retry logic defined in `ai_processing_service.py` and queue modules ensure resilience.
8. Provider configuration: `app/core/settings.py` handles API keys (`GOOGLE_API_KEY`, `OPENAI_API_KEY`) and model selection (`AI_MODEL`).

---

## 10. Deployment & Environments
1. Docker Compose files (`docker-compose.yml`, `docker-compose.staging.yml`, `docker-compose.monitoring.yml`, `docker-compose.smoke.yml`, `docker-compose.secure.yml`) define service stacks for different scenarios.
2. Containers include Postgres (`db`), Redis (`redis`), ChromaDB (`chromadb`), FastAPI API (`api`), Celery worker (`worker`), Celery beat scheduler (`scheduler`), monitoring stack, and optional smoke test runners.
3. Environment variables pulled from `.env` and `env.example` control secrets, host addresses, feature toggles, and performance tuning knobs.
4. Makefile targets accelerate workflows (e.g., `make dev-up`, `make lint`, `make test`, `make format`).
5. Scripts like `scripts/deploy.py`, `scripts/start_services.py`, and `scripts/run_tests.py` support automation in CI/CD pipelines.
6. Production deployment should integrate with container orchestration (Kubernetes/ECS) using Compose definitions as blueprints; IaC adoption is pending (see platform doc).

---

## 11. Local Development Workflow
1. Prerequisites: Python 3.10+, Node.js 18+, Docker, Redis, Postgres, ChromaDB container images.
2. Initialize environment: copy `env.example` to `.env`, adjust secrets, ensure `GOOGLE_API_KEY` or other provider keys are set for AI features.
3. Install dependencies: `pip install -r requirements.txt`, `npm install` at repo root (or within `client/`).
4. Launch backend services: `uvicorn backend.app.main:app --reload` for local dev, or `docker-compose.smoke.yml` for container-based stack.
5. Run Celery worker: `celery -A app.infrastructure.queue.celery_app worker --loglevel=info` when testing background tasks.
6. Start web client: `npm run dev --workspace @propertypro/web` (assuming workspace scripts are defined in `client/package.json`).
7. Start mobile client: `npm run start --workspace @propertypro/mobile` to launch Expo bundler.
8. Execute tests: `pytest` for backend, `npm run test` for frontend unit tests (once implemented), `npx playwright test` for web e2e.
9. Monitor logs: backend logs stored in `logs/`, Celery logs in respective containers, frontend logs in terminal.
10. Update documentation: modify handbook files within the same PR to maintain accuracy.

---
## 12. Key User Journeys
1. **User Authentication**: Web/mobile clients call `/auth/login` (FastAPI `auth_router.py`), backend validates password hash, issues JWT and refresh token, stores session metadata.
2. **Property Creation**: User submits property data via `/properties` endpoints, data is validated, inserted into `properties` table, cache invalidation triggered.
3. **AI Chat Session**: Client initiates chat via `/chat/sessions` WebSocket, backend uses `rag_service.py` to fetch context, `ai_manager.py` selects model, `action_engine.py` post-processes response and logs to session history.
4. **Marketing Campaign Launch**: Campaign configured via `marketing_automation_router.py`, stored in Postgres, scheduled tasks enqueued to Celery worker, notifications dispatched through `notification_service.py`.
5. **Document Ingestion**: User uploads PDF, `file_processing_router.py` stores file, `document_processing_service.py` extracts metadata, embeddings pushed to ChromaDB.
6. **CMA Report Generation**: CMA request hits `cma_reports_router.py`, data fetched from property/transaction tables, AI summarization invoked, PDF generated and delivered.
7. **Lead Nurturing**: Sequence updates triggered via `nurturing_router.py`, pipeline uses Celery beat scheduler, `client_nurturing_service.py` customizes messaging, results recorded in CRM.
8. **Monitoring & Alerts**: `/health` endpoint consumed by Compose healthchecks; Prometheus scrapes metrics from `monitoring/application_metrics.py`; alerts configured via `monitoring/alertmanager`.
9. **Feedback Loop**: Users submit feedback; stored via `feedback_router.py`, processed by `human_expertise_service.py` for continuous improvement.

---

## 13. Security Considerations
1. **JWT Secrets**: Ensure `SECRET_KEY` and `JWT_SECRET` are set via environment variables; defaults in settings are development-only.
2. **RBAC Enforcement**: Use `require_roles` dependency in routers to guard privileged endpoints; review `role_based_access.py` for mappings.
3. **Rate Limiting**: `rate_limiter.py` provides per-route throttling; integrate with login and high-cost endpoints.
4. **Session Management**: `session_manager.py` handles session tokens; verify expirations and revocation lists.
5. **Dev Auth Bypass**: `dev_auth_bypass.py` and `simple_dev_auth.py` should be disabled in production; guard with environment checks.
6. **Data Access**: Raw SQL queries must sanitize inputs; prefer parameterized queries through SQLAlchemy `text()` with bindings.
7. **File Uploads**: `settings.py` restricts allowed extensions and size; ensure scanning for malware when integrating external services.
8. **Secrets Storage**: Move to secret management (Vault/SSM) for production; `.env` usage limited to development.
9. **Compliance Logging**: Track access to sensitive client data via logging middleware; evaluate PII redaction.
10. **Dependency Management**: Monitor vulnerabilities via `pip-audit` or `npm audit`; integrate into CI.

---

## 14. Observability
1. **Logging**: Python logging configured in `main.py` and `monitoring/logging_config.py`; ensure consistent log levels and JSON formatting for aggregation.
2. **Metrics**: Custom metrics produced by `monitoring/application_metrics.py` and `monitoring/performance_monitor.py`; integrate with Prometheus exporters.
3. **Tracing**: Not currently implemented; consider OpenTelemetry integration to trace AI workflows end-to-end.
4. **Dashboards**: Grafana dashboards stored under `monitoring/grafana/`; update to reflect new KPIs.
5. **Alerting**: Alertmanager configuration in `monitoring/alertmanager/`; link alerts to on-call rotations.
6. **Health Checks**: Compose healthchecks target `/health`; extend to cover dependencies (DB, Redis, ChromaDB).
7. **Queue Monitoring**: Celery monitoring via Flower (not yet configured) or Prometheus metrics; plan adoption.
8. **Log Retention**: Configure log rotation policies in production; current repo writes to `logs/` without rotation.

---

## 15. Testing Landscape
1. **Backend Unit/Integration**: Minimal coverage exists (e.g., `backend/tests/test_aura_integration.py`); expand to cover routers and services.
2. **Shared Tests**: `tests/` directory hosts integration scaffolding; align with backend fixtures in `tests/conftest.py`.
3. **Frontend E2E**: `client/apps/web/tests/e2e.spec.ts` uses Playwright; extend scenarios to cover login, AI chat, property CRUD, marketing flows.
4. **Frontend Unit/Component**: No tests currently; adopt React Testing Library and MSW mocks.
5. **Mobile Tests**: Expo app lacks automated testing; integrate Detox or Expo E2E harness.
6. **Performance Tests**: `tests/performance` placeholders exist; implement Locust/K6 for load testing.
7. **CI Integration**: Establish GitHub Actions pipelines for linting, tests, style checks, and security scans.

---

## 16. Release Management
1. Use `docs/progress/release-readiness.md` to track gate status for each milestone.
2. Maintain `docs/progress/dev-journal.md` to log daily progress, blockers, and decisions.
3. Align release branches with readiness tracker updates; link evidence (test reports, dashboards) in tracker table.
4. Conduct pre-release smoke tests using `docker-compose.smoke.yml` and `scripts/run_tests.py --smoke`.
5. Archive release notes and feature toggles in `CHANGELOG.md` or dedicated docs within `docs/business`.
6. Post-release, update monitoring dashboards and analytics baselines captured in `monitoring/`.

---

## 17. Contribution Guidelines (Interim)
1. Update relevant documentation alongside code changes, especially handbook sections that reference touched modules.
2. Include migration scripts when modifying database schema or SQL queries.
3. Add or update automated tests corresponding to new or affected features.
4. Run linting/formatting scripts (`make lint`, `npm run lint`) before pushing.
5. Seek security review for endpoints handling sensitive data (client PII, transaction info).
6. Keep environment variables documented in `env.example`; describe any new ones.
7. For AI features, document prompts, model choices, and guardrails in `docs/`.

---

## 18. Glossary of Key Terms
1. **RAG (Retrieval-Augmented Generation)**: Architecture combining vector retrieval (`ChromaDB`) with generative models in `rag_service.py`.
2. **AI Package**: A bundle of tasks executed by `task_orchestrator.py`, tracked in `package_executions` and `package_steps` tables.
3. **Nurturing Sequence**: Automated follow-up plan orchestrated by `nurturing_scheduler.py` and marketing services.
4. **CMA (Comparative Market Analysis)**: Report comparing similar properties; implemented in `cma_reports_router.py`.
5. **ChromaDB**: Vector database storing embeddings for knowledge retrieval.
6. **Celery**: Distributed task queue used for asynchronous processing.
7. **Zustand**: State management library used in shared `@propertypro/store` package.
8. **Expo**: Framework for React Native mobile apps; used in `client/apps/mobile`.
9. **Playwright**: E2E testing framework for web client.
10. **Prometheus/Grafana**: Monitoring stack capturing metrics and visualizations.

---
## 19. Future Roadmap (Technical)
1. **CI/CD Modernization**: Implement multi-stage pipelines (lint, test, security scan, container build) with caching for Python/Node.
2. **Infrastructure as Code**: Translate Docker Compose definitions into Terraform or CloudFormation modules.
3. **Observability Enhancements**: Add distributed tracing, log aggregation, and APM instrumentation.
4. **Data Governance**: Implement automated data quality checks and catalog updates for `data/` sources.
5. **AI Guardrails**: Expand compliance monitoring and human-in-the-loop instrumentation.
6. **Feature Flags**: Introduce centralized flagging system for rolling out features incrementally.
7. **Package Publishing**: Formalize release process for shared packages (`@propertypro/*`) to ensure versioned consistency.

---

## 20. Contact Points & Ownership
1. **Backend Core**: Ownership resides with Platform API squad; refer to `docs/business` for team roster.
2. **AI & ML**: AI Innovation squad manages `app/domain/ai` and ML pipelines.
3. **Frontend Web**: Agent Experience squad maintains `client/apps/web` and related packages.
4. **Mobile**: Mobile Enablement squad supports `client/apps/mobile`.
5. **Data**: Data Engineering squad maintains datasets, ingestion scripts, and schema evolution.
6. **DevOps/Infra**: Reliability squad handles Docker Compose, monitoring, deployment scripts.
7. **Documentation**: Handled collectively; designate a doc DRI per sprint to ensure freshness.

---

## 21. Appendix A — File Reference Quick List
1. `backend/app/main.py`
2. `backend/app/core/settings.py`
3. `backend/app/core/database.py`
4. `backend/app/core/middleware.py`
5. `backend/app/core/role_based_access.py`
6. `backend/app/core/token_manager.py`
7. `backend/app/api/v1/auth_router.py`
8. `backend/app/api/v1/property_management.py`
9. `backend/app/api/v1/transactions_router.py`
10. `backend/app/api/v1/clients_router.py`
11. `backend/app/api/v1/ai_assistant_router.py`
12. `backend/app/api/v1/chat_sessions_router.py`
13. `backend/app/api/v1/marketing_automation_router.py`
14. `backend/app/api/v1/social_media_router.py`
15. `backend/app/api/v1/task_orchestration_router.py`
16. `backend/app/api/v1/report_generation_router.py`
17. `backend/app/api/v1/analytics_router.py`
18. `backend/app/domain/ai/rag_service.py`
19. `backend/app/domain/ai/action_engine.py`
20. `backend/app/domain/ai/ai_manager.py`
21. `backend/app/domain/marketing/*`
22. `backend/app/domain/workflows/*`
23. `backend/app/infrastructure/queue/celery_app.py`
24. `backend/app/infrastructure/queue/task_manager.py`
25. `backend/app/infrastructure/db/database_enhancement_optimizer.py`
26. `backend/services/document_processing_service.py`
27. `backend/schema/database.sql`
28. `client/apps/web/App.tsx`
29. `client/apps/web/src/components/CommandCenter.tsx`
30. `client/apps/web/src/components/ContactManagementView.tsx`
31. `client/apps/web/src/services/api.ts`
32. `client/apps/web/src/store/*`
33. `client/apps/web/src/theme/*`
34. `client/apps/mobile/App.tsx`
35. `client/apps/mobile/src/screens/*`
36. `client/packages/services/src/api.ts`
37. `client/packages/store/src/userStore.ts`
38. `client/packages/ui/*`
39. `client/packages/theme/*`
40. `client/packages/features/*`
41. `data/properties.csv`
42. `data/transactions.csv`
43. `data/market_data.csv`
44. `data/documents/*`
45. `data_simulation/generate_additional_data.py`
46. `docker-compose.yml`
47. `docker-compose.monitoring.yml`
48. `monitoring/application_metrics.py`
49. `monitoring/performance_monitor.py`
50. `scripts/run_tests.py`

---

## 22. Appendix B — Environment Variables
1. `DATABASE_URL` — Postgres connection string; defaults to local dev instance.
2. `CHROMA_HOST` / `CHROMA_PORT` — ChromaDB service coordinates.
3. `REDIS_URL` — Redis connection string used by caches and Celery.
4. `GOOGLE_API_KEY` — Gemini API key for AI features (required for production AI flows).
5. `OPENAI_API_KEY` — Optional alternative AI provider key (used in Docker Compose).
6. `AI_MODEL` — Identifier for default AI model; default `gemini-1.5-flash`.
7. `SECRET_KEY` / `JWT_SECRET` — Secrets for JWT signing; must be unique per environment.
8. `ACCESS_TOKEN_EXPIRE_MINUTES` — JWT expiration in minutes.
9. `JWT_REFRESH_TOKEN_EXPIRE_DAYS` — Refresh token lifespan.
10. `BCRYPT_ROUNDS` — Password hashing cost factor.
11. `LOG_LEVEL` — Logging verbosity for backend services.
12. `ENABLE_BLUEPRINT_2` — Feature toggle for blueprint features.
13. `NURTURING_SCHEDULER_ENABLED` — Toggle for nurture job execution.
14. `DOCUMENT_GENERATION_ENABLED` — Toggle for report generation features.
15. `MAX_FILE_SIZE` — Upload size limit in bytes.

---

## 23. Appendix C — Toolchain Reference
1. Python 3.10, FastAPI, SQLAlchemy, Pydantic, Celery, Redis.
2. TypeScript 5+, React 18, Vite, Zustand, Playwright, Expo.
3. ChromaDB for vector search, Postgres 15 for relational data.
4. Prometheus/Grafana for monitoring, Alertmanager for alerts.
5. Docker/Docker Compose for environment orchestration.
6. Makefile, PowerShell scripts, and Python automation in `scripts/`.

---

## 24. Appendix D — Data Flow Diagrams (Textual)
1. **Authentication Flow**: Client -> `/auth/login` -> `auth_router` -> `database.py` (users table) -> token issuance -> response -> store token in frontend Zustand store -> subsequent requests attach `Authorization` header.
2. **AI Chat Flow**: Client WebSocket -> `chat_sessions_router` -> `session_manager.py` -> `rag_service.py` (retrieval) -> `ai_manager.py` (model call) -> `action_engine.py` (post-processing) -> response streamed -> logs stored -> analytics event emitted -> optional follow-up tasks enqueued to Celery.
3. **Document Processing Flow**: Client upload -> `file_processing_router` -> `file_storage_service.py` -> `document_processing_service.py` (OCR, parsing) -> embeddings created -> stored in ChromaDB -> metadata persisted in Postgres -> available for AI retrieval.
4. **Marketing Automation Flow**: Client config -> `marketing_automation_router` -> `marketing` domain services -> records stored -> tasks scheduled via `nurturing_scheduler.py` -> Celery worker executes -> results logged -> notifications dispatched via `notification_service.py`.
5. **Reporting Flow**: Client request -> `report_generation_router` -> `reporting_service.py` -> data aggregated from Postgres -> AI summarization -> PDF generated -> stored in `uploads/` -> signed URL returned.
6. **Monitoring Flow**: Services emit metrics -> `application_metrics.py` -> Prometheus scrape -> Grafana dashboards -> Alertmanager triggers -> on-call runbook executed.

---

## 25. Appendix E — Coding Standards Snapshot
1. Python code style adheres to Black/PEP8 conventions; configure `pyproject.toml` (pending) or run `black` manually.
2. TypeScript formatting relies on Prettier; ensure consistent import ordering via ESLint configs.
3. Naming conventions: snake_case for Python modules, PascalCase for React components, camelCase for TypeScript variables.
4. Directory naming encourages `lowercase_with_underscores` in backend, `lowercase-with-dashes` or camelCase in frontend.
5. Keep functions focused, with docstrings describing parameters and return values for complex logic.
6. Document new environment variables in `env.example` and this handbook.

---

## 26. Appendix F — Incident Response Outline
1. Detect issue via Alertmanager notification referencing `monitoring` rules.
2. Check `/health` endpoints and relevant service logs (`logs/app.log`, Celery worker logs).
3. Validate database connectivity using `scripts/test_connections.py`.
4. Inspect queue backlog via Celery monitoring tools (add Flower or CLI checks).
5. If AI provider issues suspected, verify `GOOGLE_API_KEY` status and fallback providers.
6. Update status page (if applicable), coordinate with product/support teams.
7. Create incident summary and add entry to `docs/progress/dev-journal.md`.
8. File follow-up tasks for root cause analysis and remediation.

---

## 27. Revision Log
1. 2025-10-02 — Initial comprehensive handbook compiled for alignment with current codebase (Codex update).

---

## 28. Maintenance Checklist
1. After each sprint, review router list for additions/removals and update Section 6 accordingly.
2. When new domain services are created, append them to Section 7 with concise descriptions.
3. Keep environment variable appendix synchronized with `env.example` revisions.
4. Update testing landscape as new suites are implemented.
5. Document new monitoring dashboards and runbooks in relevant sections.
6. Review contact points quarterly to account for team changes.

---

## 29. Related Documents
1. `docs/handbook/backend.md` — Deep dive into backend architecture.
2. `docs/handbook/frontend.md` — Detailed frontend and workspace guide.
3. `docs/handbook/platform.md` — Platform, data, operations, and improvement plan.
4. `docs/progress/release-readiness.md` — Release gating tracker.
5. `docs/progress/dev-journal.md` — Session-based progress log.
6. `docs/business/` — Product and go-to-market documentation.

---

Stay disciplined about updating this handbook. Its accuracy directly affects onboarding speed, architectural consistency, and cross-team coordination.
## 30. Router Endpoint Reference Highlights
1. `auth_router.py` endpoints:
   - `/auth/login` authenticates users via email/password, hashing comparison through `verify_password`.
   - `/auth/refresh` exchanges refresh tokens for new access tokens using `generate_refresh_token`.
2. `team_management_router.py` endpoints:
   - `/teams` CRUD for team records, applying role checks to restrict admin access.
   - `/teams/{team_id}/members` manages membership assignments and role updates.
3. `clients_router.py` endpoints:
   - `/clients` supports listing with filters (status, agent) and creation of new clients with budgets.
   - `/clients/{client_id}` fetches details, updates preferences, and records notes.
4. `property_management.py` endpoints:
   - `/properties` handles creation, search filters (location, price range), and soft deletes.
   - `/properties/{property_id}` updates metadata, attaches media references, and toggles availability.
5. `transactions_router.py` endpoints:
   - `/transactions` records offers, bids, and sales status transitions tracked in `transaction_history`.
   - `/transactions/{transaction_id}/status` enforces valid workflow transitions and logs audit entries.
6. `chat_sessions_router.py` endpoints:
   - `/chat/sessions` initializes sessions, persists context, and returns session identifiers.
   - WebSocket `/chat/stream/{session_id}` streams AI responses, handles typing indicators, and logs events.
7. `ai_assistant_router.py` endpoints:
   - `/ai/assist` processes synchronous prompts using `EnhancedRAGService` for rapid responses.
   - `/ai/assist/task` queues asynchronous actions via `ActionEngine` and Celery tasks.
8. `documents_router.py` endpoints:
   - `/documents/upload` accepts multipart uploads, stores metadata, and schedules OCR.
   - `/documents/{doc_id}` retrieves processed document data and downloadable links.
9. `report_generation_router.py` endpoints:
   - `/reports/cma` orchestrates CMA generation, combining SQL data with AI summarization.
   - `/reports/performance` compiles performance analytics with optional PDF rendering.
10. `marketing_automation_router.py` endpoints:
    - `/marketing/campaigns` configures campaigns, segmentation, and channel mix parameters.
    - `/marketing/campaigns/{id}/launch` triggers Celery tasks that send content to outbound services.
11. `social_media_router.py` endpoints:
    - `/social/posts` drafts, schedules, and previews platform-specific content.
    - `/social/posts/{id}/status` polls publishing results and error diagnostics.
12. `nurturing_router.py` endpoints:
    - `/nurturing/sequences` creates multi-step journey plans referencing templates in workflows.
    - `/nurturing/sequences/{id}/pause` allows operators to pause/resume automation safely.
13. `analytics_router.py` endpoints:
    - `/analytics/summary` aggregates KPIs (lead volume, conversion rate) with caching.
    - `/analytics/engagement` provides channel-specific metrics for marketing performance.
14. `performance_router.py` endpoints:
    - `/performance/runtime` surfaces API latency stats, queue backlog, and worker health.
    - `/performance/celery` summarizes Celery queue metrics and retry counts.
15. `feedback_router.py` endpoints:
    - `/feedback` captures rating, comments, and context for AI replies.
    - `/feedback/export` produces CSV reports consumed by quality analysts.
16. `search_optimization_router.py` endpoints:
    - `/search/reindex` triggers background reindexing routines to refresh search indices.
    - `/search/boosting` updates boosting rules for property attributes or agent priority.
17. `data_router.py` endpoints:
    - `/data/import` allows uploading bulk CSVs that feed into ingestion scripts.
    - `/data/status` lists ingestion run history and failure diagnostics.
18. `database_enhancement_router.py` endpoints:
    - `/database/optimize` invokes index optimizer and vacuum routines.
    - `/database/plan` previews proposed database enhancements before execution.
19. `file_processing_router.py` endpoints:
    - `/files/text-extract` extracts text from uploaded documents using AI processors.
    - `/files/tabular-preview` provides preview of CSV rows for validation before ingestion.
20. `human_expertise_router.py` endpoints:
    - `/expertise/reviews` assigns AI outputs to reviewers and tracks review lifecycle.
    - `/expertise/decisions` captures override decisions to retrain AI behavior.
21. `ml_advanced_router.py` endpoints:
    - `/ml/price-forecast` delivers price predictions for listings using advanced models.
    - `/ml/risk-score` evaluates transaction risk for compliance teams.
22. `ml_insights_router.py` endpoints:
    - `/ml/market-trends` returns trend analyses with comparisons to historical data.
    - `/ml/lead-scoring` provides AI-derived lead readiness scores for agent prioritization.
23. `ml_websocket_router.py` endpoints:
    - WebSocket `/ml/stream` streams incremental results for long-running ML computations.
    - `/ml/jobs/{id}` polls job status, error messages, and output artifacts.
24. `phase3_advanced_router.py` endpoints:
    - `/phase3/pilots` toggles pilot features for select tenants.
    - `/phase3/insights` shares experimental analytics not yet GA.
25. `task_orchestration_router.py` endpoints:
    - `/tasks/packages` lists AI packages with metadata and execution history.
    - `/tasks/packages/{id}/resume` restarts failed packages from last successful step.
26. `workflows_router.py` endpoints:
    - `/workflows/templates` enumerates automation templates with versioning.
    - `/workflows/{id}/state` reveals detailed workflow state machine transitions.

---

## 31. Frontend Workspace Mapping
1. `client/apps/web/src/components/CommandCenter.tsx` orchestrates dashboard modules, pulling data from stores and services.
2. `client/apps/web/src/components/ContactManagementView.tsx` displays CRM records, integrates with `clientStore` actions, and renders analytics summaries.
3. `client/apps/web/src/components/PackagesView.tsx` manages AI package creation, leveraging `workflowEngine.ts` for backend interactions.
4. `client/apps/web/src/components/SocialMediaView.tsx` coordinates scheduling UI, content previews, and channel selection.
5. `client/apps/web/src/components/TasksView.tsx` renders task lists, enabling inline status updates tied to backend workflows.
6. `client/apps/web/src/components/Analytics/KpiCard.tsx` (representative) shows KPI values, using `apiGet` wrappers to fetch analytics data.
7. `client/apps/web/src/screens/Dashboard` modules aggregate components into route-level experiences.
8. `client/apps/web/src/services/api.ts` re-exports shared API utilities, ensuring a single HTTP abstraction across applications.
9. `client/apps/web/src/store/index.ts` composes Zustand slices for global state, hooking into shared store packages.
10. `client/apps/web/src/theme/index.ts` merges theme tokens with responsive breakpoints and typography scales.
11. `client/apps/mobile/src/components/Dashboard` replicates key dashboard widgets with React Native primitives from `@propertypro/ui`.
12. `client/apps/mobile/src/screens/ChatScreen.tsx` integrates the AI assistant experience with mobile navigation stacks.
13. `client/apps/mobile/src/services/voiceService.ts` bridges microphone input with backend voice processing endpoints.
14. `client/packages/services/src/api.ts` provides HTTP wrappers that automatically include auth headers and handle JSON/FormData payloads.
15. `client/packages/services/src/aiCoordinator.ts` coordinates chat message lifecycle, streaming updates to UI components.
16. `client/packages/services/src/marketingService.ts` exposes marketing-specific endpoints to both web and mobile clients.
17. `client/packages/store/src/userStore.ts` manages authentication state, tokens, and user metadata.
18. `client/packages/store/src/propertyStore.ts` stores property collections, filters, and selection state shared across apps.
19. `client/packages/store/src/transactionStore.ts` tracks transaction lists and derived metrics for dashboards.
20. `client/packages/store/src/uiStore.ts` keeps UI preference flags (theme, layout, panel states) synchronized across sessions.
21. `client/packages/ui` defines shared components (buttons, cards, modals) for consistent look and feel across platforms.
22. `client/packages/theme` holds design tokens (colors, spacing, typography); consumed by both web and mobile builds.
23. `client/packages/features` encapsulates reusable business logic modules (e.g., property comparisons, marketing checklists).
24. `client/packages/assets` stores SVGs, icons, and media assets referenced by UI components.

---
