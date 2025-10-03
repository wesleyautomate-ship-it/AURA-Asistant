# Platform, Data, and Operations Handbook

> Scope: Cross-cutting concerns spanning data assets, AI infrastructure, DevOps, monitoring, quality, and process maturity for PropertyPro AI.
> Audiences: Data engineering, machine learning, DevOps/SRE, platform architects, security, and engineering leadership.

---

## 1. Platform Overview
1. PropertyPro AI operates as a full-stack platform integrating deterministic CRM workflows with AI-driven automation for Dubai real estate.
2. Core services: FastAPI backend, Vite web client, Expo mobile client, Celery workers, ChromaDB vector store, Postgres relational database, Redis cache/broker.
3. Data pipelines ingest structured CSV/JSON datasets and unstructured documents to feed AI retrieval, analytics dashboards, and reporting features.
4. Operations rely on Docker Compose orchestrations for local and staging environments, with future migration to cloud orchestration (Kubernetes/ECS).
5. Monitoring stack includes Prometheus, Grafana, Alertmanager, with logs routed to local filesystem pending integration with centralized logging.
6. Quality, security, and compliance processes require maturation; this handbook outlines current state and recommended improvements.

---

## 2. Data Landscape
1. Structured datasets stored in `/data` including `properties.csv`, `transactions.csv`, `clients.csv`, `market_data.csv`, `market_reports.csv`, `neighborhoods.json`, etc.
2. Datasets provide ground truth for Postgres tables defined in `backend/schema/database.sql`.
3. `data_simulation/` contains scripts (`generate_additional_data.py`, `generate_company_data.py`) producing synthetic data for testing scenarios.
4. Document corpus under `data/documents` includes PDFs/DOCX used for knowledge ingestion and AI context.
5. Data quality management currently manual; implement validation scripts to check schema, duplicates, anomalies before ingestion.
6. Maintain data catalog documenting source, refresh cadence, owner, and usage for each dataset.
7. Identify sensitive data (client contact info, transactions) and enforce access controls and encryption where necessary.
8. Establish retention policies aligning with business and regulatory requirements (e.g., GDPR-equivalent in Dubai).
9. Plan incremental updates to datasets (delta loads) to avoid full reloads when refreshing market data.
10. Document data lineage showing how raw datasets transform into application tables and analytics outputs.

---
## 3. Database Schema & Management
1. Base schema defined in `backend/schema/database.sql`; use this as canonical reference for tables, columns, constraints.
2. Introduce Alembic migrations to manage schema evolution; document migration workflow (generate -> review -> apply).
3. Maintain versioned migration history to enable rollbacks and reproducible environments.
4. For each schema change, update handbook, dataset loaders, and API logic simultaneously to avoid drift.
5. Implement database seeding scripts referencing `data/` datasets for local/testing environments.
6. Use environment-specific databases (dev, staging, prod) with separate credentials and access policies.
7. Apply performance tuning (indexes, vacuum) using scripts in `backend/app/infrastructure/db` and monitor results.
8. Consider partitioning large tables (transactions) based on date to maintain query performance.
9. Implement backup and restore strategy (regular snapshots, tested recovery procedures).
10. Monitor database connections, slow queries, and storage growth via monitoring stack.

---

## 4. Vector Store & AI Data
1. ChromaDB hosts embeddings for document/text retrieval; configured via `CHROMA_HOST` / `CHROMA_PORT`.
2. Embeddings generated when documents ingested or updated; ensure consistent embedding model versioning.
3. Maintain metadata store linking embeddings to original documents, categories, and access permissions.
4. Plan for vector store backups (snapshotting data directory) and replication strategies for high availability.
5. Monitor vector store performance (latency, throughput) and adjust top-k retrieval parameters for optimal response time.
6. Consider sharding by tenant or domain if dataset grows large to maintain retrieval speed.
7. Document embedding pipeline steps: text extraction -> chunking -> embedding -> storage -> index refresh.
8. Establish process for re-embedding after prompt/template changes to ensure alignment.
9. Manage sensitive content scrubbing before embedding (remove PII where not needed).
10. Evaluate security controls for vector store (network restrictions, authentication) to prevent unauthorized access.

