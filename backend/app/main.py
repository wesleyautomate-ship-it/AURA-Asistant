"""
PropertyPro AI - Backend API (Clean Architecture)

This FastAPI application provides the single canonical backend for PropertyPro AI,
an intelligent real estate assistant designed for a mobile-first experience.

API Documentation:
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation:    http://localhost:8000/redoc
- OpenAPI schema:         http://localhost:8000/openapi.json

Security Features:
- User authentication with JWT tokens
- Role-based access control (RBAC)
- User data isolation
- Secure session management
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
    Depends,
    WebSocket,
    APIRouter,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Union, Dict, Any, Optional
import os
import json
import importlib

try:
    import google.generativeai as genai
except ImportError:
    logger.warning("Google Generative AI not available - AI features disabled")
    genai = None
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
import pandas as pd
import shutil
import time
import asyncio
from pathlib import Path
from werkzeug.utils import secure_filename

# Import from clean architecture structure
from app.core.settings import get_settings
from app.core.database import get_db, SessionLocal, init_db
from app.core.middleware import (
    get_current_user,
    require_roles,
    RequestLoggingMiddleware,
)
from app import status

# Import routers from clean architecture
try:
    from app.api.v1.property_management import router as property_router

    logger.info("Property management router loaded")
except ImportError as e:
    logger.warning(f"Property management router not loaded: {e}")
    property_router = None

try:
    from app.api.v1.properties_router import router as properties_router

    logger.info("Properties router loaded")
except ImportError as e:
    logger.warning(f"Properties router not loaded: {e}")
    properties_router = None

try:
    from app.api.v1.clients_router import router as clients_router

    logger.info("Clients router loaded")
except ImportError as e:
    logger.warning(f"Clients router not loaded: {e}")
    clients_router = None

try:
    from app.api.v1.transactions_router import router as transactions_router

    logger.info("Transactions router loaded")
except ImportError as e:
    logger.warning(f"Transactions router not loaded: {e}")
    transactions_router = None

try:
    from app.api.v1.chat_sessions_router import (
        router as chat_sessions_router,
        root_router as chat_root_router,
    )

    logger.info("Chat sessions router loaded")
except ImportError as e:
    logger.warning(f"Chat sessions router not loaded: {e}")
    chat_sessions_router = None
    chat_root_router = None

try:
    from app.api.v1.data_router import (
        router as data_router,
        root_router as data_root_router,
    )

    logger.info("Data router loaded")
except ImportError as e:
    logger.warning(f"Data router not loaded: {e}")
    data_router = None
    data_root_router = None

try:
    from app.api.v1.file_processing_router import (
        router as file_processing_router,
        root_router as file_processing_root_router,
    )

    logger.info("File processing router loaded")
except ImportError as e:
    logger.warning(f"File processing router not loaded: {e}")
    file_processing_router = None
    file_processing_root_router = None

try:
    from app.api.v1.performance_router import router as performance_router

    logger.info("Performance router loaded")
except ImportError as e:
    logger.warning(f"Performance router not loaded: {e}")
    performance_router = None

try:
    from app.api.v1.feedback_router import router as feedback_router

    logger.info("Feedback router loaded")
except ImportError as e:
    logger.warning(f"Feedback router not loaded: {e}")
    feedback_router = None

try:
    from app.api.v1.templates_router import router as templates_router

    logger.info("Templates router loaded")
except ImportError as e:
    logger.warning(f"Templates router not loaded: {e}")
    templates_router = None

try:
    from app.api.v1.admin_router import (
        router as admin_router,
        ingest_router as admin_ingest_router,
    )

    logger.info("Admin router loaded")
except ImportError as e:
    logger.warning(f"Admin router not loaded: {e}")
    admin_router = None
    admin_ingest_router = None

# Get settings
settings = get_settings()

# Feature flags -------------------------------------------------------------
logger.info(
    "Features: pdf=%s, vector=%s",
    settings.ENABLE_PDF_WEASYPRINT,
    settings.ENABLE_VECTOR_CHROMA,
)

pdf_feature_enabled = False
if settings.ENABLE_PDF_WEASYPRINT:
    try:
        importlib.import_module("weasyprint")
        pdf_feature_enabled = True
    except Exception as exc:
        logger.warning(
            "PDF feature disabled due to import error: %s",
            exc,
        )
else:
    logger.info("PDF feature disabled")

vector_feature_enabled = False
chromadb_module = None
if settings.ENABLE_VECTOR_CHROMA:
    try:
        chromadb_module = importlib.import_module("chromadb")
        vector_feature_enabled = True
    except Exception as exc:
        logger.warning(
            "Vector/RAG feature disabled due to import error: %s",
            exc,
        )
else:
    logger.info("Vector/RAG feature disabled")

report_router = None
if pdf_feature_enabled:
    try:
        from app.api.v1.report_generation_router import router as report_router

        logger.info("Report generation router loaded")
    except ImportError as e:
        logger.warning(f"Report generation router not loaded: {e}")
        report_router = None
else:
    logger.info("Report generation router skipped (PDF optional features disabled)")

try:
    from app.api.v1.intelligence_router import router as intelligence_router

    logger.info("Intelligence router loaded")
except ImportError as e:
    logger.warning(f"Intelligence router not loaded: {e}")
    intelligence_router = None

# Import AI services from clean architecture
EnhancedRAGService = None
QueryIntent = None
if vector_feature_enabled:
    try:
        from app.domain.ai.rag_service import EnhancedRAGService, QueryIntent

        logger.info("RAG service loaded")
    except Exception as e:
        logger.warning(f"RAG service disabled: {e}")
        EnhancedRAGService = None
        QueryIntent = None
        vector_feature_enabled = False
else:
    logger.info("RAG service skipped (vector features disabled)")

try:
    from app.domain.ai.ai_manager import AIEnhancementManager

    logger.info("AI manager loaded")
except ImportError as e:
    logger.warning(f"AI manager not loaded: {e}")
    AIEnhancementManager = None

try:
    from app.domain.ai.action_engine import ActionEngine

    logger.info("Action engine loaded")
except ImportError as e:
    logger.warning(f"Action engine not loaded: {e}")
    ActionEngine = None

# Import monitoring from clean architecture
include_rag_monitoring_routes = None
if vector_feature_enabled:
    try:
        from app.infrastructure.integrations.rag_monitoring import (
            include_rag_monitoring_routes,
        )

        logger.info("RAG monitoring loaded")
    except Exception as e:
        logger.warning(f"RAG monitoring disabled: {e}")
        include_rag_monitoring_routes = None
else:
    logger.info("RAG monitoring skipped (vector features disabled)")

# Import async processing from clean architecture
try:
    from app.infrastructure.queue.async_processing import router as async_router

    logger.info("Async processing router loaded")
except ImportError as e:
    logger.warning(f"Async processing router not loaded: {e}")
    async_router = None

# Import Blueprint 2.0 routers from clean architecture
documents_router = None
if pdf_feature_enabled:
    try:
        from app.api.v1.documents_router import router as documents_router

        logger.info("Documents router loaded")
    except ImportError as e:
        logger.warning(f"Documents router not loaded: {e}")
        documents_router = None
else:
    logger.info("Documents router skipped (PDF optional features disabled)")

try:
    from app.api.v1.health_router import router as health_v1_router

    logger.info("Health v1 router loaded")
except ImportError as e:
    logger.warning(f"Health v1 router not loaded: {e}")
    health_v1_router = None

try:
    from app.api.v1.auth_router import router as auth_v1_router

    logger.info("Auth v1 router loaded")
except ImportError as e:
    logger.warning(f"Auth v1 router not loaded: {e}")
    auth_v1_router = None

try:
    from app.api.v1.nurturing_router import router as nurturing_router

    logger.info("Nurturing router loaded")
except ImportError as e:
    logger.warning(f"Nurturing router not loaded: {e}")
    nurturing_router = None

try:
    from app.api.v1.ml_advanced_router import router as ml_advanced_router

    logger.info("ML advanced router loaded")
except ImportError as e:
    logger.warning(f"ML advanced router not loaded: {e}")
    ml_advanced_router = None

try:
    from app.api.v1.ml_insights_router import router as ml_insights_router

    logger.info("ML insights router loaded")
except ImportError as e:
    logger.warning(f"ML insights router not loaded: {e}")
    ml_insights_router = None

try:
    from app.api.v1.ml_websocket_router import router as ml_websocket_router

    logger.info("ML websocket router loaded")
except ImportError as e:
    logger.warning(f"ML websocket router not loaded: {e}")
    ml_websocket_router = None

search_optimization_router = None
if vector_feature_enabled:
    try:
        from app.api.v1.search_optimization_router import (
            router as search_optimization_router,
        )

        logger.info("Search optimization router loaded")
    except Exception as e:
        logger.warning(f"Search optimization router disabled: {e}")
        search_optimization_router = None
else:
    logger.info("Search optimization router skipped (vector features disabled)")

database_enhancement_router = None
if vector_feature_enabled:
    try:
        from app.api.v1.database_enhancement_router import (
            router as database_enhancement_router,
        )

        logger.info("Database enhancement router loaded")
    except Exception as e:
        logger.warning(f"Database enhancement router disabled: {e}")
        database_enhancement_router = None
else:
    logger.info("Database enhancement router skipped (vector features disabled)")

# Import Phase 3 routers from clean architecture
try:
    from app.api.v1.phase3_advanced_router import router as phase3_advanced_router

    logger.info("Phase 3 advanced router loaded")
except ImportError as e:
    logger.warning(f"Phase 3 advanced router not loaded: {e}")
    phase3_advanced_router = None

try:
    from app.api.v1.human_expertise_router import router as human_expertise_router

    logger.info("Human expertise router loaded")
except ImportError as e:
    logger.warning(f"Human expertise router not loaded: {e}")
    human_expertise_router = None

try:
    from app.api.v1.ai_request_router import router as ai_request_router

    logger.info("AI request router loaded")
except ImportError as e:
    logger.warning(f"AI request router not loaded: {e}")
    ai_request_router = None

try:
    from app.api.v1.team_management_router import router as team_management_router

    logger.info("Team management router loaded")
except ImportError as e:
    logger.warning(f"Team management router not loaded: {e}")
    team_management_router = None

try:
    from app.api.v1.property_detection_router import router as property_detection_router

    logger.info("Property detection router loaded")
except ImportError as e:
    logger.warning(f"Property detection router not loaded: {e}")
    property_detection_router = None

try:
    from app.api.v1.admin_knowledge_router import router as admin_knowledge_router

    logger.info("Admin knowledge router loaded")
except ImportError as e:
    logger.warning(f"Admin knowledge router not loaded: {e}")
    admin_knowledge_router = None

# Import AURA routers from clean architecture
try:
    from app.api.v1.marketing_automation_router import (
        router as marketing_automation_router,
    )

    logger.info("Marketing automation router loaded")
except ImportError as e:
    logger.warning(f"Marketing automation router not loaded: {e}")
    marketing_automation_router = None

try:
    from app.api.v1.cma_reports_router import router as cma_reports_router

    logger.info("CMA reports router loaded")
except ImportError as e:
    logger.warning(f"CMA reports router not loaded: {e}")
    cma_reports_router = None

try:
    from app.api.v1.social_media_router import router as social_media_router

    logger.info("Social media router loaded")
except ImportError as e:
    logger.warning(f"Social media router not loaded: {e}")
    social_media_router = None

try:
    from app.api.v1.task_orchestration_router import router as task_orchestration_router

    logger.info("Task orchestration router loaded")
except ImportError as e:
    logger.warning(f"Task orchestration router not loaded: {e}")
    task_orchestration_router = None

try:
    from app.api.v1.analytics_router import router as analytics_router

    logger.info("Analytics router loaded")
except ImportError as e:
    logger.warning(f"Analytics router not loaded: {e}")
    analytics_router = None

try:
    from app.api.v1.workflows_router import router as workflows_router

    logger.info("Workflows router loaded")
except ImportError as e:
    logger.warning(f"Workflows router not loaded: {e}")
    workflows_router = None

try:
    from app.api.v1.command_center_router import router as command_center_router

    logger.info("Command center router loaded")
except ImportError as e:
    logger.warning(f"Command center router not loaded: {e}")
    command_center_router = None

try:
    from app.api.v1.tasks_router import router as tasks_router

    logger.info("Tasks router loaded")
except ImportError as e:
    logger.warning(f"Tasks router not loaded: {e}")
    tasks_router = None

# Import models from clean architecture
# NOTE: Temporarily disabled to prevent table redefinition conflicts
# The specific models needed by routers are imported directly in their respective files
try:
    # Only import core models for basic functionality
    from app.core.models import User, UserSession, Permission, Role, AuditLog
    from app.core.models import ChatThread, ChatMessage
    from app.core.models import BrochureDraft, BrochureTemplate
    from app.core.models import Property, PropertyPhoto, PropertyType, PropertyStatus
    
    # Commented out to prevent "properties" table redefinition:
    # from app.domain.listings.brokerage_models import *
    # from app.domain.listings.phase3_advanced_models import *
    # from app.domain.listings.ai_assistant_models import *

    logger.info("Core models loaded (selective import to prevent conflicts)")
except ImportError as e:
    logger.warning(f"Some models could not be imported: {e}")

# Determine AI feature availability
AI_FEATURES_ENABLED = genai is not None and bool(
    getattr(settings, "google_api_key", None)
)
if not AI_FEATURES_ENABLED:
    logger.warning(
        "AI features disabled - configure GOOGLE_API_KEY to enable AI-powered endpoints."
    )

# Create FastAPI app (single canonical API)
app = FastAPI(
    title="PropertyPro AI",
    description="Mobile-first intelligent real estate assistant (Clean Architecture)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS allowed origins: %s", settings.CORS_ALLOWED_ORIGINS)

# Lightweight version value for dev health checks
# Prefer a package __version__, otherwise fall back to 'dev'
VERSION = "dev"
try:
    from app.core import __version__ as _pkg_version  # type: ignore

    if isinstance(_pkg_version, str) and _pkg_version:
        VERSION = _pkg_version
except Exception:
    # Keep default VERSION = 'dev'
    pass

# Status endpoints ---------------------------------------------------------


@app.get("/healthz")
async def healthz():
    """Simple liveness endpoint."""
    return status.liveness()


@app.get("/api/v1/healthz")
async def api_healthz():
    """API-prefixed liveness endpoint (frontend compatibility)."""
    return status.liveness()


@app.get("/readyz")
async def readyz():
    """Readiness endpoint for orchestrators and load balancers."""
    configured_store = (
        getattr(settings, "object_store_path", None)
        or getattr(settings, "OBJECT_STORE_PATH", None)
    )
    object_store_path = Path(configured_store) if configured_store else None
    payload = status.readiness(SessionLocal, object_store_path)
    if not payload.get("ok", False):
        return JSONResponse(payload, status_code=503)
    return payload


@app.get("/api/v1/readyz")
async def api_readyz():
    """API-prefixed readiness endpoint (frontend compatibility)."""
    configured_store = (
        getattr(settings, "object_store_path", None)
        or getattr(settings, "OBJECT_STORE_PATH", None)
    )
    object_store_path = Path(configured_store) if configured_store else None
    payload = status.readiness(SessionLocal, object_store_path)
    if not payload.get("ok", False):
        return JSONResponse(payload, status_code=503)
    return payload


@app.get("/version")
async def version():
    """Expose build metadata."""
    return status.version_info()


@app.get("/api/v1/version")
async def api_version():
    """API-prefixed version endpoint (frontend compatibility)."""
    return status.version_info()


logger.info("Status endpoints ready")

# Dev-only helpers ---------------------------------------------------------
_DEV_ENV_NAMES = {"development", "dev", "local"}
_current_env = str(
    getattr(settings, "ENV", getattr(settings, "environment", "development"))
).lower()

if _current_env in _DEV_ENV_NAMES:

    @app.get("/_dev/whoami", include_in_schema=False)
    async def dev_whoami(current_user: Any = Depends(get_current_user)):
        """Return the active user for quick auth checks."""
        return {
            "user": {
                "id": getattr(current_user, "id", None),
                "email": getattr(current_user, "email", None),
                "role": getattr(current_user, "role", None),
                "is_superuser": getattr(current_user, "is_superuser", False),
                "is_dev_user": getattr(current_user, "is_dev_user", False),
            }
        }

# Helper to register AI-dependent routers with graceful fallback
def register_ai_router(router, prefix: str, tags: list[str], feature_name: str):
    if not router:
        return

    if AI_FEATURES_ENABLED:
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info(f"{feature_name} router included at {prefix}")
        return

    fallback_router = APIRouter(prefix=prefix, tags=[f"{feature_name} (Disabled)"])

    async def ai_disabled_endpoint(*_: Any, **__: Any):
        raise HTTPException(
            status_code=503,
            detail=(
                f"{feature_name} endpoints are currently disabled because AI features "
                "are not configured. Set GOOGLE_API_KEY to enable them."
            ),
        )

    for path in ("", "/{path:path}"):
        fallback_router.add_api_route(
            path,
            ai_disabled_endpoint,
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            include_in_schema=False,
        )

    app.include_router(fallback_router)
    logger.warning(
        f"{feature_name} router disabled - registered fallback stub at {prefix}"
    )


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# Include routers
logger.info("Including routers...")

if property_router:
    app.include_router(property_router, prefix="/api/v1")
    app.include_router(
        property_router, prefix="/api"
    )  # Legacy compatibility for existing clients
    logger.info("Property router included at /api/v1/properties and /api/properties")

if properties_router:
    app.include_router(properties_router, tags=["Properties"])
    logger.info("Properties router included at /api/v1/properties")

if clients_router:
    app.include_router(clients_router, tags=["Clients"])
    logger.info("Clients router included at /api/v1/clients")

if transactions_router:
    app.include_router(transactions_router, tags=["Transactions"])
    logger.info("Transactions router included at /api/v1/transactions")

if chat_sessions_router:
    app.include_router(chat_sessions_router, prefix="/api/chat", tags=["Chat"])
    logger.info("Chat sessions router included")

if chat_root_router:
    app.include_router(chat_root_router, prefix="/api", tags=["Chat Root"])
    logger.info("Chat root router included")

if data_router:
    app.include_router(data_router, prefix="/api/data", tags=["Data"])
    logger.info("Data router included")

if data_root_router:
    app.include_router(data_root_router, prefix="/api", tags=["Data Root"])
    logger.info("Data root router included")

if file_processing_router:
    app.include_router(
        file_processing_router, prefix="/api/files", tags=["File Processing"]
    )
    logger.info("File processing router included")

if file_processing_root_router:
    app.include_router(
        file_processing_root_router, prefix="/api", tags=["File Processing Root"]
    )
    logger.info("File processing root router included")

# Static files for uploads (serves files created by export endpoints)
try:
    app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
    logger.info("Mounted static uploads at /uploads")
except Exception as e:
    logger.warning(f"Failed to mount /uploads: {e}")

# Asset serving for storage service
try:
    from app.services.storage_service import get_storage_service
    from fastapi import Path as PathParam
    
    @app.get("/api/v1/assets/{asset_path:path}")
    async def serve_asset(asset_path: str = PathParam(...)):
        """Serve assets from storage service"""
        storage = get_storage_service()
        return storage.serve_file(asset_path)
        
    logger.info("Asset serving route mounted at /api/v1/assets/")
except Exception as e:
    logger.warning(f"Failed to mount asset serving: {e}")

if performance_router:
    app.include_router(
        performance_router, prefix="/api/performance", tags=["Performance"]
    )
    logger.info("Performance router included")

if feedback_router:
    app.include_router(feedback_router, prefix="/api/feedback", tags=["Feedback"])
    logger.info("Feedback router included")

if admin_router:
    app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
    logger.info("Admin router included")

if admin_ingest_router:
    app.include_router(
        admin_ingest_router, prefix="/api/admin/ingest", tags=["Admin Ingest"]
    )
    logger.info("Admin ingest router included")

if report_router:
    app.include_router(report_router, prefix="/api/reports", tags=["Reports"])
    logger.info("Report router included")

if async_router:
    app.include_router(async_router, prefix="/api/async", tags=["Async Processing"])
    logger.info("Async router included")

if documents_router:
    app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
    logger.info("Documents router included")

# Export router (PDF-dependent features)
if pdf_feature_enabled:
    try:
        from app.api.v1.export_router import router as export_router

        app.include_router(export_router, tags=["Export"])
        logger.info("Export router included at /api/v1/export")
    except ImportError as e:
        logger.warning(f"Export router not loaded: {e}")
else:
    logger.info("Export router skipped (PDF optional features disabled)")

# Brochure router should be available even when PDF rendering is disabled
try:
    from app.api.v1.brochures_router import router as brochures_router

    app.include_router(brochures_router, tags=["Brochures"])
    logger.info("Brochures router included at /api/v1/brochures")
except ImportError as e:
    logger.warning(f"Brochures router not loaded: {e}")

if templates_router:
    app.include_router(templates_router)
    logger.info("Templates router included at /api/v1/templates")

if health_v1_router:
    app.include_router(health_v1_router, prefix="/api/v1", tags=["Health"])
    logger.info("Health v1 router included at /api/v1/health")

if auth_v1_router:
    app.include_router(auth_v1_router, prefix="/api/v1", tags=["Authentication"])
    logger.info("Auth v1 router included at /api/v1/auth")

if nurturing_router:
    app.include_router(nurturing_router, prefix="/api/nurturing", tags=["Nurturing"])
    logger.info("Nurturing router included")

if ml_advanced_router:
    app.include_router(
        ml_advanced_router, prefix="/api/ml/advanced", tags=["ML Advanced"]
    )
    logger.info("ML advanced router included")

if ml_insights_router:
    app.include_router(
        ml_insights_router, prefix="/api/ml/insights", tags=["ML Insights"]
    )
    logger.info("ML insights router included")

if ml_websocket_router:
    app.include_router(
        ml_websocket_router, prefix="/api/ml/websocket", tags=["ML WebSocket"]
    )
    logger.info("ML websocket router included")

if search_optimization_router:
    app.include_router(
        search_optimization_router, prefix="/api/search", tags=["Search Optimization"]
    )
    logger.info("Search optimization router included")

if database_enhancement_router:
    app.include_router(
        database_enhancement_router,
        prefix="/api/database",
        tags=["Database Enhancement"],
    )
    logger.info("Database enhancement router included")

if phase3_advanced_router:
    app.include_router(
        phase3_advanced_router, prefix="/api/phase3", tags=["Phase 3 Advanced"]
    )
    logger.info("Phase 3 advanced router included")

if human_expertise_router:
    app.include_router(human_expertise_router, prefix="/api/v1", tags=["Human Experts"])
    logger.info("Human expertise router included at /api/v1/experts")

# AI request router - register with correct path
if ai_request_router:
    app.include_router(ai_request_router, tags=["AI Requests"])
    logger.info("AI request router included at /api/requests")

if team_management_router:
    app.include_router(
        team_management_router, prefix="/api/teams", tags=["Team Management"]
    )
    logger.info("Team management router included")

register_ai_router(
    property_detection_router,
    "/api/property-detection",
    ["Property Detection"],
    "Property detection",
)

register_ai_router(
    admin_knowledge_router,
    "/api/admin/knowledge",
    ["Admin Knowledge"],
    "Admin knowledge",
)

# Include AURA routers
if intelligence_router:
    app.include_router(
        intelligence_router, prefix="/api/v1", tags=["Intelligence Pipeline"]
    )
    logger.info("Intelligence router included at /api/v1/intelligence")

# Explicit chat console shim to ensure /api/v1/intelligence/chat is registered
try:
    from app.api.v1.chat_console_router import router as chat_console_router

    app.include_router(
        chat_console_router, prefix="/api/v1", tags=["Intelligence Pipeline"]
    )
    logger.info("Chat console router included at /api/v1/intelligence/chat")
except ImportError as e:
    logger.warning(f"Chat console router not loaded: {e}")

register_ai_router(
    marketing_automation_router,
    "/api/v1/marketing",
    ["AURA Marketing"],
    "Marketing automation",
)

register_ai_router(cma_reports_router, "/api/v1/cma", ["AURA CMA"], "CMA reports")

register_ai_router(
    social_media_router, "/api/v1/social", ["AURA Social"], "Social media"
)

register_ai_router(
    analytics_router, "/api/v1/analytics", ["AURA Analytics"], "Analytics"
)

register_ai_router(
    workflows_router, "/api/v1/workflows", ["AURA Workflows"], "Workflows"
)

register_ai_router(
    task_orchestration_router,
    "/api/v1/orchestration",
    ["AI Task Orchestration"],
    "Task orchestration",
)

# Include command center router
if command_center_router:
    app.include_router(command_center_router, prefix="/api/v1", tags=["Command Center"])
    logger.info("Command center router included at /api/v1/command-center")

# Include tasks router
if tasks_router:
    app.include_router(tasks_router, tags=["Tasks"])
    logger.info("Tasks router included at /api/v1/tasks")

# Include RAG monitoring routes
if include_rag_monitoring_routes:
    include_rag_monitoring_routes(app)
    logger.info("RAG monitoring routes included")


@app.on_event("startup")
def ensure_database_initialized() -> None:
    """Ensure database schema exists before serving requests."""
    try:
        init_db()
    except Exception as exc:  # pragma: no cover - startup safety
        logger.error("Database initialization failed: %s", exc)
logger.info("Starting PropertyPro AI Backend")

# Development endpoint for AI requests
@app.get("/api/requests/dev")
async def requests_dev():
    """Get mock AI requests for frontend development"""
    return [
        {
            "id": "1",
            "team": "marketing",
            "title": "Create listing description for 3-bedroom condo",
            "description": "Need a compelling listing description for a modern 3-bedroom condo in downtown with city views",
            "status": "queued",
            "eta": "2025-10-05T20:00:00Z",
            "priority": 7,
            "created_at": "2025-10-05T19:45:00Z",
            "updated_at": "2025-10-05T19:45:00Z",
            "steps": [
                {"step": "queued", "status": "completed", "progress": 100},
                {"step": "planning", "status": "pending", "progress": 0},
            ],
            "deliverables": [],
        },
        {
            "id": "2",
            "team": "analytics",
            "title": "Market analysis for Miami Beach properties",
            "description": "Analyze recent sales trends and pricing in Miami Beach area",
            "status": "processing",
            "eta": "2025-10-05T20:10:00Z",
            "priority": 5,
            "created_at": "2025-10-05T18:45:00Z",
            "updated_at": "2025-10-05T19:45:00Z",
            "steps": [
                {"step": "queued", "status": "completed", "progress": 100},
                {"step": "planning", "status": "completed", "progress": 100},
                {"step": "generating", "status": "in_progress", "progress": 65},
            ],
            "deliverables": [],
        },
    ]


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "PropertyPro AI Backend",
        "architecture": "clean",
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PropertyPro AI - Mobile-first intelligent real estate assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ========================================
# AURA COMMAND CENTER v2.7.1 ROUTERS
# ========================================

# Voice transcription router
try:
    from app.api.v1.voice_router import router as voice_router

    app.include_router(voice_router, tags=["Voice"])
    logger.info("Voice transcription router included at /api/v1/voice")
except ImportError as e:
    logger.warning(f"Voice router not loaded: {e}")

# AI streaming router
try:
    from app.api.v1.ai_streaming_router import router as ai_streaming_router

    app.include_router(ai_streaming_router, tags=["AI Streaming"])
    logger.info("AI streaming router included at /api/v1/ai_request/stream")
except ImportError as e:
    logger.warning(f"AI streaming router not loaded: {e}")
    
# Contacts & Followups minimal API (additive, dev-friendly)
try:
    from app.api.v1.contacts_router import router as contacts_router
    from app.api.v1.followups_router import router as followups_router
    from app.api.v1.ai_contacts_router import router as ai_contacts_router

    app.include_router(contacts_router, prefix="/api/v1")
    app.include_router(followups_router, prefix="/api/v1")
    app.include_router(ai_contacts_router, prefix="/api/v1")
    logger.info("Contacts/followups/ai contacts routers included at root paths")
except ImportError as e:
    logger.warning(f"Contacts/Followups/AI contacts routers not loaded: {e}")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


