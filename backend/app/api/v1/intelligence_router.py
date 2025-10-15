"""
Intelligence Router
==================

Unified API endpoints for Aura's intelligence pipeline.
Consolidates transcription, content generation, memory enrichment, and categorization.

Features:
- Mock transcription prompts (AURA_MOCK_MODE)
- Real-time progress streaming via SSE
- JWT authentication and user context
- Comprehensive error handling
- Schema harmonization
"""

import os
import uuid
import json
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    File,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.middleware import get_current_user
from app.core.models import User
from app.core.models import ChatThread, ChatMessage
from app.core.database import engine as core_engine
from app.schemas.intelligence import (
    ContentGenerationRequest,
    TranscriptionRequest,
    RefinementRequest,
    ContentGenerationResponse,
    TranscriptionResponse,
    TaskStatusResponse,
    ContentRetrievalResponse,
    RefinementResponse,
    MockPromptResponse,
    IntelligenceError,
    ValidationErrorResponse,
    StreamProgressEvent,
    ContentType,
    TaskStatus,
)
from app.domain.ai.task_orchestrator import AITaskOrchestrator
from app.domain.ai.rag_service import EnhancedRAGService, QueryIntent

logger = logging.getLogger(__name__)

# Router prefix should be relative to API version; main app includes this under
# prefix "/api/v1", resulting in final path "/api/v1/intelligence".
router = APIRouter(prefix="/intelligence", tags=["Intelligence Pipeline"])

# Mock transcription prompts for testing
MOCK_TRANSCRIPTION_PROMPTS = [
    {
        "text": "Prepare a detailed property valuation report for my client in Dubai Marina.",
        "mock_type": "cma_request",
        "description": "CMA report generation request",
    },
    {
        "text": "Generate a comprehensive social media campaign for my luxury villa listing in Palm Jumeirah.",
        "mock_type": "social_campaign",
        "description": "Social media content generation",
    },
    {
        "text": "Create an investor pitch deck for a mixed-use development project in Downtown Dubai.",
        "mock_type": "pitch_deck",
        "description": "Pitch deck presentation request",
    },
    {
        "text": "Analyze market trends and prepare a market report for Q4 2024 in the UAE real estate sector.",
        "mock_type": "market_analysis",
        "description": "Market trend analysis request",
    },
    {
        "text": "Draft a professional property description for a 3-bedroom apartment with marina views.",
        "mock_type": "property_description",
        "description": "Property listing description",
    },
]

# Check if mock mode is enabled
AURA_MOCK_MODE = os.getenv("AURA_MOCK_MODE", "false").lower() == "true"

# Initialize orchestrator factory
def get_orchestrator(db: Session = Depends(get_db)) -> AITaskOrchestrator:
    """Get task orchestrator instance"""
    return AITaskOrchestrator(lambda: db)


