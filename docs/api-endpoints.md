# PropertyPro AI API Endpoint Guide

This guide summarizes the canonical REST and WebSocket endpoints exposed by the FastAPI backend in `backend/app/api/v1`. Use this document as a quick reference while building or testing features. For full architectural detail, consult `docs/handbook/backend.md` Sections 6 and 8.

## Base URL
- Local development: `http://localhost:8000/api/v1`
- Docker Compose: `http://api:8000/api/v1`

All endpoints require a valid JWT unless otherwise noted. Responses follow the Pydantic schemas defined alongside each router.

## Authentication & Accounts
| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/login` | Exchange email/password for access + refresh tokens. |
| POST | `/auth/refresh` | Issue a new access token from a refresh token. |
| POST | `/auth/logout` | Invalidate current session tokens. |

## Core CRM
| Method | Path | Description |
| --- | --- | --- |
| GET | `/clients` | List clients with filter and pagination support. |
| POST | `/clients` | Create a new client record. |
| PATCH | `/clients/{client_id}` | Update client attributes, preferences, or assigned agent. |
| GET | `/properties` | Retrieve portfolio of properties with advanced search filters. |
| POST | `/properties` | Create or import a property listing. |
| PATCH | `/properties/{property_id}` | Update property metadata, pricing, and status. |
| GET | `/transactions` | List transactions with status and commission data. |
| POST | `/transactions` | Record a new transaction or offer. |
| PATCH | `/transactions/{transaction_id}/status` | Move a transaction through the lifecycle; writes to `transaction_history`. |

## AI Assistance & Chat
| Method | Path | Description |
| --- | --- | --- |
| POST | `/ai/assist` | Synchronous AI response using Enhanced RAG pipeline. |
| POST | `/ai/assist/task` | Queue asynchronous AI workflow package; returns task id. |
| POST | `/ai/assist/preview` | Optional dry-run endpoint for prompt validation. |
| POST | `/chat/sessions` | Create a chat session and return session metadata. |
| GET | `/chat/sessions/{session_id}` | Fetch transcript history. |
| WS | `/chat/stream/{session_id}` | WebSocket stream for live AI responses, typing indicators, and follow-up actions. |

## Documents & Knowledge
| Method | Path | Description |
| --- | --- | --- |
| POST | `/documents/upload` | Upload PDF/DOCX/CSV for processing and embedding. |
| GET | `/documents/{document_id}` | Retrieve processed document metadata and download link. |
| POST | `/documents/reindex` | Rebuild ChromaDB embeddings for updated documents. |
| GET | `/admin/knowledge` | List curated knowledge articles (admin only). |
| POST | `/admin/knowledge` | Create or update knowledge entries that feed the AI context. |

## Marketing & Automation
| Method | Path | Description |
| --- | --- | --- |
| GET | `/marketing/campaigns` | List marketing campaigns with performance metrics. |
| POST | `/marketing/campaigns` | Create a campaign with channel mix and scheduling rules. |
| POST | `/marketing/campaigns/{campaign_id}/launch` | Trigger Celery workflow to launch a campaign. |
| GET | `/social/posts` | Retrieve scheduled social posts and status. |
| POST | `/social/posts` | Draft or schedule a social media post. |
| POST | `/nurturing/sequences` | Configure lead nurturing sequences. |
| POST | `/nurturing/sequences/{sequence_id}/pause` | Pause or resume a sequence. |

## Analytics & Reporting
| Method | Path | Description |
| --- | --- | --- |
| GET | `/analytics/summary` | Aggregate KPIs for dashboards. |
| GET | `/analytics/engagement` | Channel engagement metrics (marketing, AI, voice). |
| POST | `/reports/cma` | Generate a comparative market analysis report. |
| POST | `/reports/performance` | Build operational performance packs. |
| GET | `/performance/runtime` | Runtime stats: latency, queue depth, worker heartbeat. |
| GET | `/performance/celery` | Celery queue metrics and task health. |

## Data Operations & Maintenance
| Method | Path | Description |
| --- | --- | --- |
| POST | `/data/import` | Bulk import CSV/JSON data into Postgres tables. |
| GET | `/data/status` | Inspect data ingest job history. |
| POST | `/database/optimize` | Run automated index and vacuum routines (admin). |
| GET | `/database/plan` | Preview optimization steps without executing (admin). |
| POST | `/search/reindex` | Rebuild search indexes and boosting weights. |

## Human Expertise & Feedback
| Method | Path | Description |
| --- | --- | --- |
| POST | `/expertise/reviews` | Submit AI output for human review queue. |
| PATCH | `/expertise/reviews/{review_id}` | Update review decisions, mark as complete. |
| POST | `/feedback` | Record user feedback on AI results or platform features. |
| GET | `/feedback/export` | Export feedback CSV for analysis. |

## Health & Diagnostics
| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Basic health probe used by orchestrators. |
| GET | `/health/details` | Extended diagnostics (DB, Redis, ChromaDB connectivity). |

## WebSocket Summary
- `/chat/stream/{session_id}` — AI chat streaming.
- `/ml/stream` — Streaming updates for long-running ML jobs (beta).

## Notes
- All POST/PATCH endpoints expect JSON unless uploading files; use multipart form data for uploads.
- Pagination typically uses `?limit=` and `?offset=` parameters; refer to router definitions for details.
- Authorization is role-based; refer to `docs/handbook/backend.md` Section 4 for RBAC matrix.
- For testing, leverage the smoke stack `docker-compose.smoke.yml` and run `scripts/run_tests.py --smoke`.

Keep this document updated when new routers or endpoints ship so it remains a reliable entry point for QA and integration work.
