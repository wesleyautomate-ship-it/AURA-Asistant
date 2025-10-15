# Agentic Chat (Console) - Changelog Entry

Version: v3.3.1 (Phase 4)

- Backend
  - New SSE chat endpoint: `POST /api/v1/intelligence/chat`
  - Additive models: `chat_threads`, `chat_messages` (SQLite)
  - Tool shim maps intents to existing intelligence pipeline (brochure/CMA/social/email)

- Frontend
  - Route `/chat/console` (feature-flag: `VITE_CHAT_CONSOLE_ENABLED`)
  - New Zustand store and streaming API client
  - 3-pane UI (threads/messages/context), voice hook placeholder

Notes: Root `docs/CHANGELOG.md` has non-UTF8 encoding and could not be appended by the automated patch tool.