# =============================================================================
# TRANSCRIPTION ENDPOINTS
# =============================================================================


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    request: TranscriptionRequest = None,
    audio_file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Transcribe audio to text with mock prompt support.

    When AURA_MOCK_MODE=true:
    - Returns predefined mock transcription prompts
    - Bypasses real audio processing
    - Useful for UI testing and development

    When AURA_MOCK_MODE=false:
    - Processes real audio files via OpenAI Whisper or Gemini STT
    - Returns actual transcription results
    """
    try:
        # Mock mode: return sample transcription prompts
        if AURA_MOCK_MODE or (request and request.use_mock):
            mock_prompt = random.choice(MOCK_TRANSCRIPTION_PROMPTS)

            logger.info(f"Mock transcription returned for user {current_user.id}")

            return TranscriptionResponse(
                text=mock_prompt["text"],
                confidence=0.95,
                language_detected="en",
                is_mock=True,
                processing_time_ms=50,  # Instant mock response
            )

        # Real mode: process actual audio file
        if not audio_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file is required when not in mock mode",
            )

        # Validate audio file
        if audio_file.content_type not in [
            "audio/wav",
            "audio/mp3",
            "audio/mpeg",
            "audio/m4a",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported audio format. Please use WAV, MP3, or M4A.",
            )

        if audio_file.size > 25 * 1024 * 1024:  # 25MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file too large. Maximum size is 25MB.",
            )

        # TODO: Implement real transcription using OpenAI Whisper or Gemini
        # For now, return a placeholder response
        start_time = datetime.utcnow()

        # Simulate processing time
        import asyncio

        await asyncio.sleep(1)

        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        logger.info(f"Audio transcription processed for user {current_user.id}")

        return TranscriptionResponse(
            text="This is a placeholder transcription. Real STT integration coming soon.",
            confidence=0.85,
            language_detected=request.language if request else "en",
            is_mock=False,
            processing_time_ms=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
        )


@router.get("/mock-prompts", response_model=List[MockPromptResponse])
async def get_mock_prompts():
    """
    Get available mock transcription prompts for testing.
    Useful for frontend development and UI testing.
    """
    return [
        MockPromptResponse(
            text=prompt["text"],
            mock_type=prompt["mock_type"],
            description=prompt["description"],
        )
        for prompt in MOCK_TRANSCRIPTION_PROMPTS
    ]


# =============================================================================
# CONTENT GENERATION ENDPOINTS
# =============================================================================


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Generate intelligent content based on user input.

    Supports all content types:
    - CMA Reports
    - Social Media Posts
    - Pitch Decks
    - Market Reports
    - Property Descriptions
    - General Content

    Processing is asynchronous with real-time progress available via SSE.
    """
    try:
        context_data = dict(request.context or {})
        resolved_content_type = request.content_type

        if not resolved_content_type and context_data.get("content_type"):
            try:
                resolved_content_type = ContentType(context_data["content_type"])
            except ValueError:
                resolved_content_type = None

        if (
            not resolved_content_type
            and request.user_input
            and "brochure" in request.user_input.lower()
        ):
            resolved_content_type = ContentType.PROPERTY_BROCHURE

        if resolved_content_type == ContentType.PROPERTY_BROCHURE:
            listing_id = (
                context_data.get("listing_id")
                or context_data.get("listingId")
                or context_data.get("target_listing_id")
            )
            if not listing_id:
                listing_id = "listing-downtown-dubai-apt"
            context_data["listing_id"] = listing_id
            context_data.setdefault("content_type", ContentType.PROPERTY_BROCHURE.value)
            context_data.setdefault("origin", "dashboard")
            if not request.user_input or not request.user_input.strip():
                request.user_input = (
                    f"Generate a property brochure for listing {listing_id}"
                )

        resolved_content_type = (
            resolved_content_type or request.content_type or ContentType.GENERAL
        )

        # Submit intelligence task
        task_id = await orchestrator.submit_intelligence_task(
            user_input=request.user_input,
            content_type=resolved_content_type,
            user_id=current_user.id,
            context=context_data,
            quality_requirements=request.quality_requirements.dict()
            if request.quality_requirements
            else None,
        )

        logger.info(
            f"Content generation task {task_id} submitted for user {current_user.id} ({resolved_content_type.value})"
        )

        # Estimate duration based on content type and mock mode
        estimated_duration_ms = 30000  # 30 seconds default
        if AURA_MOCK_MODE:
            estimated_duration_ms = 3000  # 3 seconds for mock
        elif resolved_content_type == ContentType.PITCH_DECK:
            estimated_duration_ms = 60000  # 1 minute for complex content
        elif resolved_content_type == ContentType.PROPERTY_BROCHURE:
            estimated_duration_ms = 45000 if not AURA_MOCK_MODE else 4000

        return ContentGenerationResponse(
            task_id=task_id,
            status=TaskStatus.QUEUED,
            message="Content generation started. Use the task ID to track progress.",
            estimated_duration_ms=estimated_duration_ms,
        )

    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start content generation: {str(e)}",
        )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Get the status of a content generation task.

    Returns detailed progress information including:
    - Current status (queued, processing, completed, failed)
    - Progress percentage (0-100)
    - Current processing step
    - Error messages if failed
    - Completion timestamps
    """
    try:
        task_result = await orchestrator.get_task_status(task_id)

        return TaskStatusResponse(
            task_id=task_result.task_id,
            status=TaskStatus(task_result.status.value),
            progress=task_result.progress,
            current_step=_get_current_step_description(
                task_result.status.value, task_result.progress
            ),
            error_message=task_result.error_message,
            started_at=task_result.started_at,
            completed_at=task_result.completed_at,
            retries=task_result.retries,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}",
        )


@router.get("/content/{content_id}", response_model=ContentRetrievalResponse)
async def get_generated_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve generated content by content ID.

    Returns the complete intelligence content including:
    - Generated structured data and narrative
    - Quality scores and assessments
    - Memory context and insights
    - Actionable recommendations
    - Export-ready status
    """
    try:
        # Query intelligence content from database
        from sqlalchemy import text

        result = db.execute(
            text(
                """
            SELECT content_id, task_id, content_type, title, enhanced,
                   quality_scores, memory_context, generated_content,
                   metadata, export_ready, version, created_at
            FROM intelligence_content 
            WHERE content_id = :content_id
        """
            ),
            {"content_id": content_id},
        )

        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
            )

        # Parse JSON fields
        quality_scores = json.loads(row.quality_scores)
        memory_context = json.loads(row.memory_context)
        generated_content = json.loads(row.generated_content)
        metadata = json.loads(row.metadata)

        # Reconstruct IntelligenceContent object
        from app.schemas.intelligence import (
            IntelligenceContent,
            QualityScores,
            MemoryContext,
            GeneratedContent,
            ContentMetadata,
        )

        content = IntelligenceContent(
            content_id=row.content_id,
            task_id=row.task_id,
            content_type=ContentType(row.content_type),
            title=row.title,
            enhanced=row.enhanced,
            quality_scores=QualityScores(**quality_scores),
            memory_context=MemoryContext(**memory_context),
            generated_content=GeneratedContent(**generated_content),
            metadata=ContentMetadata(**metadata),
            export_ready=row.export_ready,
            version=row.version,
        )

        # Generate recommendations and refinement suggestions
        recommendations = _generate_usage_recommendations(content)
        refinement_suggestions = _generate_refinement_suggestions(content)

        return ContentRetrievalResponse(
            content=content,
            recommendations=recommendations,
            refinement_suggestions=refinement_suggestions,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve content: {str(e)}",
        )


