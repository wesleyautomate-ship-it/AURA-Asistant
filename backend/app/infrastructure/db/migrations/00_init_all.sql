\set ON_ERROR_STOP on

-- Run all migrations located in this directory
\i /docker-entrypoint-initdb.d/base_schema_migration.sql
\i /docker-entrypoint-initdb.d/ai_assistant_schema_migration.sql

-- Seed demo agent user for smoke environment
INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
VALUES ('agent1@dubai-estate.com', '$2b$12$SUhrHJmOhziPy1WnvXXz2un0bitEw3AFDbr7jAHH.icQzuVysSpla', 'Demo', 'Agent', 'agent', TRUE, TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
VALUES ('admin@dubai-estate.com', '$2b$12$SUhrHJmOhziPy1WnvXXz2un0bitEw3AFDbr7jAHH.icQzuVysSpla', 'Demo', 'Admin', 'admin', TRUE, TRUE)
ON CONFLICT (email) DO NOTHING;