---

## 5. AI Infrastructure & Governance
1. Primary AI provider: Google Gemini, configured via `GOOGLE_API_KEY` and `AI_MODEL` in settings.
2. Optional fallback provider: OpenAI, with environment variables defined in Docker Compose.
3. Maintain provider configuration (model version, timeouts, retries) in central settings to ensure consistent behavior.
4. Track usage metrics (tokens, latency, error rates) and cost to manage budget.
5. Implement guardrails: prompt templates enforce tone, disclaimers, allowed actions; compliance services review outputs.
6. Store prompt/response logs securely for auditing and tuning; ensure access restricted to authorized personnel.
7. Human-in-the-loop workflows assign sensitive outputs to reviewers via `human_expertise_service`.
8. Establish model release management: test new models in staging, capture metrics, update documentation before production rollout.
9. Document failure modes (provider unavailable, quota exceeded) and fallback strategies (cached responses, degraded modes).
10. Keep taxonomy of AI intents (`QueryIntent`) synchronized with product features, updating retrieval weighting accordingly.

---

## 6. Background Processing & Scheduling
1. Celery worker processes asynchronous tasks; define concurrency per environment (2 workers default) with scaling plan.
2. Redis serves as broker/backend; secure with password (`REDIS_PASSWORD`) and network restrictions.
3. Celery Beat scheduler triggers recurring jobs (nurturing sequences, data refresh, maintenance tasks).
4. Document each scheduled job (name, frequency, purpose, owner) in operational runbook.
5. Monitor task queue depth, success/failure counts, and average execution time; adjust concurrency as needed.
6. Ensure idempotency for tasks to handle retries without duplicate side effects.
7. Provide manual re-run capability for failed tasks via API or admin UI.
8. Implement distributed locking for tasks that must not overlap (e.g., maintenance scripts).
9. Use Celery task naming conventions and structured logging for observability.
10. Plan for Celery migration to alternative (RQ, Dramatiq) if future requirements demand.

---

## 7. Deployment Architecture
1. Local/staging environments orchestrated via Docker Compose (`docker-compose.yml` variants) defined in repo.
2. Services include `db`, `redis`, `chromadb`, `api`, `worker`, `scheduler`, optional `monitoring` stack, and `web` client (if containerized separately).
3. Compose variants tailored for staging, smoke testing, monitoring, and security hardening.
4. Environment variables provided via `.env`; ensure production uses secrets manager instead.
5. Plan migration to Kubernetes/ECS with infrastructure-as-code (Terraform) defining services, secrets, scaling policies.
6. Define network topology (VPC, subnets, security groups) restricting access between components.
7. Implement API gateway or load balancer fronting FastAPI service with TLS termination and WAF policies.
8. Use container registry (ECR/GCR) for storing production images; implement build pipeline with vulnerability scanning.
9. Document scaling strategy (horizontal for API, worker; vertical for DB) and auto-scaling triggers.
10. Maintain disaster recovery plan including backup restoration and failover environments.

---
## 8. Monitoring & Observability Stack
1. Prometheus configuration located in `monitoring/prometheus/prometheus.yml`; define scrape targets for API, worker, scheduler, and application metrics endpoints.
2. Grafana dashboards stored under `monitoring/grafana/`; maintain dashboards for API latency, task queues, AI usage, database health, and frontend performance (if instrumented).
3. Alertmanager configuration lives in `monitoring/alertmanager/`; define alert rules for error rate spikes, unavailable services, long task queues, and resource exhaustion.
4. Logging configuration in `monitoring/logging_config.py`; migrate to centralized logging (ELK, Loki) for production visibility.
5. Add tracing instrumentation (OpenTelemetry) for API, Celery, and frontend to observe end-to-end latency.
6. Implement healthcheck endpoints returning dependency statuses for orchestrators and uptime monitors.
7. Configure synthetic monitoring (uptime robot, Pingdom) to verify key endpoints externally.
8. Document on-call rotation and escalation policy tied to Alertmanager notifications.
9. Capture SLA/SLO metrics (availability, latency) and review monthly with stakeholders.
10. Build runbooks for common alerts (database down, AI provider outage, queue backlog) referencing this handbook.

