"""
PropertyPro AI - Backend API (Clean Architecture)

This FastAPI application provides the single canonical backend for PropertyPro AI,
an intelligent real estate assistant designed for a mobile-first experience.

📚 API Documentation:
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation:    http://localhost:8000/redoc
- OpenAPI schema:         http://localhost:8000/openapi.json

🔐 Security Features:
- User authentication with JWT tokens
- Role-based access control (RBAC)
- User data isolation
- Secure session management
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, WebSocket, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union, Dict, Any, Optional
import os
import json
try:
    import google.generativeai as genai
except ImportError:
    logger.warning("Google Generative AI not available - AI features disabled")
    genai = None
import chromadb
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
from app.core.database import get_db
from app.core.middleware import get_current_user, require_roles, RequestLoggingMiddleware

# Import routers from clean architecture
try:
    from app.api.v1.property_management import router as property_router
    logger.info("Property management router loaded")
except ImportError as e:
    logger.warning(f"Property management router not loaded: {e}")
    property_router = None

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
    from app.api.v1.chat_sessions_router import router as chat_sessions_router, root_router as chat_root_router
    logger.info("Chat sessions router loaded")
except ImportError as e:
    logger.warning(f"Chat sessions router not loaded: {e}")
    chat_sessions_router = None
    chat_root_router = None

try:
    from app.api.v1.data_router import router as data_router, root_router as data_root_router
    logger.info("Data router loaded")
except ImportError as e:
    logger.warning(f"Data router not loaded: {e}")
    data_router = None
    data_root_router = None

try:
    from app.api.v1.file_processing_router import router as file_processing_router, root_router as file_processing_root_router
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
    from app.api.v1.admin_router import router as admin_router, ingest_router as admin_ingest_router
    logger.info("Admin router loaded")
except ImportError as e:
    logger.warning(f"Admin router not loaded: {e}")
    admin_router = None
    admin_ingest_router = None

try:
    from app.api.v1.report_generation_router import router as report_router
    logger.info("Report generation router loaded")
except ImportError as e:
    logger.warning(f"Report generation router not loaded: {e}")
    report_router = None

# Import AI services from clean architecture
try:
    from app.domain.ai.rag_service import EnhancedRAGService, QueryIntent
    logger.info("RAG service loaded")
except ImportError as e:
    logger.warning(f"RAG service not loaded: {e}")
    EnhancedRAGService = None
    QueryIntent = None

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
try:
    from app.infrastructure.integrations.rag_monitoring import include_rag_monitoring_routes
    logger.info("RAG monitoring loaded")
except ImportError as e:
    logger.warning(f"RAG monitoring not loaded: {e}")
    include_rag_monitoring_routes = None

# Import async processing from clean architecture
try:
    from app.infrastructure.queue.async_processing import router as async_router
    logger.info("Async processing router loaded")
except ImportError as e:
    logger.warning(f"Async processing router not loaded: {e}")
    async_router = None

# Import Blueprint 2.0 routers from clean architecture
try:
    from app.api.v1.documents_router import router as documents_router
    logger.info("Documents router loaded")
except ImportError as e:
    logger.warning(f"Documents router not loaded: {e}")
    documents_router = None

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

try:
    from app.api.v1.search_optimization_router import router as search_optimization_router
    logger.info("Search optimization router loaded")
except ImportError as e:
    logger.warning(f"Search optimization router not loaded: {e}")
    search_optimization_router = None

try:
    from app.api.v1.database_enhancement_router import router as database_enhancement_router
    logger.info("Database enhancement router loaded")
except ImportError as e:
    logger.warning(f"Database enhancement router not loaded: {e}")
    database_enhancement_router = None

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
    from app.api.v1.marketing_automation_router import router as marketing_automation_router
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

# Import models from clean architecture
try:
    from app.domain.listings.brokerage_models import *
    from app.domain.listings.phase3_advanced_models import *
    from app.domain.listings.ai_assistant_models import *
    from app.core.models import *
    logger.info("Models loaded")
except ImportError as e:
    logger.warning(f"Some models could not be imported: {e}")

# Get settings
settings = get_settings()

# Determine AI feature availability
AI_FEATURES_ENABLED = genai is not None and bool(getattr(settings, "google_api_key", None))
if not AI_FEATURES_ENABLED:
    logger.warning("AI features disabled - configure GOOGLE_API_KEY to enable AI-powered endpoints.")

# Create FastAPI app (single canonical API)
app = FastAPI(
    title="PropertyPro AI",
    description="Mobile-first intelligent real estate assistant (Clean Architecture)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
            )
        )

    for path in ("", "/{path:path}"):
        fallback_router.add_api_route(
            path,
            ai_disabled_endpoint,
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            include_in_schema=False
        )

    app.include_router(fallback_router)
    logger.warning(f"{feature_name} router disabled - registered fallback stub at {prefix}")

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
    app.include_router(property_router, prefix="/api")  # Legacy compatibility for existing clients
    logger.info("Property router included at /api/v1/properties and /api/properties")

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
    app.include_router(file_processing_router, prefix="/api/files", tags=["File Processing"])
    logger.info("File processing router included")

if file_processing_root_router:
    app.include_router(file_processing_root_router, prefix="/api", tags=["File Processing Root"])
    logger.info("File processing root router included")

if performance_router:
    app.include_router(performance_router, prefix="/api/performance", tags=["Performance"])
    logger.info("Performance router included")

if feedback_router:
    app.include_router(feedback_router, prefix="/api/feedback", tags=["Feedback"])
    logger.info("Feedback router included")

if admin_router:
    app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
    logger.info("Admin router included")

if admin_ingest_router:
    app.include_router(admin_ingest_router, prefix="/api/admin/ingest", tags=["Admin Ingest"])
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
    app.include_router(ml_advanced_router, prefix="/api/ml/advanced", tags=["ML Advanced"])
    logger.info("ML advanced router included")

if ml_insights_router:
    app.include_router(ml_insights_router, prefix="/api/ml/insights", tags=["ML Insights"])
    logger.info("ML insights router included")

if ml_websocket_router:
    app.include_router(ml_websocket_router, prefix="/api/ml/websocket", tags=["ML WebSocket"])
    logger.info("ML websocket router included")

if search_optimization_router:
    app.include_router(search_optimization_router, prefix="/api/search", tags=["Search Optimization"])
    logger.info("Search optimization router included")

if database_enhancement_router:
    app.include_router(database_enhancement_router, prefix="/api/database", tags=["Database Enhancement"])
    logger.info("Database enhancement router included")

if phase3_advanced_router:
    app.include_router(phase3_advanced_router, prefix="/api/phase3", tags=["Phase 3 Advanced"])
    logger.info("Phase 3 advanced router included")

if human_expertise_router:
    app.include_router(human_expertise_router, prefix="/api/v1", tags=["Human Experts"])
    logger.info("Human expertise router included at /api/v1/experts")

register_ai_router(ai_request_router, "/api/ai/requests", ["AI Requests"], "AI request")

if team_management_router:
    app.include_router(team_management_router, prefix="/api/teams", tags=["Team Management"])
    logger.info("Team management router included")

register_ai_router(property_detection_router, "/api/property-detection", ["Property Detection"], "Property detection")

register_ai_router(admin_knowledge_router, "/api/admin/knowledge", ["Admin Knowledge"], "Admin knowledge")

# Include AURA routers
register_ai_router(marketing_automation_router, "/api/v1/marketing", ["AURA Marketing"], "Marketing automation")

register_ai_router(cma_reports_router, "/api/v1/cma", ["AURA CMA"], "CMA reports")

register_ai_router(social_media_router, "/api/v1/social", ["AURA Social"], "Social media")

register_ai_router(analytics_router, "/api/v1/analytics", ["AURA Analytics"], "Analytics")

register_ai_router(workflows_router, "/api/v1/workflows", ["AURA Workflows"], "Workflows")

register_ai_router(task_orchestration_router, "/api/v1/orchestration", ["AI Task Orchestration"], "Task orchestration")

# Include RAG monitoring routes
if include_rag_monitoring_routes:
    include_rag_monitoring_routes(app)
    logger.info("RAG monitoring routes included")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "PropertyPro AI Backend",
        "architecture": "clean"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PropertyPro AI - Mobile-first intelligent real estate assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

