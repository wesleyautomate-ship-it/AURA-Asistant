# Brochure Feature Fix Log

## Phase 1 Highlights (DATE_PLACEHOLDER)
- Added realistic dev brochure schema + seeds (`dev_data/load.py`).
- Rebuilt test fixture (`backend/app/tests/conftest.py`) so brochure drafts, templates, and properties exist for integration tests.
- Patched `/api/v1/templates` to respond to the non-trailing slash path.
- Fixed auth audit logs (occurred_at column) to stabilize login flows used by brochure endpoints.
- All brochure router tests (`app/tests/test_brochure_routes.py`) now pass.