---

## 9. Logging Strategy & Retention
1. Backend logs output to `logs/app.log`; configure log rotation (size/time-based) to prevent disk saturation.
2. Celery logs stored separately; collect and forward to central logging solution.
3. Frontend console logs not persisted; integrate client-side logging service for error capture.
4. Tag logs with request IDs, user IDs, tenant IDs to aid troubleshooting.
5. Redact sensitive data (passwords, access tokens, personal data) before logging.
6. Define retention policy (e.g., 90 days) aligning with compliance; automate archival/deletion.
7. Provide search/indexing capabilities (ELK, Loki) for investigators to query logs quickly.
8. Implement log-based alerts for security anomalies (multiple failed logins, unusual export activity).
9. Document logging schema and sample entries for analysts.
10. Train developers on log hygiene to maintain useful signal-to-noise ratio.

---

## 10. Security & Compliance
1. Implement principle of least privilege for all services; restrict database users by role (read-only vs read-write).
2. Ensure environment secrets stored securely (Vault, AWS Secrets Manager) with rotation policies.
3. Enforce HTTPS for all external traffic, HSTS for browsers, and TLS for internal services where possible.
4. Conduct regular vulnerability scans (Snyk, Dependabot) for Python and Node dependencies.
5. Run static analysis (Bandit) for Python and ESLint security rules for frontend.
6. Audit AI outputs for compliance (anti-money laundering, fair housing) using `compliance_monitoring_service` and human review.
7. Implement DLP policies preventing unauthorized export of client data.
8. Maintain incident response plan (documented in this handbook) with defined roles and communication steps.
9. Conduct tabletop exercises to prepare team for security incidents.
10. Keep privacy policy and terms of service updated in line with features and data usage.

---

## 11. Quality Engineering & Testing Infrastructure
1. Backend tests (pytest) should run in isolated environment with ephemeral databases (use `docker-compose.smoke.yml`).
2. Frontend Playwright tests run headless; integrate into CI for regression detection.
3. Introduce contract testing (e.g., Pact) between frontend and backend to ensure API compatibility.
4. Implement load testing (Locust/K6) for critical endpoints and AI flows to establish performance baselines.
5. Add integration tests combining backend and Celery (using test broker) for asynchronous flow validation.
6. Track test coverage; set minimum thresholds for backend and frontend to encourage quality.
7. Provide test data management strategy (synthetic data) to avoid production data usage in tests.
8. Automate regression suites triggered nightly to detect flakiness or environment issues early.
9. Document test environments (URLs, credentials, data reset procedure) for QA and stakeholders.
10. Monitor test stability, triage flaky tests promptly, and record flake budgets.

---

## 12. Continuous Integration / Continuous Delivery (CI/CD)
1. Establish GitHub Actions pipelines running lint, unit tests, integration tests, and e2e smoke tests on PRs.
2. Use separate workflows for backend and frontend to optimize runtime and caching.
3. Implement build pipeline producing Docker images tagged with commit SHA and pushing to registry.
4. Include security scanning (Trivy, Snyk) in CI before merging.
5. Automate deployment to staging environment upon merge to main branch; require manual approval for production.
6. Integrate infrastructure tests (Terraform plan/apply) once IaC introduced.
7. Configure Slack/Teams notifications for pipeline results and deployment status.
8. Enforce code owners for critical directories to ensure appropriate reviews.
9. Record deployment metadata (version, change summary) in release tracker for traceability.
10. Maintain rollback scripts or automated rollback tasks for quick recovery.

