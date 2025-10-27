## Workflows / Task Orchestration — Audit

### 1. Worker Infrastructure
- `/api/v1/workflows` and `/api/v1/orchestration` enqueue multi-step tasks via `AITaskOrchestrator`. Without the background worker plus Redis, the queue raises connection errors and endpoints return 500.

**Action**: Provide an in-process orchestrator stub for dev/tests that executes tasks synchronously (or records them in SQLite for later polling).

### 2. Template Definitions
- Workflow packages reference `marketing_packages`, `automation_steps`, etc. These tables are missing from the SQLite schema, causing SQL errors when listing packages.

**Action**: Ship migrations + seed data for the standard workflow packages (e.g., “Listing Launch”, “New Lead Nurture”).

### 3. SSE Streaming
- `test_sse_completion.py` fails because `/api/v1/orchestration/sse` expects live events from the worker. Current implementation returns 503 when SSE isn’t configured.

**Action**: Add a mock SSE stream in dev that replays canned events, so front-end tests can assert streaming behavior.

### 4. Front-End Contracts
- The front-end expects deterministic statuses (`queued`, `in_progress`, `completed`). In dev the orchestrator never updates status fields, so the UI remains stuck on “Queued”.

**Action**: Extend the stub orchestrator to simulate status transitions and timestamps.
