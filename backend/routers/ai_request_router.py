"""
AI Request Router
================

FastAPI router for the new AI request system including:
- Request creation and management
- Real-time progress tracking via SSE
- Template management
- Brand asset management
- Deliverable handling
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid

from auth.database import get_db
from auth.middleware import get_current_user, require_roles
from auth.models import User
from app.domain.listings.ai_request_models import AIRequestNew, AIRequestStep, Deliverable, Template, AIBrandAsset, AIRequestEvent
from services.ai_processing_service import AIProcessingService
from services.file_storage_service import file_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/requests", tags=["AI Requests"])

# =====================================================
# PYDANTIC MODELS
# =====================================================

class AIRequestCreate(BaseModel):
    team: str = Field(..., description="AI team (marketing, analytics, social, strategy, packages, transactions)")
    content: str = Field(..., description="Request content (text or transcript)")
    template_id: Optional[str] = Field(None, description="Template ID to use")
    brand_context: Optional[Dict[str, Any]] = Field(None, description="Brand context for personalization")
    priority: int = Field(5, ge=1, le=10, description="Priority level (1-10)")

class AIRequestResponse(BaseModel):
    id: str
    team: str
    title: str
    description: str
    status: str
    eta: Optional[datetime]
    priority: int
    created_at: datetime
    updated_at: datetime
    steps: List[Dict[str, Any]] = []
    deliverables: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True

class AIRequestUpdate(BaseModel):
    status: Optional[str] = None
    eta: Optional[datetime] = None
    priority: Optional[int] = None

class RevisionRequest(BaseModel):
    instructions: str = Field(..., description="Instructions for revision")

class TemplateResponse(BaseModel):
    id: str
    team: str
    name: str
    description: Optional[str]
    output_format: str
    estimated_duration: int

    class Config:
        from_attributes = True

class BrandAssetResponse(BaseModel):
    id: str
    type: str
    name: str
    description: Optional[str]
    url: str
    config: Dict[str, Any]

    class Config:
        from_attributes = True

# =====================================================
# AI REQUEST ENDPOINTS
# =====================================================

@router.post("/", response_model=AIRequestResponse)
async def create_ai_request(
    request_data: AIRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI request"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage"
            )
        
        # Generate title from content (first 100 chars)
        title = request_data.content[:100] + "..." if len(request_data.content) > 100 else request_data.content
        
        # Create the request
        ai_request = AIRequestNew(
            user_id=current_user.id,
            brokerage_id=current_user.brokerage_id,
            team=request_data.team,
            title=title,
            description=request_data.content,
            content=request_data.content,
            template_id=request_data.template_id,
            brand_context=request_data.brand_context or {},
            priority=request_data.priority,
            status='queued',
            eta=datetime.now() + timedelta(hours=2)  # Default 2-hour ETA
        )
        
        db.add(ai_request)
        db.flush()  # Get the ID
        
        # Create initial steps
        steps = [
            {'step': 'queued', 'status': 'completed', 'progress': 100},
            {'step': 'planning', 'status': 'pending', 'progress': 0},
            {'step': 'generating', 'status': 'pending', 'progress': 0},
            {'step': 'validating', 'status': 'pending', 'progress': 0},
            {'step': 'draft_ready', 'status': 'pending', 'progress': 0}
        ]
        
        for step_data in steps:
            step = AIRequestStep(
                request_id=ai_request.id,
                step=step_data['step'],
                status=step_data['status'],
                progress=step_data['progress']
            )
            db.add(step)
        
        db.commit()
        
        # Start the AI pipeline asynchronously
        asyncio.create_task(start_ai_processing(ai_request.id, db))
        
        return AIRequestResponse(
            id=str(ai_request.id),
            team=ai_request.team,
            title=ai_request.title,
            description=ai_request.description,
            status=ai_request.status,
            eta=ai_request.eta,
            priority=ai_request.priority,
            created_at=ai_request.created_at,
            updated_at=ai_request.updated_at,
            steps=[],
            deliverables=[]
        )
        
    except Exception as e:
        logger.error(f"Error creating AI request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI request: {str(e)}"
        )

@router.post("/audio")
async def create_audio_request(
    audio: UploadFile = File(...),
    team: str = Form(...),
    template_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an AI request from audio file"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage"
            )
        
        # Save audio file
        file_info = await file_storage.save_audio_file(audio, str(uuid.uuid4()))
        
        # TODO: Implement audio transcription
        # For now, use a placeholder transcript
        transcript = "Audio transcription would go here. This is a placeholder for the actual transcript."
        
        # Create the request
        ai_request = AIRequestNew(
            user_id=current_user.id,
            brokerage_id=current_user.brokerage_id,
            team=team,
            title=transcript[:100] + "..." if len(transcript) > 100 else transcript,
            description=transcript,
            content=transcript,
            content_type='audio',
            audio_url=file_info['url'],
            template_id=template_id,
            status='queued',
            eta=datetime.now() + timedelta(hours=2)
        )
        
        db.add(ai_request)
        db.flush()
        
        # Create initial steps
        steps = [
            {'step': 'queued', 'status': 'completed', 'progress': 100},
            {'step': 'planning', 'status': 'pending', 'progress': 0},
            {'step': 'generating', 'status': 'pending', 'progress': 0},
            {'step': 'validating', 'status': 'pending', 'progress': 0},
            {'step': 'draft_ready', 'status': 'pending', 'progress': 0}
        ]
        
        for step_data in steps:
            step = AIRequestStep(
                request_id=ai_request.id,
                step=step_data['step'],
                status=step_data['status'],
                progress=step_data['progress']
            )
            db.add(step)
        
        db.commit()
        
        # Start the AI pipeline asynchronously
        asyncio.create_task(start_ai_processing(ai_request.id, db))
        
        return {"id": str(ai_request.id), "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating audio request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audio request: {str(e)}"
        )

@router.get("/", response_model=List[AIRequestResponse])
async def get_requests(
    status: Optional[str] = None,
    team: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI requests for the current user"""
    try:
        query = db.query(AIRequestNew).filter(AIRequestNew.user_id == current_user.id)
        
        if status:
            query = query.filter(AIRequestNew.status == status)
        if team:
            query = query.filter(AIRequestNew.team == team)
        
        requests = query.order_by(AIRequestNew.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            AIRequestResponse(
                id=str(req.id),
                team=req.team,
                title=req.title,
                description=req.description,
                status=req.status,
                eta=req.eta,
                priority=req.priority,
                created_at=req.created_at,
                updated_at=req.updated_at,
                steps=[],
                deliverables=[]
            )
            for req in requests
        ]
        
    except Exception as e:
        logger.error(f"Error getting requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get requests"
        )