# =============================================================================
# CHAT ORCHESTRATOR (SSE)
# =============================================================================


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


def _ensure_chat_tables():
    """Create chat tables if they don't exist (SQLite-safe, additive)."""
    try:
        from app.core.models import Base

        Base.metadata.create_all(
            bind=core_engine, tables=[ChatThread.__table__, ChatMessage.__table__]
        )
    except Exception as e:
        logger.warning(f"Chat tables ensure failed (may already exist): {e}")


def _detect_tool_intent(text: str) -> Optional[Dict[str, Any]]:
    """Very small intent shim mapping keywords to tool actions."""
    t = text.lower()
    if "brochure" in t:
        return {"name": "create_brochure", "args": {}}
    if "cma" in t or "market analysis" in t:
        return {"name": "create_cma", "args": {}}
    if "social" in t or "post" in t:
        return {"name": "create_social_post", "args": {}}
    if "email" in t and ("draft" in t or "write" in t):
        return {"name": "create_email_draft", "args": {}}
    return None


def _tool_to_task_payload(tool_name: str, message: str) -> Dict[str, Any]:
    """Map tool request to orchestrator input payload."""
    if tool_name == "create_brochure":
        return {
            "content_type": ContentType.PROPERTY_BROCHURE.value,
            "user_input": message,
        }
    if tool_name == "create_cma":
        return {
            "content_type": ContentType.CMA_REPORT.value
            if hasattr(ContentType, "CMA_REPORT")
            else ContentType.GENERAL.value,
            "user_input": message,
        }
    if tool_name == "create_social_post":
        return {"content_type": "marketing_campaign", "user_input": message}
    if tool_name == "create_email_draft":
        return {"content_type": "email_draft", "user_input": message}
    return {"content_type": ContentType.GENERAL.value, "user_input": message}


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """Agentic chat endpoint with SSE streaming and tool invocation shim."""
    _ensure_chat_tables()

    # Upsert thread
    thread_id = request.thread_id or str(uuid.uuid4())
    if not request.thread_id:
        try:
            db.add(ChatThread(id=thread_id, title=None, user_id=current_user.id))
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to create chat thread (may exist): {e}")

    # Persist user message
    try:
        db.add(
            ChatMessage(
                id=str(uuid.uuid4()),
                thread_id=thread_id,
                role="user",
                text=request.message,
            )
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to persist user chat message: {e}")

    # Initialize RAG service
    rag = None
    try:
        rag = EnhancedRAGService()
    except Exception as e:
        logger.warning(f"RAG service unavailable: {e}")

    async def event_stream():
        # thinking
        yield f"event: thinking\ndata: {json.dumps({'status':'starting'})}\n\n"

        # retrieval
        retrieval_sources: List[Dict[str, Any]] = []
        if rag:
            try:
                # Minimal retrieval shim via rag intents
                analysis_intent = QueryIntent.GENERAL
                matches: List[Dict[str, Any]] = []
                # Best-effort: use hybrid_search if present
                try:
                    from app.domain.ai.hybrid_search_engine import HybridSearchEngine

                    hs = HybridSearchEngine()
                    matches = hs.search(request.message, top_k=3) or []
                except Exception:
                    matches = []

                for m in (matches or [])[:3]:
                    retrieval_sources.append(
                        {
                            "source": m.get("source") or "db",
                            "snippet": (m.get("content") or m.get("text") or "")[:200],
                            "score": m.get("score") or 0.0,
                        }
                    )
            except Exception as e:
                logger.warning(f"Retrieval failed: {e}")

        if retrieval_sources:
            yield f"event: retrieval\ndata: {json.dumps({'items': retrieval_sources})}\n\n"

        # tool intent detection
        tool = _detect_tool_intent(request.message)
        if tool:
            payload = _tool_to_task_payload(tool["name"], request.message)
            try:
                # Reuse content generation orchestrator path
                task_id = await orchestrator.submit_intelligence_task(
                    user_input=payload.get("user_input", request.message),
                    content_type=ContentType(
                        payload.get("content_type", ContentType.GENERAL.value)
                    ),
                    user_id=current_user.id,
                    context={"origin": "chat_ui", **(request.metadata or {})},
                )
                yield f"event: tool_invocation\ndata: {json.dumps({'name': tool['name'], 'task_id': task_id})}\n\n"
            except Exception as e:
                logger.error(f"Tool invocation failed: {e}")

        # stream assistant message (mocked incremental chunks)
        assistant_text_parts = [
            "Let me help with that. ",
            "I’m analyzing relevant company docs and listings. ",
            "Here’s a concise answer leveraging our knowledge base.",
        ]
        full_assistant = ""
        for i, part in enumerate(assistant_text_parts):
            await asyncio.sleep(0.3 if i == 0 else 0.6)
            full_assistant += part
            yield f"event: message\ndata: {json.dumps({'content': part})}\n\n"

        # Persist assistant message
        try:
            db.add(
                ChatMessage(
                    id=str(uuid.uuid4()),
                    thread_id=thread_id,
                    role="assistant",
                    text=full_assistant,
                )
            )
            db.commit()
        except Exception as e:
            logger.error(f"Failed to persist assistant message: {e}")

        yield f"event: final\ndata: {json.dumps({'done': True, 'thread_id': thread_id})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/refine/{content_id}", response_model=RefinementResponse)