---

## 13. Process Improvements (Adoption Plan)
1. Automated CI pipelines — design workflows, allocate owner, target completion date, and integrate with repository.
2. Alembic migrations — scaffold migration environment, train developers, enforce migration requirement in PR template.
3. Infrastructure-as-code — prototype Terraform modules for core services, iterate with DevOps team.
4. ADRs (`docs/adr/`) — establish template, require ADR for architectural decisions (AI provider switch, caching strategy, multi-tenancy).
5. Pre-commit hooks — configure `pre-commit` with Black, isort, flake8, mypy, ESLint, Prettier; enforce on CI.
6. Incident response runbooks — build consistent runbook per alert type, store in `docs/runbooks/` (to be created).
7. Security posture — integrate dependency scanning, secret scanning, and periodic penetration tests.
8. Observability enhancements — implement metrics/traces, expand dashboards, document SLOs.
9. Data governance — create data dictionary, access control policies, and request process for data extracts.
10. Release governance — standardize release checklist including documentation updates, test evidence, rollback plan.

---
## 14. Runbooks & Operational Procedures
1. **Backend outage**: Verify `/health` endpoint, inspect API logs, restart service if necessary, escalate if database unreachable.
2. **Database connectivity issue**: Check Postgres container health, review logs for connection limits, apply failover plan if hardware failure.
3. **Redis down**: Restart Redis service, clear corrupted data if necessary (with caution), notify teams about potential queue delays.
4. **Celery backlog**: Inspect queue length, scale workers, identify long-running tasks, and resolve bottlenecks.
5. **AI provider outage**: Switch to fallback provider or degrade to cached responses, inform customer success teams.
6. **Document processing failures**: Review processing logs, identify problematic files, requeue after patching parser issues.
7. **Monitoring alert**: Follow alert-specific runbook detailing diagnostics, mitigation, and communication steps.
8. **Security incident**: Invoke incident response plan, isolate affected systems, begin forensics, communicate with stakeholders.
9. **Deployment rollback**: Use previous image tag, run database rollback if necessary, validate system health post-rollback.
10. **Data ingestion failure**: Inspect logs, fix schema mismatches, re-run ingestion job, notify data consumers.

---

## 15. Incident Response Plan
1. Detection: Alert triggered (monitoring, user report) -> On-call engineer paged.
2. Classification: Determine severity (SEV1-4) based on impact; document in incident tracking tool.
3. Containment: Stabilize system (disable feature, rate limit, isolate component) to stop impact.
4. Communication: Notify stakeholders (engineering leadership, support, customers if needed) with initial summary and ETA.
5. Resolution: Implement fix, monitor system for recovery, document actions taken.
6. Post-incident: Write retrospective including root cause, impact, timeline, and follow-up actions.
7. Knowledge sharing: Update runbooks, add tests or alerts preventing recurrence, share learnings in engineering forum.
8. Metrics: Track MTTR (mean time to recovery), incident frequency, and repeat issues.
9. Training: Conduct drills to keep team prepared, update plan as organization evolves.
10. Tooling: Maintain incident management tooling (pager system, ticketing, status page) with documented procedures.

---

## 16. Data Governance Framework
1. Identify data owners responsible for each dataset, ensuring accountability.
2. Classify data sensitivity levels (public, internal, confidential, restricted).
3. Implement access controls (RBAC) for data queries and exports; log access for auditing.
4. Maintain data dictionary describing fields, definitions, allowed values, and lineage.
5. Establish data request process for analytics teams requiring new datasets or extracts.
6. Schedule regular data quality checks (completeness, accuracy, anomalies) with automated reports.
7. Document data retention and deletion policies; implement scripts enforcing them.
8. Ensure compliance with local regulations (Dubai real estate laws, privacy requirements).
9. Provide onboarding training covering data handling and security protocols.
10. Review governance policies quarterly and after major incidents.