@router.get("/{request_id}", response_model=AIRequestResponse)
async def get_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific AI request"""
    try:
        request_uuid = uuid.UUID(request_id)
        ai_request = db.query(AIRequestNew).filter(
            AIRequestNew.id == request_uuid,
            AIRequestNew.user_id == current_user.id
        ).first()
        
        if not ai_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        # Get steps
        steps = db.query(AIRequestStep).filter(
            AIRequestStep.request_id == request_uuid
        ).order_by(AIRequestStep.created_at).all()
        
        # Get deliverables
        deliverables = db.query(Deliverable).filter(
            Deliverable.request_id == request_uuid
        ).all()
        
        return AIRequestResponse(
            id=str(ai_request.id),
            team=ai_request.team,
            title=ai_request.title,
            description=ai_request.description,
            status=ai_request.status,
            eta=ai_request.eta,
            priority=ai_request.priority,
            created_at=ai_request.created_at,
            updated_at=ai_request.updated_at,
            steps=[{
                "step": step.step,
                "status": step.status,
                "progress": step.progress,
                "started_at": step.started_at,
                "finished_at": step.finished_at
            } for step in steps],
            deliverables=[{
                "id": str(deliverable.id),
                "type": deliverable.type,
                "name": deliverable.name,
                "url": deliverable.url,
                "preview_url": deliverable.preview_url,
                "status": deliverable.status
            } for deliverable in deliverables]
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID format"
        )
    except Exception as e:
        logger.error(f"Error getting request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get request"
        )

@router.get("/{request_id}/stream")
async def stream_request_updates(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream real-time updates for a request via Server-Sent Events"""
    try:
        request_uuid = uuid.UUID(request_id)
        
        # Verify user owns the request
        ai_request = db.query(AIRequestNew).filter(
            AIRequestNew.id == request_uuid,
            AIRequestNew.user_id == current_user.id
        ).first()
        
        if not ai_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        async def event_generator():
            # Send initial state
            yield f"data: {json.dumps({'type': 'initial', 'data': {'status': ai_request.status, 'eta': ai_request.eta.isoformat() if ai_request.eta else None}})}\n\n"
            
            # TODO: Implement actual event streaming
            # This would connect to Redis pub/sub or similar
            # For now, just send periodic updates
            while True:
                await asyncio.sleep(5)
                yield f"data: {json.dumps({'type': 'heartbeat', 'data': {'timestamp': datetime.now().isoformat()}})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID format"
        )
    except Exception as e:
        logger.error(f"Error streaming request updates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream updates"
        )