async def refine_content(
    content_id: str,
    request: RefinementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db),
):
    """
    Refine existing content based on user feedback.

    Takes the original content and applies refinements such as:
    - Tone adjustments
    - Content expansion or condensing
    - Additional data incorporation
    - Style modifications
    - Quality improvements
    """
    try:
        # Verify content exists and user has access
        from sqlalchemy import text

        result = db.execute(
            text(
                """
            SELECT content_id, generated_content, content_type
            FROM intelligence_content 
            WHERE content_id = :content_id
        """
            ),
            {"content_id": content_id},
        )

        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original content not found",
            )

        # Create refinement context
        refinement_context = {
            "original_content_id": content_id,
            "original_content": json.loads(row.generated_content),
            "content_type": row.content_type,
            "refinement_prompt": request.refinement_prompt,
            "is_refinement": True,
            **(request.context or {}),
        }

        # Submit refinement task
        task_id = await orchestrator.submit_intelligence_task(
            user_input=f"Refine this content: {request.refinement_prompt}",
            content_type=ContentType(row.content_type),
            user_id=current_user.id,
            context=refinement_context,
            quality_requirements=request.quality_requirements.dict()
            if request.quality_requirements
            else None,
        )

        logger.info(
            f"Content refinement task {task_id} submitted for content {content_id}"
        )

        return RefinementResponse(
            task_id=task_id,
            original_content_id=content_id,
            refined_content_id=f"refined_{content_id}_{task_id[:8]}",
            status=TaskStatus.QUEUED,
            message="Content refinement started. Use the task ID to track progress.",
            improvements_made=[],  # Will be populated when complete
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content refinement failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start content refinement: {str(e)}",
        )


