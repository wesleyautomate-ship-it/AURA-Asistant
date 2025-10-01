# Data & Database Audit Report

## Scope
- **Objective**: Review relational schema, migrations, and data tooling supporting PropertyPro AI’s S.MPLE workflows.
- **Key References**: `backend/app/infrastructure/db/migrations/`, `backend/app/domain/listings/`, `backend/app/core/settings.py`, `scripts/data_pipeline/`, `data/`.

## Schema Overview
- **Migrations**: SQL files such as `backend/app/infrastructure/db/migrations/base_schema_migration.sql`, `ai_assistant_schema_migration.sql`, and `schema_enhancement_migration.sql` define tables for properties, clients, AI requests, and extended brokerage data.
- **ORM Models**: `backend/app/domain/listings/enhanced_real_estate_models.py` and related modules map migrations to SQLAlchemy models used by routers like `clients_router.py` and `transactions_router.py`.
- **Settings Binding**: `backend/app/core/settings.py` resolves `DATABASE_URL` (PostgreSQL) and ensures migrations mount in docker-compose via `db` service volume mapping.

## Data Sources & Pipelines
- **Seed Data**: `data/` directory contains CSVs (`agents.csv`, `clients.csv`, property datasets) and simulated PDF profiles under `data_simulation/` to bootstrap the system.
- **Pipeline Scripts**: `scripts/data_pipeline/cleaning.py` and `enrichment.py` plus `scripts/backup/add_*_to_chroma.py` indicate plans for ingestion and vectorization, though operational integration is not documented.
- **Mock Fallbacks**: Frontend modules (`frontend/src/components/MarketingView.tsx`, `frontend/src/components/SocialMediaView.tsx`) revert to `sampleProperties`, highlighting missing live data flows.

## Gaps & Risks
- **Analytics Storage**: No dedicated tables surfaced for analytics KPIs described in `frontend/docs/analytics-features.md`. Verify `analytics_router.py` persistence.
- **Indexing Strategy**: Raw SQL migrations lack explicit indexes for frequent filters (e.g., `price`, `location`, `status`) used in `property_management.py` search queries.
- **Data Freshness**: Absence of scheduled ETL integration between CSV seeds and live tables; Celery tasks may exist but require confirmation.
- **Schema Documentation**: No ERD or schema summary available; onboarding relies on reading large SQL files.

## Recommended Backlog Items
- **Analytics Tables**: Extend migrations to include CMA snapshots, performance metrics, and market insights to support `frontend/src/components/analytics/` dashboards.
- **Index Enhancements**: Add indexes for `price`, `location`, `status`, `client_status`, and timestamp columns to improve query performance.
- **ETL Pipeline**: Formalize ingestion scripts (e.g., integrate `scripts/data_pipeline/`) into Celery workflows with documentation in `docs/`.
- **Schema Docs**: Auto-generate ERDs or markdown summaries for each migration to align dev teams.

## Confidence
- **Level**: Low-Medium. Large migration footprint reviewed at high level; full verification of all tables vs. UX requirements will require deeper SQL inspection and runtime testing.
