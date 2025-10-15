# Aura Real Estate Assistant – Build Notes & Design Decisions
*(Updated for v2.6.9 - Command Center Complete)*

## Overview
**Vision:** A data-driven, AI-first assistant that *creates the work* (content, CMA, listings presentations, market reports) and the agent verifies.  
**Current:** v2.6.9 - Full voice-first Command Center with transcription preview, ready for backend integration.

## What Aura Can Do (backed by our backend)
- AI chat & multi-step task orchestration (requests queue, sockets, costs).  
- CMA generation, market analytics, pricing models, RAG search, document/asset pipeline, compliance gates, marketing automation.  
- Dubai-specific KPIs (AED/sqft, DOM, inventory, absorption) and RERA-aware workflows.

## Current Progress (v2.6.9)
- ✅ Smart Dashboard (Create • Daily Briefing • Analytics) - v2.1-v2.4.1
- ✅ Live KPI simulation, deltas, and AI narrative
- ✅ 2×2 mobile layout, swipe gestures, accessibility
- ✅ Bottom Navigation + Command FAB - v2.5
- ✅ **AI Command Center (Voice-First)** - v2.6.1-v2.6.9
  - Voice/Text mode toggle with smooth transitions
  - Real-time waveform visualization (Web Audio API)
  - Mic amplitude reactivity with 24 animated bars
  - Transcription preview toggle (waveform ↔ text)
  - Recording flow: Mic → Pause/Stop → Preview → Send/Delete
  - Responsive positioning (mobile/tablet/desktop)
  - Safe area insets for modern devices
  - Smooth animations with Framer Motion
- ✅ Comprehensive documentation + changelog system

## Completed Versions

### v2.5 – App Shell ✅
BottomNav (mobile), GlobalHeader (search/?K, avatar), Command FAB, Notifications; route stubs: /tasks, /chat, /analytics, /properties, /contacts, /requests, /settings.

### v2.6.1-v2.6.9 – AI Command Center (Voice-First) ✅
**v2.6.4:** Symmetric mirrored bar waveform centered on baseline  
**v2.6.7:** Real-time mic amplitude visualization, dynamic button visibility  
**v2.6.8:** Responsive positioning above BottomNav with safe area support  
**v2.6.9:** Transcription preview toggle, refined Stop/Send flow with 'stopped' phase  

**Features:**

### v3.3.1 - Agentic Chat (Console) Additions

- Added backend chat orchestrator endpoint: `POST /api/v1/intelligence/chat` (SSE)
- Persist threads/messages in SQLite tables: `chat_threads`, `chat_messages`
- Frontend route `/chat/console` with 3-pane console, feature-flagged by `VITE_CHAT_CONSOLE_ENABLED`
- Zustand store `src/store/chatStore.ts` and streaming client `src/services/api/chatApi.ts`
- Minimal components: Message list, thread list, context panel

Quick test log (manual):
- Start backend; open `/chat/console`
- Send: "Summarize our marketing policy" → streaming chunks appear; context panel updates when retrieval available
- Send: "Create a brochure for listing ID 123" → `tool_invocation` event received with `task_id`
- New thread + rename verified locally (client-side state)

Changed files (key):
- Backend: `backend/app/api/v1/intelligence_router.py`, `backend/app/core/models.py`
- Frontend: `aura-client/src/pages/ChatConsole.tsx`, `aura-client/src/routes/index.tsx`, `aura-client/src/pages/Chat.tsx`, `aura-client/src/store/chatStore.ts`, `aura-client/src/services/api/chatApi.ts`, `aura-client/src/components/chat/*`
- Voice + text modes with smooth toggle
- Live waveform (24 bars, 3px width, spring physics)
- Web Audio API integration with fallback
- Transcription preview (MessageSquare toggle)
- Recording states: idle → listening → paused → stopped → thinking → responding
- Delete/Send actions after stopping
- Glass morphism design, rounded-3xl panel
- Mobile-first with device-specific spacing

## Next UI (capability-driven)

### v2.7 – Backend Integration & Real AI ⌛
- Connect voice transcription API: POST /api/v1/voice/transcribe
- Implement streaming AI responses (replace mock)
- WebSocket for real-time updates
- Command history persistence
- Quick Actions: CMA, "Just Listed", Market Update
- Request queue/status tracking

### v2.8 – Marketing Studio & Orchestration
Content Studio (wizards + preview + brand themes), Asset Library (versions, scheduling), Approvals/Compliance; Request Inbox (live statuses, retry/cancel).

### v2.9 – CMA & Listing Presentation + Market Intelligence
CMA Wizard (comps → adjustments → price → export), Listing Presentation Builder; Area Explorer (AED/sqft, DOM, inventory, absorption, watchlists).

### v3.0 – CRM & Listings (thin slice)
Properties list/grid + AI description panel; Contacts/Leads with lead score & next best action; quick "Generate content" shortcuts.

### v3.1 – Analytics & Reporting
Campaign ROI, funnel, request throughput, model usage/cost; exports.

### Cross-cutting
Auth, Settings, Global Search (?K), ErrorBoundary/skeletons/toasts, WebSocket client.

## Challenges & Solutions
- ✅ Voice reliability → Implemented visual states + text fallback + Web Audio API with graceful degradation (v2.6.7)
- ✅ Smooth animations → Framer Motion with spring physics, AnimatePresence for transitions (v2.6.x)
- ✅ Mobile positioning → Responsive bottom offsets + safe-area-inset support (v2.6.8)
- ⌛ Real-time orchestration → WebSocket + optimistic UI (planned v2.7)
- ⌛ Backend sync for AI → Replace mock with live endpoints (v2.7+)

## Technical Decisions

### State Management (Zustand)
- Simple, performant, TypeScript-first
- Scales well for complex UI state
- No boilerplate compared to Redux

### Animation (Framer Motion)
- Spring physics for organic movement
- AnimatePresence for enter/exit transitions
- GPU-accelerated transforms
- Excellent TypeScript support

### Audio (Web Audio API)
- Native browser support (no external libraries)
- Real-time amplitude analysis
- Fallback sine-wave animation when mic unavailable
- Smooth interpolation prevents jitter

### Voice Flow Design
- **Idle:** Single Mic button (clean, uncluttered)
- **Recording:** Pause + Stop + Send (contextual controls)
- **Paused:** Resume + Stop + Send (frozen waveform)
- **Stopped:** Delete + Send (preview before commit)
- **Responding:** No buttons (clear AI processing state)

## Summary
Aura has evolved from concept → **working voice-first AI console** (v2.6.9) for Dubai real estate. The Command Center provides a polished, professional interface ready for backend integration. Next phase focuses on real AI responses, task orchestration, and marketing automation. The UI philosophy remains: "AI creates, agent verifies."

## Phase 3.2 Notes (2025-10-14)
- Wired the dashboard "Generate Brochure" quick action to the live intelligence pipeline with a streaming modal that keeps the `screenshots/dashboard_baseline.png` and `screenshots/command_center_baseline.png` spacing constants.
- Added a brochure-specific detail view in the Content Viewer, reusing BottomDock actions and matching the card hierarchy from `screenshots/tasks_baseline.png`.
- Extended the intelligence API wrapper with `generateBrochure` plus SSE progress logging, then mapped `PROPERTY_BROCHURE` payloads into the intelligence store.
- Documented the end-to-end flow in `tests/ui_brochure.spec.ts` for manual Playwright verification.