---

## 17. Analytics & Reporting Infrastructure
1. Backend analytics endpoints aggregate metrics for dashboards; future plan includes dedicated analytics warehouse.
2. Build ETL pipelines exporting data from Postgres to analytics store (Snowflake/BigQuery) for BI tools.
3. Document KPI definitions (lead conversion, time-to-close, campaign ROI) to align analytics and product teams.
4. Implement scheduled jobs to refresh analytics views and monitor for failures.
5. Provide self-service dashboards (Looker/Tableau) for stakeholders once data warehouse available.
6. Track AI engagement metrics (message count, feedback scores) for product roadmap decisions.
7. Ensure analytics data is anonymized where possible to protect privacy.
8. Align analytics retention with governance policies; purge stale data as required.
9. Correlate analytics with system metrics to identify performance bottlenecks impacting user behavior.
10. Publish monthly analytics summaries to product/leadership.

---

## 18. Release Readiness Gates (Detailed)
1. **Backend Alignment**: Ensure routers, domain services, and tasks updated for feature; document changes in backend handbook.
2. **Frontend Alignment**: Confirm UI consumes new endpoints, passes tests, updates docs.
3. **Data Preparedness**: Validate datasets, migrations, and data quality for new features.
4. **Testing Evidence**: Provide reports (pytest, Playwright) demonstrating coverage of affected areas.
5. **Security Review**: Evaluate new endpoints, secrets, or data flows with security team.
6. **Performance Baseline**: Run smoke/performance tests verifying no major regressions.
7. **Observability**: Update dashboards, alerts, and logging for new components.
8. **Documentation**: Update handbook sections, runbooks, and user-facing release notes.
9. **Operational Training**: Brief support/reliability teams on new features and known limitations.
10. **Approval**: Product/engineering leadership sign off based on readiness tracker.

---

## 19. Risk Register (Sample)
1. AI provider dependency — Mitigation: maintain fallback provider, monitor quotas.
2. Schema drift — Mitigation: enforce migrations, schema validation, and documentation updates.
3. Data quality degradation — Mitigation: automated validation, alerts, manual reviews.
4. Security breach — Mitigation: IAM controls, monitoring, incident response drills.
5. Queue backlog — Mitigation: autoscale workers, monitor metrics, optimize tasks.
6. Performance regression — Mitigation: load testing, performance budgets, code reviews.
7. Compliance violation — Mitigation: compliance monitoring service, human review, policy training.
8. Documentation drift — Mitigation: doc review in PR checklist, assigned documentation owners.
9. Talent dependency — Mitigation: cross-training, onboarding documentation, shared knowledge base.
10. Infrastructure outage — Mitigation: backups, DR plan, multi-zone deployment.

---

## 20. Tooling & Automation Roadmap
1. Implement internal CLI for tasks (create migration, scaffold router, run smoke tests).
2. Automate dataset refresh pipeline triggered by new data availability.
3. Integrate Slack bots announcing deployments, incidents, and alerts.
4. Build analytics pipeline summarizing AI usage and customer insights for product team.
5. Automate security scanning and patch management across services.
6. Develop infrastructure dashboards reporting cost, utilization, and capacity planning.
7. Create developer portal aggregating documentation, runbooks, and metrics.
8. Introduce feature flag management console for product owners.
9. Build auto-remediation scripts responding to common incidents (restart stuck worker, clear queue).
10. Implement governance automation (automatic access reviews, logging of data exports).