# =============================================================================
# STREAMING ENDPOINTS
# =============================================================================


@router.get("/stream/{task_id}")
async def stream_task_progress(
    task_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AITaskOrchestrator = Depends(get_orchestrator),
):
    """
    Stream real-time progress updates for a task via Server-Sent Events (SSE).

    Returns a continuous stream of progress events until the task completes.
    Client should listen for 'progress' events and handle completion/errors.
    """

    async def event_generator():
        try:
            async for event in orchestrator.subscribe_to_task_progress(task_id):
                # Format as SSE
                event_data = {
                    "task_id": event.task_id,
                    "status": event.status.value,
                    "progress": event.progress,
                    "current_step": event.current_step,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                }

                yield f"event: {event.event}\n"
                yield f"data: {json.dumps(event_data)}\n\n"

        except Exception as e:
            logger.error(f"Streaming error for task {task_id}: {e}")
            error_event = {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
            yield f"event: error\n"
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================


@router.get("/health")
async def health_check():
    """Health check endpoint for the intelligence pipeline"""
    return {
        "status": "healthy",
        "service": "Intelligence Pipeline",
        "version": "3.4",
        "mock_mode": AURA_MOCK_MODE,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/content-types")
async def get_supported_content_types():
    """Get list of supported content types"""
    return [
        {
            "type": content_type.value,
            "name": content_type.name.replace("_", " ").title(),
            "description": _get_content_type_description(content_type),
        }
        for content_type in ContentType
    ]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _get_current_step_description(status: str, progress: int) -> str:
    """Get human-readable current step description"""
    if status == "queued":
        return "Waiting in queue..."
    elif status == "processing":
        if progress < 20:
            return "Initializing content generation..."
        elif progress < 40:
            return "Analyzing requirements..."
        elif progress < 70:
            return "Generating content..."
        elif progress < 90:
            return "Applying quality checks..."
        else:
            return "Finalizing content..."
    elif status == "completed":
        return "Content generation completed!"
    elif status == "failed":
        return "Content generation failed"
    else:
        return "Processing..."


def _get_content_type_description(content_type: ContentType) -> str:
    """Get description for content type"""
    descriptions = {
        ContentType.CMA_REPORT: "Comprehensive market analysis with comparable properties and pricing",
        ContentType.SOCIAL_POST: "Engaging social media content optimized for platforms",
        ContentType.PITCH_DECK: "Professional investment presentations with financial modeling",
        ContentType.MARKET_REPORT: "Market trend analysis and industry insights",
        ContentType.EMAIL_CAMPAIGN: "Email marketing campaigns with segmentation",
        ContentType.PROPERTY_DESCRIPTION: "Compelling property listings and descriptions",
        ContentType.LISTING_STRATEGY: "Strategic marketing plans for property listings",
        ContentType.GENERAL: "General-purpose content generation",
    }
    return descriptions.get(content_type, "AI-generated content")


def _generate_usage_recommendations(content) -> List[str]:
    """Generate usage recommendations based on content"""
    recommendations = []

    if content.quality_scores.overall_score > 0.9:
        recommendations.append("Content quality is excellent - ready for immediate use")
    elif content.quality_scores.overall_score > 0.8:
        recommendations.append("Good quality content - consider minor refinements")
    else:
        recommendations.append("Content may benefit from refinement before use")

    if content.content_type == ContentType.SOCIAL_POST:
        recommendations.append("Schedule posts during peak engagement hours")
        recommendations.append("Include high-quality images for better performance")
    elif content.content_type == ContentType.CMA_REPORT:
        recommendations.append("Review comparable properties for accuracy")
        recommendations.append("Update market data before client presentation")

    return recommendations


def _generate_refinement_suggestions(content) -> List[str]:
    """Generate refinement suggestions based on content analysis"""
    suggestions = []

    if content.quality_scores.brand_compliance < 0.85:
        suggestions.append("Improve brand consistency and tone")

    if content.quality_scores.content_quality < 0.8:
        suggestions.append("Enhance content depth and detail")

    if not content.enhanced:
        suggestions.append("Enable intelligence features for better results")

    suggestions.extend(
        [
            "Adjust tone and style for target audience",
            "Add more specific examples or data points",
            "Optimize for better engagement and conversion",
        ]
    )

    return suggestions[:5]  # Limit to top 5 suggestions
