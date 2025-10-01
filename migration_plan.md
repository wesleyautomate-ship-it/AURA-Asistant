# PropertyPro AI: Clean Architecture Migration Plan

This document outlines the implementation plan to complete the migration to the new, clean architecture, address critical gaps, and consolidate the codebase. The primary goal is to create a stable, maintainable, and scalable platform by eliminating legacy code and completing in-progress features.

## Guiding Principles

1.  **Single Source of Truth:** There must be only one implementation for any given feature.
2.  **Modern Architecture First:** All new development and consolidation efforts will target the new clean architecture (`backend/app`).
3.  **Security is Paramount:** Critical security gaps must be addressed before any new features are deployed.

---

## Phase 1: Backend Consolidation & Critical Fixes (Highest Priority)

This phase focuses on stabilizing the backend by removing duplicate implementations, fixing the critical authentication flaw, and implementing the missing core AI functionality.

### **Task 1.1: Consolidate AI & Voice Routers**

*   **Objective:** Create a single, unified entry point for all AI and voice-related requests.
*   **Steps:**
    1.  Formally deprecate `backend/app/api/v1/ai_assistant_router.py`.
    2.  Identify any essential logic from the deprecated router (e.g., human-in-the-loop review logic) and merge it into `backend/app/api/v1/ai_request_router.py`.
    3.  Modify the `ai_request_router.py` to handle all request types, ensuring the `/audio` endpoint is the single point of entry for voice commands.
    4.  Remove the deprecated router from the main FastAPI application in `backend/app/main.py`.

### **Task 1.2: Consolidate AI & Voice Services**

*   **Objective:** Unify the backend service logic to prevent code duplication.
*   **Steps:**
    1.  Formally deprecate the entire `backend/services` directory.
    2.  Merge the functionality from `backend/services/ai_request_processing_service.py` and `backend/services/voice_processing_service.py` into the new services located in `backend/app/domain/ai/`.
    3.  The `ai_processing_service.py` should be the single service responsible for orchestrating the AI pipeline.
    4.  The `voice_processing_service.py` should be solely responsible for audio handling and transcription, passing the result to the `ai_processing_service`.

### **Task 1.3: Implement Voice Transcription**

*   **Objective:** Replace the simulated voice transcription with a real implementation.
*   **Steps:**
    1.  Choose a production-grade speech-to-text provider (e.g., Google Speech-to-Text, AWS Transcribe).
    2.  Integrate the chosen provider's SDK into `backend/app/domain/ai/voice_processing_service.py`.
    3.  Replace the `_transcribe_audio` function's mock logic with a real API call to the transcription service.
    4.  Ensure proper error handling for transcription failures.

### **Task 1.4: Fix Frontend Authentication Flaw**

*   **Objective:** Secure the API by ensuring all frontend requests are authenticated.
*   **Steps:**
    1.  Modify the `frontend/src/services/api.ts` module.
    2.  Inside the `apiGet` and `apiPost` functions, retrieve the `authToken` from the Zustand `userStore`.
    3.  If a token exists, add it to the `Authorization` header of every outgoing request (e.g., `headers: { 'Authorization': `Bearer ${token}` }`).

---

## Phase 2: Frontend Refactoring & Feature Completion

This phase focuses on improving the frontend codebase and implementing the remaining mocked features.

### **Task 2.1: Refactor the `CommandCenter` Component**

*   **Objective:** Create a single, responsive `CommandCenter` component for a consistent user experience.
*   **Steps:**
    1.  Delete `frontend/src/components/CommandCenter.mobile.tsx`.
    2.  Refactor `frontend/src/components/CommandCenter.tsx` to be fully responsive.
    3.  Use media queries (or a library like `react-responsive`) to adapt the layout and features for mobile screen sizes.
    4.  Ensure feature parity, including the waveform visualizer (or a suitable mobile alternative) and transcript editing, is available on all screen sizes.

### **Task 2.2: Implement Mocked Frontend Services**

*   **Objective:** Connect the remaining frontend features to the backend.
*   **Steps:**
    1.  For each mocked service (`aiCoordinator.ts`, `socialMediaApi.ts`, `workflowEngine.ts`), implement real API calls to the corresponding backend endpoints.
    2.  Ensure the `voiceService.ts` is refactored to use the central `api.ts` module, removing its hardcoded URL.

---

## Phase 3: Data Migration & Deprecation

This phase focuses on cleaning up the database schema and removing all legacy code.

### **Task 3.1: Consolidate Database Models**

*   **Objective:** Create a single, unified database schema based on the "enhanced" models.
*   **Steps:**
    1.  Formally deprecate the models in `backend/models/ai_assistant_models.py` and `backend/models/brokerage_models.py`.
    2.  The models in `enhanced_real_estate_models.py` and `ai_request_models.py` will be the single source of truth.
    3.  Review all models and ensure relationships are correctly defined and that there is no feature loss from the old models.

### **Task 3.2: Plan and Execute Data Migration**

*   **Objective:** Migrate all data from the old database tables to the new ones without data loss.
*   **Steps:**
    1.  Develop a comprehensive data migration plan.
    2.  Write and test migration scripts (e.g., using Alembic) to move data from the old tables (e.g., `ai_requests`) to the new tables (e.g., `ai_requests_new`).
    3.  Execute the migration scripts in a staging environment first, and then in production during a planned maintenance window.

### **Task 3.3: Final Code Deprecation**

*   **Objective:** Remove all legacy code from the project.
*   **Steps:**
    1.  Once the data migration is complete and verified, delete all deprecated files and directories, including:
        *   `backend/main.py`
        *   The entire `backend/services` directory.
        *   The deprecated model files in `backend/models`.
        *   The deprecated router files.
    2.  Perform a full-text search for any remaining references to the old files and remove them.
