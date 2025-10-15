Version: v3.4.1 → v3.6
Mode: AI-assisted coding
Goal: From activation → fully functional, production-ready system
Tracking: ✅ = complete | 🔄 = in-progress | ⏳ = not started

⚙️ Phase 1 — v3.4.1 Activation & Foundation

Activate AI, authentication, and core backend/frontend wiring.

✅	Hour	Deliverable	Output
⏳	1	Verify repo setup	Clean install, confirm .env and dependencies.
⏳	2	Install Vertex AI SDK	pip install google-cloud-aiplatform google-generativeai.
⏳	3	Add settings_ai.py	Centralize AI configuration + API keys.
⏳	4	Implement Gemini Audio (transcribe.py)	Real STT transcription via Gemini Audio.
⏳	5	Implement Gemini Text (generation.py)	AI text generation via Vertex AI SDK.
⏳	6	Wire AI into /intelligence router	Replace mock pipeline with real service calls.
⏳	7	Add AI error mapping	Handle provider and timeout errors gracefully.
⏳	8	Create authStore.ts	JWT login/logout/refresh with Zustand persistence.
⏳	9	Add ProtectedRoute.tsx	Redirect unauthenticated users → login.
⏳	10	Add Login.tsx UI	Basic email/password authentication page.
⏳	11	Inject Auth headers globally	Modify intelligenceApi.ts to use bearer token.
⏳	12	Test Auth Flow	Validate login → refresh → logout.
⏳	13	CommandCenter → Real Transcription	Voice → Gemini Audio → Text.
⏳	14	CommandCenter → Real Generation	Text → Gemini → CMA mock output.
⏳	15	Validate SSE Progress	Ensure streaming works, fallback to polling.
⏳	16	Setup CI/CD skeleton	.github/workflows/build.yml for client + backend.
⏳	17	Docker Build Test	Confirm both client & backend containers start correctly.
⏳	18	Phase QA & Documentation	Verify mocks, AI, and auth all operational.
🧠 Phase 2 — v3.4.2 CMA End-to-End Integration

Create AURA’s first fully working vertical flow (voice → CMA report).

✅	Hour	Deliverable	Output
⏳	1	Define CMAReport schema	types/intelligence.ts interfaces.
⏳	2	Create CMA prompt template	Real estate-specific Gemini prompt.
⏳	3	Extend generation service	Map content_type='CMA_REPORT' to CMA template.
⏳	4	Build /pages/CMAReport.tsx	Interactive CMA report viewer.
⏳	5	Connect CommandCenter → CMA	Voice prompt → CMA report request.
⏳	6	Stream AI progress	Real-time updates of CMA pipeline steps.
⏳	7	Implement content storage	Save CMA outputs to Postgres.
⏳	8	Create /getContent/{id}	Retrieve saved report.
⏳	9	Display report in UI	Render CMA sections dynamically.
⏳	10	Implement PDF export	CMA → downloadable PDF via reportlab.
⏳	11	Add “Recent Reports” feed	Reuse RequestFeed.tsx to show history.
⏳	12	Add “Refine” endpoint	Allow AI to improve CMA with new input.
⏳	13	Error recovery in CommandCenter	Retry/resume failed tasks.
⏳	14	Polish CMA layout	Final UI structure (Summary, Comparables, Insights).
⏳	15	Voice test suite	Multiple test recordings per property type.
⏳	16	Add caching layer (Redis)	Cache CMA requests for 10 min.
⏳	17	Log analytics event	Track CMA generation stats.
⏳	18	QA + Regression	Verify full workflow reliability.
⏳	19	Record internal demo video	Proof of working CMA feature.
⏳	20	Documentation update	CMA_FLOW_COMPLETE.md.
📦 Phase 3 — v3.4.3 Data Population & RAG Context

Give AURA memory and context through embeddings + ChromaDB.

✅	Hour	Deliverable	Output
⏳	1	Gather dataset	Real estate corpus + market data.
⏳	2	Create data_loader.py	Load sample data into Postgres.
⏳	3	Add embedding service	Gemini Embeddings API integration.
⏳	4	Index ChromaDB	Vectorize and store property docs.
⏳	5	Create rag_service.py	Query Chroma + return context.
⏳	6	Integrate RAG with generation	Inject retrieved knowledge into prompts.
⏳	7	Add “Knowledge Refresh” CLI	Re-embed new documents.
⏳	8	Add Celery task	Async embedding refresh jobs.
⏳	9	Add /context/status API	Monitor embedding state.
⏳	10	Add frontend context badge	“Context Active” icon in CommandCenter.
⏳	11–16	Optimize + QA	Query quality testing + RAG latency benchmarks.
📨 Phase 4 — v3.5 Expansion

Expand into multiple AI content types + async processing.

✅	Hour	Deliverable	Output
⏳	1–4	Add Social Post generator	Create Gemini templates for LinkedIn/IG.
⏳	5–7	Add Pitch Deck builder	Generate investment slide content.
⏳	8–10	Add Market Report generator	Data aggregation + analysis summary.
⏳	11–13	Email & Notifications	SendGrid integration + async queue.
⏳	14–16	File Upload pipeline	S3 storage + doc parsing.
⏳	17–20	Async background jobs	Enable Celery worker for long tasks.
⏳	21–24	QA + Docs	Validate all content generators.
🏗️ Phase 5 — v3.6 Performance & Production

Final performance, scaling, and deployment preparation.

✅	Hour	Deliverable	Output
⏳	1–3	Redis caching optimization	Global caching layer for API responses.
⏳	4–6	Query optimization	Add indexes + tune slow queries.
⏳	7–9	Monitoring setup	Sentry, Prometheus, or Cloud Logging.
⏳	10–12	Security hardening	HTTPS, secret vault, rate limiting.
⏳	13–15	Load testing	Simulate 100+ concurrent users.
⏳	16–18	Docker Compose (prod)	Deployable container config.
⏳	19	Backup automation	Daily snapshots for Postgres/Chroma.
⏳	20	Final QA & launch docs	Sign-off and deployment notes.
✅ Progress Key
⏳ = Not Started
🔄 = In Progress
✅ = Complete