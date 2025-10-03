# PropertyPro AI Roadmap

Updated October 2025 to align with the current codebase and release readiness tracker. Use this roadmap to communicate milestones across product, engineering, and operations teams.

## Phase 1 — Foundation (Complete)
- Unified FastAPI backend (`backend/app`) delivering core CRM, AI, and document workflows.
- Shared frontend workspace (`client/`) with web and mobile apps reusing services, stores, and UI packages.
- Seed datasets ingested into Postgres and ChromaDB; smoke stack available via Docker Compose.
- Baseline monitoring and logging configured; health endpoints integrated with Compose checks.

## Phase 2 — Beta Hardening (In Progress)
1. **Quality Gates**
   - CI pipeline executing backend pytest and frontend build (see `.github/workflows/ci.yml`).
   - Smoke suite automated through `scripts/run_tests.py --smoke` and Playwright scenarios.
2. **Data & Migration Discipline**
   - Alembic workflow adopted for schema evolution, with migration checklists per PR.
   - Dataset validation scripts ensuring CSV/JSON inputs remain consistent.
3. **AI & Workflow Enhancements**
   - Human-in-the-loop review loops wired through `human_expertise_service.py`.
   - Additional intents and action packages for marketing and transaction follow-ups.
4. **UX Polish**
   - Responsive dashboards, voice-assisted chat refinements, and accessibility fixes.

## Phase 3 — Launch Readiness
- Multi-tenant controls (RBAC, data isolation) formalized for production roll-out.
- Infrastructure-as-code (Terraform/Kubernetes) managing staging and production deployments.
- Expanded observability: tracing, advanced alerting, and on-call runbooks.
- Performance baseline established for AI latency, task throughput, and dashboard load times.
- Go-to-market alignment with marketing collateral, pricing, and support workflows.

## Phase 4 — Growth & Automation
- Advanced analytics warehouse powering self-service BI and predictive insights.
- Feature flag platform enabling phased rollouts and A/B testing.
- Marketplace integrations (CRM, MLS, advertising platforms) via documented APIs.
- Automated post-release telemetry reviews feeding product prioritization.
- Continuous compliance audits with automated evidence collection.

## Governance & Tracking
- Use `docs/progress/release-readiness.md` to mark phase gate completion and attach evidence.
- Maintain `docs/progress/dev-journal.md` for weekly updates and decisions.
- Update this roadmap quarterly or when strategic priorities shift.

By aligning execution with these phases, the team can deliver a reliable, AI-first experience for real estate professionals while maintaining operational excellence.
