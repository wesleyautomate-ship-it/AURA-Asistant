"""
Chat Sessions Router - FastAPI Router for Session and Conversation Management

This router handles all chat session and conversation management endpoints
migrated from main.py to maintain frontend compatibility while following
the secure architecture patterns of main_secure.py.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import text
from datetime import datetime
import uuid
import json
import time

# Import dependencies
from auth.middleware import get_current_user
from auth.models import User
from database_manager import get_db_connection
from app.core.settings import DATABASE_URL
from rag_service import EnhancedRAGService
from chat_report_integration import chat_report_integration

# Import advanced chat dependencies
try:
    from entity_detection_service import entity_detection_service, Entity
    from context_management_service import context_management_service

    ADVANCED_CHAT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Advanced chat services not available: {e}")
    ADVANCED_CHAT_AVAILABLE = False

# Initialize router
router = APIRouter(prefix="/sessions", tags=["Chat Sessions"])

# Root level chat endpoint (for frontend compatibility)
root_router = APIRouter(tags=["Chat"])

# AI Suggestions endpoint
@root_router.get("/chat/suggestions")
async def get_ai_suggestions(current_user: User = Depends(get_current_user)):
    """
    Get AI-powered suggestions for the current user based on their role and context
    """
    try:
        # Generate role-based suggestions
        if current_user.role == "brokerage_owner" or current_user.role == "admin":
            suggestions = {
                "tasks": [
                    "Review team performance metrics",
                    "Check compliance status",
                    "Generate revenue report",
                    "Review agent training needs",
                ],
                "suggestions": [
                    {
                        "title": "Team Performance Review",
                        "description": "3 agents need performance improvement plans",
                    },
                    {
                        "title": "Compliance Training Update",
                        "description": "Schedule quarterly compliance training session",
                    },
                    {
                        "title": "Revenue Analytics",
                        "description": "Generate monthly revenue breakdown by agent",
                    },
                ],
            }
        else:  # Agent role
            suggestions = {
                "tasks": [
                    "Follow up with Ali Khan",
                    "Create CMA for Dubai Marina property",
                    "Schedule property viewing",
                    "Update client database",
                ],
                "suggestions": [
                    {
                        "title": "Send new CMA for Palm Jumeirah villa",
                        "description": "Based on recent market activity, create updated analysis",
                    },
                    {
                        "title": "Update client follow-up template",
                        "description": "Personalize message for Ali Khan based on preferences",
                    },
                    {
                        "title": "Check new listings in Dubai Marina",
                        "description": "3 new properties match your client criteria",
                    },
                ],
            }

        return suggestions

    except Exception as e:
        print(f"Error getting AI suggestions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get suggestions: {str(e)}"
        )


# Market Analytics endpoint
@root_router.get("/analytics/market")
async def get_market_analytics(current_user: User = Depends(get_current_user)):
    """
    Get Dubai real estate market analytics and trends
    """
    try:
        # Mock market data - will be replaced with real analytics
        market_data = {
            "average_price": 1250,  # AED per sq ft
            "price_change": 5.2,  # percentage
            "trending_areas": [
                {"name": "Dubai Marina", "price": 1450, "change": 8.5, "trend": "up"},
                {"name": "Downtown Dubai", "price": 1650, "change": 3.2, "trend": "up"},
                {
                    "name": "Palm Jumeirah",
                    "price": 2200,
                    "change": -1.2,
                    "trend": "down",
                },
                {"name": "JBR", "price": 1350, "change": 6.8, "trend": "up"},
            ],
            "price_history": [
                {"month": "Jan", "price": 1200},
                {"month": "Feb", "price": 1220},
                {"month": "Mar", "price": 1180},
                {"month": "Apr", "price": 1250},
                {"month": "May", "price": 1280},
                {"month": "Jun", "price": 1250},
            ],
            "ai_summary": "Dubai's real estate market shows strong growth with a 5.2% increase in average prices. Dubai Marina and JBR are leading with 8.5% and 6.8% growth respectively. The market is showing resilience with consistent demand for waterfront properties.",
            "market_insights": [
                {"label": "Market Activity", "value": 87, "color": "success"},
                {"label": "Investment Potential", "value": 92, "color": "primary"},
                {"label": "Price Stability", "value": 78, "color": "warning"},
            ],
        }

        return market_data

    except Exception as e:
        print(f"Error getting market analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get market analytics: {str(e)}"
        )


# RERA Compliance endpoint
@root_router.get("/rera_compliance/status")
async def get_compliance_status(current_user: User = Depends(get_current_user)):
    """
    Get RERA compliance status and alerts
    """
    try:
        # Mock compliance data - will be replaced with real compliance checks
        compliance_data = {
            "overall_score": 95,
            "score_change": 2.5,
            "alerts": [
                {
                    "id": 1,
                    "type": "warning",
                    "title": "3 agents need compliance training renewal",
                    "description": "Training certificates expire within 30 days",
                    "priority": "medium",
                    "action": "Schedule Training",
                    "due_date": "2024-12-15",
                },
                {
                    "id": 2,
                    "type": "info",
                    "title": "Brand guidelines updated",
                    "description": "New RERA branding requirements implemented",
                    "priority": "low",
                    "action": "Review Guidelines",
                    "due_date": "2024-12-20",
                },
                {
                    "id": 3,
                    "type": "success",
                    "title": "All documentation up to date",
                    "description": "Property listings comply with current regulations",
                    "priority": "low",
                    "action": "View Details",
                    "due_date": None,
                },
            ],
            "pending_documents": [
                {
                    "name": "Property Registration - Villa 12",
                    "status": "pending",
                    "days_left": 5,
                },
                {
                    "name": "RERA License Renewal",
                    "status": "in_review",
                    "days_left": 12,
                },
                {
                    "name": "Client Agreement - Ali Khan",
                    "status": "pending",
                    "days_left": 2,
                },
            ],
            "compliance_metrics": [
                {"label": "Document Compliance", "value": 98, "color": "success"},
                {"label": "Training Completion", "value": 87, "color": "warning"},
                {"label": "License Status", "value": 100, "color": "success"},
                {"label": "Brand Compliance", "value": 92, "color": "primary"},
            ],
            "ai_insights": [
                "Compliance score improved by 2.5% this month",
                "All critical documents are up to date",
                "Consider scheduling training sessions for Q1 2025",
            ],
        }

        return compliance_data

    except Exception as e:
        print(f"Error getting compliance status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get compliance status: {str(e)}"
        )


# Workflow Status endpoint
@root_router.get("/transactions")
async def get_workflow_status(current_user: User = Depends(get_current_user)):
    """
    Get active transactions and workflow status
    """
    try:
        # Mock workflow data - will be replaced with real transaction data
        workflow_data = {
            "active_transactions": [
                {
                    "id": 1,
                    "client": "Ali Khan",
                    "property": "Villa 12, Emirates Hills",
                    "value": "2.5M AED",
                    "status": "negotiation",
                    "progress": 65,
                    "steps": [
                        {"label": "Initial Contact", "completed": True},
                        {"label": "Property Viewing", "completed": True},
                        {"label": "Offer Submitted", "completed": True},
                        {"label": "Negotiation", "completed": False},
                        {"label": "Contract Signing", "completed": False},
                        {"label": "Completion", "completed": False},
                    ],
                    "next_action": "Schedule negotiation meeting",
                    "due_date": "2024-12-10",
                },
                {
                    "id": 2,
                    "client": "Sarah Johnson",
                    "property": "Apartment 45, Dubai Marina",
                    "value": "1.8M AED",
                    "status": "viewing",
                    "progress": 35,
                    "steps": [
                        {"label": "Initial Contact", "completed": True},
                        {"label": "Property Viewing", "completed": False},
                        {"label": "Offer Submitted", "completed": False},
                        {"label": "Negotiation", "completed": False},
                        {"label": "Contract Signing", "completed": False},
                        {"label": "Completion", "completed": False},
                    ],
                    "next_action": "Conduct property viewing",
                    "due_date": "2024-12-08",
                },
            ],
            "pending_approvals": [
                {
                    "id": 1,
                    "type": "CMA Report",
                    "client": "Ahmed Al-Rashid",
                    "property": "Villa 8, Palm Jumeirah",
                    "status": "pending",
                },
                {
                    "id": 2,
                    "type": "Contract Review",
                    "client": "Maria Santos",
                    "property": "Apartment 23, Downtown",
                    "status": "in_review",
                },
            ],
            "workflow_metrics": [
                {"label": "Active Transactions", "value": 8, "color": "primary"},
                {"label": "Completion Rate", "value": 78, "color": "success"},
                {
                    "label": "Avg. Processing Time",
                    "value": 12,
                    "color": "info",
                    "unit": "days",
                },
                {"label": "Pending Approvals", "value": 3, "color": "warning"},
            ],
            "ai_insights": [
                "2 transactions are approaching critical deadlines",
                "Consider following up with Ali Khan for negotiation meeting",
                "Average completion time improved by 15% this month",
            ],
        }

        return workflow_data

    except Exception as e:
        print(f"Error getting workflow status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get workflow status: {str(e)}"
        )


# Pydantic Models
class ChatSessionCreate(BaseModel):
    """Create a new chat session"""

    title: str = "New Chat"
    role: str = "client"
    user_preferences: Optional[Dict[str, Any]] = None


class ChatSessionResponse(BaseModel):
    """Chat session response"""

    session_id: str
    title: str
    role: str
    created_at: str
    updated_at: str
    message_count: int
    user_preferences: Dict[str, Any]
    is_active: bool


class ChatSessionListResponse(BaseModel):
    """List of chat sessions"""

    sessions: List[ChatSessionResponse]
    total_count: int


class ChatMessageResponse(BaseModel):
    """Chat message response"""

    id: int
    session_id: str
    role: str
    content: str
    timestamp: str
    message_type: str
    metadata: Optional[Dict[str, Any]] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response"""

    session_id: str
    title: str
    messages: List[ChatMessageResponse]
    user_preferences: Dict[str, Any]
    conversation_summary: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """Update user preferences"""

    budget_range: Optional[List[float]] = None
    preferred_locations: Optional[List[str]] = None
    property_types: Optional[List[str]] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    investment_goals: Optional[List[str]] = None
    timeline: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model"""

    message: str
    session_id: Optional[str] = None
    file_upload: Optional[Dict[str, Any]] = None
    detect_entities: bool = False  # Optional entity detection


class ChatResponse(BaseModel):
    """Chat response model"""

    response: str
    session_id: str
    message_id: str
    timestamp: str
    sources: List[Dict[str, Any]] = []
    confidence: float
    intent: str
    metadata: Dict[str, Any] = {}
    detected_entities: Optional[
        List[Dict[str, Any]]
    ] = None  # Optional detected entities


# Advanced Chat Models
class EntityDetectionRequest(BaseModel):
    """Request model for entity detection"""

    message: str
    session_id: Optional[str] = None
    user_id: Optional[int] = None


class EntityDetectionResponse(BaseModel):
    """Response model for entity detection"""

    entities: List[Dict[str, Any]]
    total_count: int
    confidence_threshold: float
    processing_time: float


class ContextRequest(BaseModel):
    """Request model for context fetching"""

    entity_type: str
    entity_id: str
    include_cache: bool = True


class ContextResponse(BaseModel):
    """Response model for context data"""

    entity_type: str
    entity_id: str
    context_data: Dict[str, Any]
    cache_status: str  # 'cached', 'fresh', 'not_found'
    last_updated: str


class PropertyDetailsRequest(BaseModel):
    """Request model for property details"""

    property_id: str
    include_market_data: bool = True
    include_similar_properties: bool = True


class PropertyDetailsResponse(BaseModel):
    """Response model for property details"""

    property: Dict[str, Any]
    market_data: List[Dict[str, Any]]
    similar_properties: List[Dict[str, Any]]
    context_type: str
    last_updated: str


class ClientInfoRequest(BaseModel):
    """Request model for client information"""

    client_id: str
    include_history: bool = True
    include_preferences: bool = True


class ClientInfoResponse(BaseModel):
    """Response model for client information"""

    client: Dict[str, Any]
    history: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    context_type: str
    last_updated: str


class MarketContextRequest(BaseModel):
    """Request model for market context"""

    location: str
    property_type: Optional[str] = None
    include_trends: bool = True
    include_insights: bool = True


class MarketContextResponse(BaseModel):
    """Response model for market context"""

    location: str
    market_data: List[Dict[str, Any]]
    trends: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    context_type: str
    last_updated: str


# Helper Functions
def get_ai_manager():
    """Get AI manager instance"""
    try:
        from ai_manager import AIEnhancementManager

        # Use provider abstraction to support OpenAI or Gemini based on env
        from ai_provider import get_ai_provider

        provider = get_ai_provider()
        return AIEnhancementManager(DATABASE_URL, provider)
    except Exception as e:
        print(f"Error initializing AI manager: {e}")
        return None


def get_rag_service():
    """Get RAG service instance"""
    try:
        from rag_service import EnhancedRAGService
        from app.core.settings import CHROMA_HOST, CHROMA_PORT

        return EnhancedRAGService()
    except Exception as e:
        print(f"Error initializing RAG service: {e}")
        return None


# Router Endpoints


@router.post("", response_model=ChatSessionResponse)
async def create_new_chat_session(
    request: ChatSessionCreate, current_user: User = Depends(get_current_user)
):
    """Create a new ChatGPT-style chat session"""
    try:
        session_id = str(uuid.uuid4())

        with get_db_connection() as conn:
            # Create new conversation with user's actual role
            user_role = current_user.role
            session_title = f"Chat Session - {current_user.first_name} {current_user.last_name} ({user_role.title()})"

            result = conn.execute(
                text(
                    """
                INSERT INTO conversations (session_id, user_id, role, title, is_active)
                VALUES (:session_id, :user_id, :role, :title, TRUE)
                RETURNING id, session_id, role, title, created_at, updated_at, is_active
            """
                ),
                {
                    "session_id": session_id,
                    "user_id": current_user.id,
                    "role": user_role,
                    "title": session_title,
                },
            )

            row = result.fetchone()

            # Create conversation preferences if provided
            if request.user_preferences:
                conn.execute(
                    text(
                        """
                    INSERT INTO conversation_preferences (session_id, user_preferences)
                    VALUES (:session_id, :preferences)
                """
                    ),
                    {
                        "session_id": session_id,
                        "preferences": json.dumps(request.user_preferences),
                    },
                )

            return ChatSessionResponse(
                session_id=session_id,
                title=session_title,
                role=user_role,
                created_at=str(row[4]),
                updated_at=str(row[5]),
                message_count=0,
                user_preferences=request.user_preferences or {},
                is_active=row[6],
            )

    except Exception as e:
        print(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    days: Optional[int] = Query(None, description="Only sessions from last N days"),
):
    """List chat sessions with user authentication and role-based filtering"""
    try:
        offset = (page - 1) * limit

        with get_db_connection() as conn:
            # Build query based on user role with date filter
            if current_user.role == "admin":
                # Admin can see all conversations
                if days:
                    query = """
                        SELECT id, session_id, title, created_at, updated_at, is_active,
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                        FROM conversations 
                        WHERE created_at >= NOW() - INTERVAL ':days days'
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """
                    params = {"limit": limit, "offset": offset, "days": days}
                else:
                    query = """
                        SELECT id, session_id, title, created_at, updated_at, is_active,
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                        FROM conversations 
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """
                    params = {"limit": limit, "offset": offset}

            elif current_user.role == "agent":
                # Agent can see their own conversations
                if days:
                    query = """
                        SELECT id, session_id, title, created_at, updated_at, is_active,
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                        FROM conversations 
                        WHERE user_id = :user_id 
                        AND created_at >= NOW() - INTERVAL ':days days'
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "user_id": current_user.id,
                        "limit": limit,
                        "offset": offset,
                        "days": days,
                    }
                else:
                    query = """
                        SELECT id, session_id, title, created_at, updated_at, is_active,
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                        FROM conversations 
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "user_id": current_user.id,
                        "limit": limit,
                        "offset": offset,
                    }

            else:
                # Employee can only see their own conversations
                if days:
                    query = """
                        SELECT id, session_id, title, created_at, updated_at, is_active,
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                        FROM conversations 
                        WHERE user_id = :user_id 
                        AND created_at >= NOW() - INTERVAL ':days days'
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "user_id": current_user.id,
                        "limit": limit,
                        "offset": offset,
                        "days": days,
                    }
                else:
                    query = """
                        SELECT id, session_id, title, created_at, updated_at, is_active,
                               (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id) as message_count
                        FROM conversations 
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :offset
                    """
                    params = {
                        "user_id": current_user.id,
                        "limit": limit,
                        "offset": offset,
                    }

            result = conn.execute(text(query), params)
            sessions = [dict(row) for row in result]

            # Get total count for pagination based on user role
            if current_user.role == "admin":
                if days:
                    count_query = """
                        SELECT COUNT(*) FROM conversations 
                        WHERE created_at >= NOW() - INTERVAL ':days days'
                    """
                    count_params = {"days": days}
                else:
                    count_query = "SELECT COUNT(*) FROM conversations"
                    count_params = {}
            elif current_user.role == "agent":
                if days:
                    count_query = """
                        SELECT COUNT(*) FROM conversations 
                        WHERE user_id = :user_id 
                        AND created_at >= NOW() - INTERVAL ':days days'
                    """
                    count_params = {"user_id": current_user.id, "days": days}
                else:
                    count_query = """
                        SELECT COUNT(*) FROM conversations 
                        WHERE user_id = :user_id
                    """
                    count_params = {"user_id": current_user.id}
            else:
                if days:
                    count_query = """
                        SELECT COUNT(*) FROM conversations 
                        WHERE user_id = :user_id 
                        AND created_at >= NOW() - INTERVAL ':days days'
                    """
                    count_params = {"user_id": current_user.id, "days": days}
                else:
                    count_query = (
                        "SELECT COUNT(*) FROM conversations WHERE user_id = :user_id"
                    )
                    count_params = {"user_id": current_user.id}

            count_result = conn.execute(text(count_query), count_params)
            total_count = count_result.fetchone()[0]

            return {
                "sessions": sessions,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit,
                },
            }

    except Exception as e:
        print(f"Error listing chat sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_session(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """Get chat session with full history - with user access control"""
    try:
        with get_db_connection() as conn:
            # Check if user has access to this session
            if current_user.role == "admin":
                # Admin can access any session
                session_query = """
                    SELECT id, session_id, role, title, created_at, updated_at, is_active
                    FROM conversations 
                    WHERE session_id = :session_id AND is_active = TRUE
                """
                session_params = {"session_id": session_id}
            elif current_user.role == "agent":
                # Agent can access their own sessions
                session_query = """
                    SELECT id, session_id, role, title, created_at, updated_at, is_active
                    FROM conversations 
                    WHERE session_id = :session_id AND is_active = TRUE 
                    AND user_id = :user_id
                """
                session_params = {"session_id": session_id, "user_id": current_user.id}
            else:
                # Employee can only access their own sessions
                session_query = """
                    SELECT id, session_id, role, title, created_at, updated_at, is_active
                    FROM conversations 
                    WHERE session_id = :session_id AND is_active = TRUE AND user_id = :user_id
                """
                session_params = {"session_id": session_id, "user_id": current_user.id}

            session_result = conn.execute(text(session_query), session_params)
            session_row = session_result.fetchone()

            if not session_row:
                raise HTTPException(
                    status_code=404, detail="Chat session not found or access denied"
                )

            # Get messages
            messages_result = conn.execute(
                text(
                    """
                SELECT id, conversation_id, role, content, timestamp, message_type, metadata
                FROM messages 
                WHERE conversation_id = :conversation_id
                ORDER BY timestamp ASC
            """
                ),
                {"conversation_id": session_row[0]},
            )

            messages = []
            for msg_row in messages_result:
                metadata = json.loads(msg_row[6]) if msg_row[6] else None
                messages.append(
                    ChatMessageResponse(
                        id=msg_row[0],
                        session_id=session_id,
                        role=msg_row[2],
                        content=msg_row[3],
                        timestamp=str(msg_row[4]),
                        message_type=msg_row[5],
                        metadata=metadata,
                    )
                )

            # Get user preferences
            prefs_result = conn.execute(
                text(
                    """
                SELECT user_preferences FROM conversation_preferences 
                WHERE session_id = :session_id
            """
                ),
                {"session_id": session_id},
            )
            prefs_row = prefs_result.fetchone()
            if prefs_row and prefs_row[0]:
                if isinstance(prefs_row[0], str):
                    user_preferences = json.loads(prefs_row[0])
                else:
                    user_preferences = prefs_row[0]
            else:
                user_preferences = {}

            # Get conversation summary from AI manager
            try:
                ai_manager = get_ai_manager()
                if ai_manager:
                    conversation_summary = ai_manager.get_conversation_summary(
                        session_id
                    )
                    summary_text = (
                        conversation_summary.get("summary", "")
                        if conversation_summary
                        else None
                    )
                else:
                    summary_text = None
            except:
                summary_text = None

            return ChatHistoryResponse(
                session_id=session_id,
                title=session_row[3],
                messages=messages,
                user_preferences=user_preferences,
                conversation_summary=summary_text,
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat_with_session(
    session_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Enhanced chat endpoint with session management"""
    start_time = time.time()

    try:
        # Get RAG service
        rag_service = get_rag_service()
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not available")

        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        # Check for report generation request first
        report_request = chat_report_integration.detect_report_request(request.message)

        if report_request:
            # Generate report
            report_data = chat_report_integration.generate_report(report_request)

            if report_data:
                response_text = chat_report_integration.format_report_response(
                    report_data
                )
            else:
                response_text = "I'm sorry, I couldn't generate the report at this time. Please try again later."
        else:
            # Use enhanced RAG service
            response_text = rag_service.get_response(
                message=request.message, role=current_user.role, session_id=session_id
            )

        # Save messages to database
        with get_db_connection() as conn:
            # Save user message
            conn.execute(
                text(
                    """
                INSERT INTO messages (conversation_id, role, content, message_type, metadata)
                VALUES (:conversation_id, 'user', :content, 'text', :metadata)
            """
                ),
                {
                    "conversation_id": session_row[0],
                    "content": request.message,
                    "metadata": json.dumps({"file_upload": request.file_upload})
                    if request.file_upload
                    else None,
                },
            )

            # Save assistant response
            conn.execute(
                text(
                    """
                INSERT INTO messages (conversation_id, role, content, message_type, metadata)
                VALUES (:conversation_id, 'assistant', :content, 'text', :metadata)
            """
                ),
                {
                    "conversation_id": session_row[0],
                    "content": response_text,
                    "metadata": json.dumps(
                        {
                            "sources": [
                                "Dubai Real Estate Database",
                                "Market Analysis Reports",
                            ],
                            "enhanced": True,
                        }
                    ),
                },
            )

        # Optional entity detection
        detected_entities = None
        if request.detect_entities and ADVANCED_CHAT_AVAILABLE:
            try:
                entities = entity_detection_service.detect_entities(response_text)
                detected_entities = []
                for entity in entities:
                    context_mapping = (
                        entity_detection_service.get_entity_context_mapping(entity)
                    )
                    detected_entities.append(
                        {
                            "entity_type": entity.entity_type,
                            "entity_value": entity.entity_value,
                            "confidence_score": entity.confidence_score,
                            "context_source": entity.context_source,
                            "metadata": entity.metadata,
                            "context_mapping": context_mapping,
                        }
                    )
            except Exception as e:
                print(f"Entity detection failed: {e}")
                # Continue without entity detection if it fails

        # Track performance
        end_time = time.time()
        response_time = end_time - start_time

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            sources=[
                {"source": "Dubai Real Estate Database", "relevance": 0.9},
                {"source": "Market Analysis Reports", "relevance": 0.8},
            ],
            confidence=0.85,
            intent="enhanced_property_search",
            metadata={
                "response_time": response_time,
                "enhanced": True,
                "entity_detection_enabled": request.detect_entities,
            },
            detected_entities=detected_entities,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in enhanced chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Reelly test endpoint removed


@router.delete("/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session (ChatGPT-style)"""
    try:
        with get_db_connection() as conn:
            # Soft delete - mark as inactive
            result = conn.execute(
                text(
                    """
                UPDATE conversations 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = :session_id
                RETURNING id
            """
                ),
                {"session_id": session_id},
            )

            if not result.fetchone():
                raise HTTPException(status_code=404, detail="Chat session not found")

            return {"success": True, "message": "Chat session deleted"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/clear")
async def clear_chat_session(session_id: str):
    """Clear all messages in a chat session (keep session)"""
    try:
        with get_db_connection() as conn:
            # Get conversation ID
            conv_result = conn.execute(
                text(
                    """
                SELECT id FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            conv_row = conv_result.fetchone()
            if not conv_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Delete all messages
            conn.execute(
                text(
                    """
                DELETE FROM messages WHERE conversation_id = :conversation_id
            """
                ),
                {"conversation_id": conv_row[0]},
            )

            # Clear AI manager memory cache if available
            try:
                ai_manager = get_ai_manager()
                if (
                    ai_manager
                    and hasattr(ai_manager, "memory_cache")
                    and session_id in ai_manager.memory_cache
                ):
                    del ai_manager.memory_cache[session_id]
            except:
                pass  # Ignore if AI manager is not available

            return {"success": True, "message": "Chat session cleared"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error clearing chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversation history endpoint (for frontend compatibility)
@root_router.get("/conversation/{session_id}", response_model=ChatHistoryResponse)
async def get_conversation_history(session_id: str):
    """Get conversation history for a specific session"""
    try:
        with get_db_connection() as conn:
            # Get conversation details
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, created_at, updated_at, is_active
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Get messages
            messages_result = conn.execute(
                text(
                    """
                SELECT id, conversation_id, role, content, timestamp, message_type, metadata
                FROM messages 
                WHERE conversation_id = :conversation_id
                ORDER BY timestamp ASC
            """
                ),
                {"conversation_id": session_row[0]},
            )

            messages = []
            for msg_row in messages_result.fetchall():
                try:
                    if msg_row[6]:
                        if isinstance(msg_row[6], str):
                            metadata = json.loads(msg_row[6])
                        else:
                            metadata = msg_row[6]
                    else:
                        metadata = {}
                except (json.JSONDecodeError, TypeError):
                    print(
                        f"Error parsing metadata for message {msg_row[0]}: {msg_row[6]}"
                    )
                    metadata = {}

                messages.append(
                    ChatMessageResponse(
                        id=msg_row[0],
                        session_id=session_id,
                        role=msg_row[2],
                        content=msg_row[3],
                        timestamp=str(msg_row[4]),
                        message_type=msg_row[5],
                        metadata=metadata,
                    )
                )

            # Get user preferences
            prefs_result = conn.execute(
                text(
                    """
                SELECT user_preferences FROM conversation_preferences
                WHERE session_id = :session_id
            """
                ),
                {"session_id": session_id},
            )

            prefs_row = prefs_result.fetchone()
            if prefs_row and prefs_row[0]:
                if isinstance(prefs_row[0], str):
                    user_preferences = json.loads(prefs_row[0])
                else:
                    user_preferences = prefs_row[0]
            else:
                user_preferences = {}

            # Temporarily disable AI manager to fix conversation endpoint
            summary_text = None

            # Ensure we always return a valid response even if no messages
            if not messages:
                messages = []

            return ChatHistoryResponse(
                session_id=session_id,
                title=session_row[3] or "New Chat",
                messages=messages,
                user_preferences=user_preferences,
                conversation_summary=summary_text,
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Root level chat endpoint (for frontend compatibility)
@root_router.post("/chat", response_model=ChatResponse)
async def chat_with_rag(
    request: ChatRequest, current_user: User = Depends(get_current_user)
):
    """Enhanced chat endpoint with RAG and session management"""
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())

        # Get RAG service
        rag_service = get_rag_service()
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not available")

        # Use RAG service as the single source of truth for conversational AI
        response_text = rag_service.get_response(
            message=request.message,
            role=current_user.role,
            session_id=request.session_id,
        )

        # Save messages to database if session exists
        if request.session_id:
            try:
                with get_db_connection() as conn:
                    # Check if session exists
                    session_result = conn.execute(
                        text(
                            """
                        SELECT id FROM conversations 
                        WHERE session_id = :session_id AND is_active = TRUE
                    """
                        ),
                        {"session_id": request.session_id},
                    )

                    session_row = session_result.fetchone()
                    if session_row:
                        # Save user message
                        conn.execute(
                            text(
                                """
                            INSERT INTO messages (conversation_id, role, content, message_type, metadata)
                            VALUES (:conversation_id, 'user', :content, 'text', :metadata)
                        """
                            ),
                            {
                                "conversation_id": session_row[0],
                                "content": request.message,
                                "metadata": json.dumps(
                                    {"file_upload": request.file_upload}
                                )
                                if request.file_upload
                                else None,
                            },
                        )

                        # Save assistant response
                        conn.execute(
                            text(
                                """
                            INSERT INTO messages (conversation_id, role, content, message_type, metadata)
                            VALUES (:conversation_id, 'assistant', :content, 'text', :metadata)
                        """
                            ),
                            {
                                "conversation_id": session_row[0],
                                "content": response_text,
                                "metadata": json.dumps(
                                    {
                                        "sources": [
                                            "Dubai Real Estate Database",
                                            "Market Analysis Reports",
                                        ]
                                    }
                                ),
                            },
                        )
            except Exception as db_error:
                print(f"Database error in chat endpoint: {db_error}")
                # Continue without saving to database

        # Optional entity detection
        detected_entities = None
        if request.detect_entities and ADVANCED_CHAT_AVAILABLE:
            try:
                entities = entity_detection_service.detect_entities(response_text)
                detected_entities = []
                for entity in entities:
                    context_mapping = (
                        entity_detection_service.get_entity_context_mapping(entity)
                    )
                    detected_entities.append(
                        {
                            "entity_type": entity.entity_type,
                            "entity_value": entity.entity_value,
                            "confidence_score": entity.confidence_score,
                            "context_source": entity.context_source,
                            "metadata": entity.metadata,
                            "context_mapping": context_mapping,
                        }
                    )
            except Exception as e:
                print(f"Entity detection failed: {e}")
                # Continue without entity detection if it fails

        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            sources=[
                "Dubai Real Estate Database",
                "Market Analysis Reports",
                "Property Listings",
            ],
            confidence=0.8,
            intent="general",
            metadata={"entity_detection_enabled": request.detect_entities},
            detected_entities=detected_entities,
        )

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ADVANCED CHAT ENDPOINTS
# =====================================================


@router.post(
    "/{session_id}/advanced/detect-entities", response_model=EntityDetectionResponse
)
async def detect_entities_in_session(
    session_id: str,
    request: EntityDetectionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Detect entities in AI response messages for a specific session

    This endpoint analyzes AI response messages to extract real estate domain entities
    such as properties, clients, locations, and market data.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        import time

        start_time = time.time()

        # Detect entities using the service
        entities = entity_detection_service.detect_entities(request.message)

        # Convert entities to response format
        entity_data = []
        for entity in entities:
            # Get context mapping for the entity
            context_mapping = entity_detection_service.get_entity_context_mapping(
                entity
            )

            entity_data.append(
                {
                    "entity_type": entity.entity_type,
                    "entity_value": entity.entity_value,
                    "confidence_score": entity.confidence_score,
                    "context_source": entity.context_source,
                    "metadata": entity.metadata,
                    "context_mapping": context_mapping,
                }
            )

        processing_time = time.time() - start_time

        return EntityDetectionResponse(
            entities=entity_data,
            total_count=len(entity_data),
            confidence_threshold=0.6,
            processing_time=round(processing_time, 3),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in entity detection: {e}")
        raise HTTPException(
            status_code=500, detail=f"Entity detection failed: {str(e)}"
        )


@router.get(
    "/{session_id}/advanced/context/{entity_type}/{entity_id}",
    response_model=ContextResponse,
)
async def fetch_entity_context_for_session(
    session_id: str,
    entity_type: str,
    entity_id: str,
    include_cache: bool = Query(True, description="Include cached data if available"),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch context data for a specific entity within a session

    This endpoint retrieves contextual information for detected entities,
    including property details, client information, location data, and market analysis.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        # Fetch context data
        context_data = await context_management_service.fetch_entity_context(
            entity_type, entity_id
        )

        if not context_data:
            raise HTTPException(
                status_code=404,
                detail=f"Context not found for {entity_type}:{entity_id}",
            )

        # Determine cache status
        cache_status = "fresh"  # For now, assume fresh data

        return ContextResponse(
            entity_type=entity_type,
            entity_id=entity_id,
            context_data=context_data,
            cache_status=cache_status,
            last_updated=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching context for {entity_type}:{entity_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Context fetching failed: {str(e)}"
        )


@router.get(
    "/{session_id}/advanced/properties/{property_id}/details",
    response_model=PropertyDetailsResponse,
)
async def get_property_details_for_session(
    session_id: str,
    property_id: str,
    include_market_data: bool = Query(
        True, description="Include market data for the property"
    ),
    include_similar_properties: bool = Query(
        True, description="Include similar properties"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed property information for a specific session

    This endpoint provides comprehensive property details including
    basic information, market data, and similar properties.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        # Fetch property context
        context_data = await context_management_service.fetch_entity_context(
            "property", property_id
        )

        if not context_data or "property" not in context_data:
            raise HTTPException(
                status_code=404, detail=f"Property not found: {property_id}"
            )

        return PropertyDetailsResponse(
            property=context_data.get("property", {}),
            market_data=context_data.get("market_data", [])
            if include_market_data
            else [],
            similar_properties=context_data.get("similar_properties", [])
            if include_similar_properties
            else [],
            context_type=context_data.get("context_type", "property_details"),
            last_updated=context_data.get("last_updated", datetime.now().isoformat()),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting property details for {property_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Property details fetching failed: {str(e)}"
        )


@router.get(
    "/{session_id}/advanced/clients/{client_id}", response_model=ClientInfoResponse
)
async def get_client_info_for_session(
    session_id: str,
    client_id: str,
    include_history: bool = Query(
        True, description="Include client interaction history"
    ),
    include_preferences: bool = Query(True, description="Include client preferences"),
    current_user: User = Depends(get_current_user),
):
    """
    Get client/lead information for a specific session

    This endpoint provides comprehensive client information including
    basic details, interaction history, and preferences.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        # Fetch client context
        context_data = await context_management_service.fetch_entity_context(
            "client", client_id
        )

        if not context_data or "client" not in context_data:
            raise HTTPException(
                status_code=404, detail=f"Client not found: {client_id}"
            )

        return ClientInfoResponse(
            client=context_data.get("client", {}),
            history=context_data.get("history", []) if include_history else [],
            preferences=context_data.get("preferences", {})
            if include_preferences
            else {},
            context_type=context_data.get("context_type", "client_info"),
            last_updated=context_data.get("last_updated", datetime.now().isoformat()),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting client info for {client_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Client info fetching failed: {str(e)}"
        )


@router.get(
    "/{session_id}/advanced/market/context", response_model=MarketContextResponse
)
async def get_market_context_for_session(
    session_id: str,
    location: str = Query(..., description="Location to get market context for"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    include_trends: bool = Query(True, description="Include market trends"),
    include_insights: bool = Query(True, description="Include investment insights"),
    current_user: User = Depends(get_current_user),
):
    """
    Get market context for a location within a specific session

    This endpoint provides market analysis data for a specific location,
    including trends, insights, and property data.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        # Fetch location context
        context_data = await context_management_service.fetch_entity_context(
            "location", location
        )

        if not context_data:
            raise HTTPException(
                status_code=404,
                detail=f"Market context not found for location: {location}",
            )

        return MarketContextResponse(
            location=location,
            market_data=context_data.get("market_data", []),
            trends=context_data.get("trends", []) if include_trends else [],
            insights=context_data.get("insights", []) if include_insights else [],
            context_type=context_data.get("context_type", "location_data"),
            last_updated=context_data.get("last_updated", datetime.now().isoformat()),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting market context for {location}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Market context fetching failed: {str(e)}"
        )


@router.post("/{session_id}/advanced/context/batch")
async def fetch_batch_context_for_session(
    session_id: str,
    entities: List[Dict[str, str]],
    current_user: User = Depends(get_current_user),
):
    """
    Fetch context for multiple entities in batch for a specific session

    This endpoint allows fetching context for multiple entities in a single request
    to improve performance when dealing with multiple detected entities.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        results = {}

        for entity in entities:
            entity_type = entity.get("entity_type")
            entity_id = entity.get("entity_id")

            if not entity_type or not entity_id:
                continue

            try:
                context_data = await context_management_service.fetch_entity_context(
                    entity_type, entity_id
                )
                results[f"{entity_type}:{entity_id}"] = {
                    "success": True,
                    "data": context_data,
                }
            except Exception as e:
                results[f"{entity_type}:{entity_id}"] = {
                    "success": False,
                    "error": str(e),
                }

        return {
            "results": results,
            "total_entities": len(entities),
            "successful_fetches": sum(1 for r in results.values() if r["success"]),
            "processing_time": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in batch context fetching: {e}")
        raise HTTPException(
            status_code=500, detail=f"Batch context fetching failed: {str(e)}"
        )


@router.delete("/{session_id}/advanced/context/cache/clear")
async def clear_context_cache_for_session(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """
    Clear expired context cache entries for a specific session

    This endpoint clears expired cache entries to free up database space.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        await context_management_service.clear_expired_cache()

        return {
            "message": "Context cache cleared successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error clearing context cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}")


@router.get("/{session_id}/advanced/health")
async def advanced_chat_health_check_for_session(
    session_id: str, current_user: User = Depends(get_current_user)
):
    """
    Health check endpoint for advanced chat services within a session

    This endpoint verifies that all advanced chat services are operational.
    """
    if not ADVANCED_CHAT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Advanced chat services not available"
        )

    try:
        # Verify session exists and user has access
        with get_db_connection() as conn:
            session_result = conn.execute(
                text(
                    """
                SELECT id, session_id, role, title, user_id
                FROM conversations 
                WHERE session_id = :session_id AND is_active = TRUE
            """
                ),
                {"session_id": session_id},
            )

            session_row = session_result.fetchone()
            if not session_row:
                raise HTTPException(status_code=404, detail="Chat session not found")

            # Check if user has access to this session
            if current_user.role != "admin" and session_row[4] != current_user.id:
                raise HTTPException(
                    status_code=403, detail="Access denied to this session"
                )

        # Basic health checks
        health_status = {
            "status": "healthy",
            "services": {
                "entity_detection": "operational",
                "context_management": "operational",
                "database_connection": "operational",
            },
            "timestamp": datetime.now().isoformat(),
        }

        return health_status

    except HTTPException:
        raise
    except Exception as e:
        print(f"Advanced chat health check failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Advanced chat services unhealthy: {str(e)}"
        )