---
## 21. Environment Matrix
1. **Local Development**: Docker Compose or native services, debug logging enabled, sample data, developer credentials.
2. **Integration / QA**: Shared environment with stable datasets, automated tests executed, feature toggles in staging mode.
3. **Staging**: Mirrors production architecture, uses near-production data (sanitized), final verification before release.
4. **Production**: Real customer data, high availability configuration, strict security controls.
5. Document environment URLs, access instructions, and differences (feature flags, data) in central wiki.
6. Use separate API keys/secrets per environment to avoid cross-environment impact.
7. Apply network restrictions preventing non-production environments from accessing production data.
8. Provide data refresh procedures for staging (scrub personal data, inject latest market data).
9. Maintain environment health dashboards and uptime monitors for each environment.
10. Establish change control process for staging/production (maintenance windows, approvals).

---

## 22. Configuration Management
1. Store configuration defaults in `app/core/settings.py` and environment overrides via environment variables.
2. Document all configuration keys, defaults, and expected ranges in environment reference section.
3. Use configuration validation functions (`validate_settings()`) to ensure required variables set in production.
4. Avoid storing secrets in code repositories; use environment injection in deployment pipelines.
5. Version configuration changes (feature toggles, thresholds) and track in change log.
6. Implement configuration reload strategy (hot reload via SIGHUP or environment refresh) where necessary.
7. Provide configuration templates for new environments or tenants.
8. Use feature flags to toggle functionality without redeploying code.
9. Monitor configuration drift using automated checks comparing environments.
10. Document fallback values to prevent downtime if configuration missing.

---

## 23. Change Management & Communication
1. Use shared calendar for planned maintenance, releases, and data migrations.
2. Notify stakeholders before changes impacting availability or functionality.
3. Require RFC (request for comments) for major architectural changes, stored in `docs/adr/` once created.
4. Maintain runbook for emergency changes, including approvals and documentation requirements.
5. Conduct post-change reviews to ensure objectives met and no regressions introduced.
6. Keep change log accessible to support teams for visibility into platform updates.
7. Ensure customer success informed of features impacting customer workflows for proactive communication.
8. Integrate change notifications into support tooling (Zendesk, Intercom) where applicable.
9. Record dependency updates (Python/Node packages) with release notes and compatibility notes.
10. Evaluate change management process quarterly for effectiveness.

---

## 24. Compliance & Legal Considerations
1. Align data handling with Dubai real estate regulations and privacy requirements.
2. Maintain audit logs for property changes, transaction updates, document access, and admin actions.
3. Provide data export/delete functionality to honor user requests (right to access/erasure).
4. Ensure marketing automation complies with communication regulations (opt-in, unsubscribe tracking).
5. Document AI usage in privacy policy, including data sources and guardrails.
6. Conduct periodic compliance audits covering security controls, data access, and retention policies.
7. Manage vendor contracts (AI providers, hosting, analytics) ensuring compliance obligations met.
8. Provide training for staff on compliance requirements and best practices.
9. Establish data processing agreements with customers if required by law.
10. Capture legal approvals before launching new data-intensive features.

---

## 25. Team Roles & Responsibilities (RACI)
1. **Platform Engineering**: Own backend infrastructure, CI/CD, monitoring stack, and reliability.
2. **Data Engineering**: Manage datasets, ingestion pipelines, schema evolution, analytics infrastructure.
3. **AI/ML Team**: Maintain AI models, prompts, RAG pipeline, compliance guardrails.
4. **Frontend/UX**: Implement UI features, accessibility, and client-side performance optimizations.
5. **Security**: Oversee security policies, incident response, vulnerability management.
6. **Product Management**: Prioritize features, define requirements, coordinate releases.
7. **Quality Engineering**: Drive testing strategy, automation, and test environment management.
8. **Support & Customer Success**: Interface with users, relay issues, support incident communication.
9. Document RACI matrix for recurring tasks (deployments, incidents, data refresh) to avoid ownership gaps.
10. Review responsibilities after org changes or major incidents.

---