@router.post("/{request_id}/approve")
async def approve_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a request and mark as delivered"""
    try:
        request_uuid = uuid.UUID(request_id)
        ai_request = db.query(AIRequestNew).filter(
            AIRequestNew.id == request_uuid,
            AIRequestNew.user_id == current_user.id
        ).first()
        
        if not ai_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        if ai_request.status != 'draft_ready':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request must be in draft_ready status to approve"
            )
        
        ai_request.status = 'approved'
        ai_request.completed_at = datetime.now()
        ai_request.updated_at = datetime.now()
        
        db.commit()
        
        return {"status": "approved", "completed_at": ai_request.completed_at}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID format"
        )
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve request"
        )

@router.post("/{request_id}/revise")
async def request_revision(
    request_id: str,
    revision_data: RevisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a revision for a request"""
    try:
        request_uuid = uuid.UUID(request_id)
        ai_request = db.query(AIRequestNew).filter(
            AIRequestNew.id == request_uuid,
            AIRequestNew.user_id == current_user.id
        ).first()
        
        if not ai_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        if ai_request.status not in ['draft_ready', 'needs_info']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request must be in draft_ready or needs_info status to request revision"
            )
        
        ai_request.status = 'needs_info'
        ai_request.description += f"\n\nRevision Request: {revision_data.instructions}"
        ai_request.updated_at = datetime.now()
        
        db.commit()
        
        # TODO: Restart the AI pipeline with revision instructions
        
        return {"status": "revision_requested"}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID format"
        )
    except Exception as e:
        logger.error(f"Error requesting revision: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request revision"
        )

# =====================================================
# TEMPLATE ENDPOINTS
# =====================================================

@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    team: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available templates"""
    try:
        query = db.query(Template).filter(Template.is_active == True)
        
        if team:
            query = query.filter(Template.team == team)
        
        templates = query.order_by(Template.name).all()
        
        return [
            TemplateResponse(
                id=template.id,
                team=template.team,
                name=template.name,
                description=template.description,
                output_format=template.output_format,
                estimated_duration=template.estimated_duration
            )
            for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get templates"
        )

# =====================================================
# BRAND ASSET ENDPOINTS
# =====================================================

@router.get("/brand-kit", response_model=List[BrandAssetResponse])
async def get_brand_assets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get brand assets for the user's brokerage"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage"
            )
        
        assets = db.query(AIBrandAsset).filter(
            AIBrandAsset.brokerage_id == current_user.brokerage_id,
            AIBrandAsset.is_active == True
        ).order_by(AIBrandAsset.type, AIBrandAsset.name).all()
        
        return [
            BrandAssetResponse(
                id=str(asset.id),
                type=asset.type,
                name=asset.name,
                description=asset.description,
                url=asset.url,
                config=asset.config
            )
            for asset in assets
        ]
        
    except Exception as e:
        logger.error(f"Error getting brand assets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get brand assets"
        )

# =====================================================
# FILE SERVING ENDPOINTS
# =====================================================

@router.get("/files/{file_type}/{request_id}/{filename}")
async def serve_file(
    file_type: str,
    request_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Serve files (deliverables, audio, previews)"""
    try:
        # Verify user has access to this request
        request_uuid = uuid.UUID(request_id)
        ai_request = db.query(AIRequestNew).filter(
            AIRequestNew.id == request_uuid,
            AIRequestNew.user_id == current_user.id
        ).first()
        
        if not ai_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found or access denied"
            )
        
        # Construct file path
        if file_type == "deliverables":
            file_path = file_storage.deliverables_path / request_id / filename
        elif file_type == "audio":
            file_path = file_storage.audio_path / request_id / filename
        elif file_type == "previews":
            file_path = file_storage.previews_path / request_id / filename
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type"
            )
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID format"
        )
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve file"
        )

@router.get("/brand-assets/{brokerage_id}/{filename}")
async def serve_brand_asset(
    brokerage_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Serve brand assets"""
    try:
        # Verify user has access to this brokerage
        if current_user.brokerage_id != int(brokerage_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brokerage's assets"
            )
        
        file_path = file_storage.brand_assets_path / brokerage_id / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand asset not found"
            )
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error serving brand asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve brand asset"
        )

# =====================================================
# AI PIPELINE PROCESSING
# =====================================================

async def start_ai_processing(request_id: uuid.UUID, db: Session):
    """Process an AI request through the pipeline"""
    try:
        # Use the AI processing service
        processing_service = AIProcessingService(db)
        success = await processing_service.process_request(str(request_id))
        
        if not success:
            logger.error(f"AI processing failed for request {request_id}")
        
    except Exception as e:
        logger.error(f"Error processing AI request {request_id}: {e}")
        # Update request status to failed
        try:
            ai_request = db.query(AIRequestNew).filter(AIRequestNew.id == request_id).first()
            if ai_request:
                ai_request.status = 'failed'
                ai_request.updated_at = datetime.now()
                db.commit()
        except Exception as update_error:
            logger.error(f"Failed to update request status: {update_error}")