## 26. Training & Onboarding
1. Provide new hires with access to this handbook, architecture diagrams, and code walkthrough recordings.
2. Schedule onboarding sessions covering backend architecture, frontend structure, AI pipeline, and data governance.
3. Assign mentors for first 4 weeks to guide through dev environment setup and first tasks.
4. Create onboarding checklist including repo access, environment setup, documentation review, and first issue.
5. Encourage shadowing of deployments, incident response, and sprint rituals to accelerate learning.
6. Provide curated list of starter tasks to build familiarity with codebase and processes.
7. Gather feedback from new hires to improve onboarding materials.
8. Update onboarding content whenever major architectural changes occur.
9. Maintain knowledge base with FAQs and troubleshooting guides.
10. Promote pair programming and code reviews to spread knowledge across teams.

---

## 27. Vendor & Third-Party Management
1. Track all third-party services (AI providers, hosting, monitoring, analytics) with owner and contract details.
2. Monitor usage limits and quotas; set alerts approaching thresholds.
3. Review security/compliance documents (SOC2, ISO) for vendors annually.
4. Ensure vendor APIs integrated via secure channels with rotated credentials.
5. Establish contingency plans for critical vendors (fallback providers, multi-vendor strategy).
6. Document support channels (ticketing, email, account manager) for faster escalation.
7. Maintain inventory of SDKs/libraries in use; track updates and deprecations.
8. Evaluate vendor performance and cost as part of quarterly business review.
9. Align vendor contracts with product roadmap timelines to avoid interruptions.
10. Update this inventory whenever new vendors onboarded or services sunset.

---

## 28. Sustainability & Cost Management
1. Monitor infrastructure costs (compute, storage, AI usage) using cloud provider dashboards or custom reports.
2. Optimize resource allocation (right-size containers, scale down idle services) to manage budget.
3. Evaluate serverless or managed services for cost-effective workloads.
4. Track AI cost per interaction and optimize prompts/context size accordingly.
5. Implement budgets and alerts in cloud provider to prevent cost overruns.
6. Archive or compress old data/logs to reduce storage expenses.
7. Review licensing and subscriptions for tools to eliminate unused seats.
8. Incorporate cost considerations in architectural decisions and ADRs.
9. Provide transparency to leadership with monthly cost reports and forecasts.
10. Align sustainability goals (energy-efficient infrastructure, carbon footprint) with company initiatives.

---

## 29. Appendix A — Configuration Reference (Expanded)
1. `DATABASE_URL`
2. `REDIS_URL`
3. `CHROMA_HOST`
4. `CHROMA_PORT`
5. `GOOGLE_API_KEY`
6. `OPENAI_API_KEY`
7. `AI_MODEL`
8. `SECRET_KEY`
9. `JWT_SECRET`
10. `ACCESS_TOKEN_EXPIRE_MINUTES`
11. `JWT_REFRESH_TOKEN_EXPIRE_DAYS`
12. `BCRYPT_ROUNDS`
13. `RATE_LIMIT_REQUESTS_PER_MINUTE`
14. `RATE_LIMIT_LOGIN_ATTEMPTS`
15. `LOG_LEVEL`
16. `HOST`
17. `PORT`
18. `ENABLE_BLUEPRINT_2`
19. `NURTURING_SCHEDULER_ENABLED`
20. `DOCUMENT_GENERATION_ENABLED`
21. `MAX_FILE_SIZE`
22. Add any new variables here; maintain default values and descriptions in documentation.

---

## 30. Appendix B — Monitoring Checklist
1. Verify Prometheus scrape targets up-to-date when services added/removed.
2. Validate Grafana dashboards after data source changes.
3. Simulate alert conditions quarterly to confirm alert delivery and runbook accuracy.
4. Ensure log retention policies enforced (rotation, archival).
5. Review SLO adherence monthly; adjust thresholds as product evolves.
6. Audit monitoring configuration in git to maintain version control.
7. Confirm alert distribution lists accurate (emails, Slack channels, PagerDuty schedules).
8. Evaluate metrics cardinality to avoid performance issues in Prometheus.
9. Document new metrics and their interpretation for team onboarding.
10. Include monitoring updates in release checklist when new features deployed.

---

## 31. Appendix C — Runbook Inventory (To Build)
1. API outage response.
2. Database failover procedure.
3. Redis cache warmup and failover.
4. Celery queue backlog remediation.
5. AI provider fallback activation.
6. Document processing failure handling.
7. Data ingestion pipeline recovery.
8. Security incident triage.
9. Deployment rollback procedure.
10. Performance regression investigation.

---

## 32. Appendix D — Documentation Roadmap
1. Create `docs/adr/` with decision log template for architecture changes.
2. Build `docs/runbooks/` directory containing detailed runbooks referenced above.
3. Develop `docs/security/` outlining policies, assessments, and compliance evidence.
4. Write `docs/data/catalog.md` capturing dataset metadata, ownership, refresh schedule.
5. Maintain `docs/ops/oncall.md` describing on-call expectations, rotation, escalation paths.
6. Create `docs/testing/strategy.md` consolidating testing methodologies and tooling.
7. Provide `docs/product/release_notes/` for summarizing features per release cycle.
8. Update `docs/infra/terraform.md` once IaC implemented.
9. Document `docs/ai/prompts.md` to track prompt templates and guardrail guidelines.
10. Archive outdated documents, linking to replacement handbook sections.

---

## 33. Appendix E — Revision Log
1. 2025-10-02 — Comprehensive platform documentation synced with current repository state, including improvement roadmap.

---
## 34. Appendix F — Operational Checklist
1. Daily: Review monitoring dashboards for anomalies.
2. Daily: Check Celery queue lengths and worker health.
3. Daily: Verify successful completion of scheduled jobs (nurturing, reports).
4. Daily: Monitor AI provider status dashboards for outages.
5. Weekly: Rotate logs if not automated; ensure disk usage within thresholds.
6. Weekly: Review security alerts and dependency updates.
7. Weekly: Validate data ingest jobs and update dataset catalog with changes.
8. Weekly: Sync documentation updates (handbooks, runbooks) with team changes.
9. Biweekly: Conduct performance benchmark runs comparing to baseline.
10. Monthly: Review cost reports and optimize resources as needed.
11. Monthly: Test backup restore procedure for database and vector store.
12. Monthly: Run incident drills focused on top risks (AI outage, database failure).
13. Monthly: Audit access controls, remove unused accounts, rotate critical secrets.
14. Quarterly: Update risk register, governance policies, and compliance evidence.
15. Quarterly: Review architecture and ADR backlog for outdated decisions.
16. Quarterly: Evaluate vendor performance and alternative options.
17. Release Day: Confirm readiness tracker complete, tests passed, documentation updated.
18. Release Day: Monitor key metrics post-deployment and validate functionality.
19. Post-Release: Collect feedback from support/product to plan improvements.
20. As Needed: Create new runbooks when novel incidents occur.

---
## 35. Appendix G — Key Contacts & Escalation
1. Platform Engineering Lead — owns backend infrastructure decisions, first escalation post-on-call.
2. Data Engineering Lead — responsible for dataset issues, ingestion failures, analytics anomalies.
3. AI/ML Lead — handles provider changes, AI quality incidents, guardrail updates.
4. Security Officer — oversees incidents involving data breaches or vulnerabilities.
5. Product Manager — coordinates release scope, communicates with stakeholders.
6. Support Manager — liaises with customers during incidents, collects impact details.
7. DevOps On-call — primary responder for infrastructure alerts.
8. Keep contact list updated in internal wiki with backup contacts and after-hours policies.

---
## 36. Appendix H — Future Reviews
1. Schedule platform architecture review in Q4 to assess readiness for multi-tenancy and regional expansion.
2. Plan AI ethics review involving legal/compliance to evaluate model transparency and bias mitigation.
3. Organize documentation audit aligning with adoption of new tooling and infrastructure.

---
