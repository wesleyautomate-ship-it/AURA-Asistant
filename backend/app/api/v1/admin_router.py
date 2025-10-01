"""
Admin Router - FastAPI Router for Administrative and Data Ingestion Endpoints

This router handles all administrative and data ingestion endpoints migrated from main.py
to maintain frontend compatibility while following the secure architecture
patterns of main_secure.py.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import shutil
import uuid

# Import secure authentication
from auth.middleware import get_current_user, require_admin
from auth.models import User

# Import dependencies
from app.core.settings import UPLOAD_DIR
from rag_service import EnhancedRAGService

# Initialize RAG service lazily
from app.core.settings import DATABASE_URL
rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        try:
            rag_service = EnhancedRAGService()
        except Exception as e:
            print(f"Warning: Could not initialize RAG service: {e}")
            return None
    return rag_service

# Initialize router
router = APIRouter(prefix="/admin", tags=["Administrative"])

# Root level ingestion endpoints
ingest_router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])

# Pydantic Models
class DailyBriefingResponse(BaseModel):
    """Daily briefing response model"""
    message: str

class DocumentIngestionResponse(BaseModel):
    """Document ingestion response model"""
    file_id: str
    filename: str
    document_type: str
    priority: str
    status: str
    chunks_created: int
    file_size: Optional[int] = None
    message: str
    error: Optional[str] = None


from services.human_expertise_service import HumanExpertiseService
from services.ai_request_processing_service import AIRequestProcessingService
from services.voice_processing_service import VoiceProcessingService

@router.get("/experts", response_model=Dict[str, Any])
async def get_all_experts(
    expertise_area: Optional[str] = None,
    availability_status: Optional[str] = None,
    is_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_roles(["admin", "brokerage_owner"])),
    db: Session = Depends(get_db)
):
    """Get all experts (admin/brokerage owner only)"""
    try:
        service = HumanExpertiseService(db)
        
        result = await service.get_all_experts(
            expertise_area=expertise_area,
            availability_status=availability_status,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting all experts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get experts: {str(e)}"
        )

@router.get("/analytics", response_model=Dict[str, Any])
async def get_ai_assistant_analytics(
    current_user: User = Depends(require_roles(["admin", "brokerage_owner"])),
    db: Session = Depends(get_db)
):
    """Get AI assistant analytics (admin/brokerage owner only)"""
    try:
        if not current_user.brokerage_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a brokerage"
            )
        
        ai_service = AIRequestProcessingService(db)
        voice_service = VoiceProcessingService(db)
        expert_service = HumanExpertiseService(db)
        
        # Get AI request analytics
        ai_analytics = await ai_service.get_brokerage_analytics(current_user.brokerage_id)
        
        # Get voice processing analytics
        voice_analytics = await voice_service.get_voice_processing_analytics(
            brokerage_id=current_user.brokerage_id
        )
        
        # Get expertise area statistics
        expert_stats = await expert_service.get_expertise_area_statistics()
        
        return {
            "ai_requests": ai_analytics,
            "voice_processing": voice_analytics,
            "expert_statistics": expert_stats,
            "brokerage_id": current_user.brokerage_id
        }
        
    except Exception as e:
        logger.error(f"Error getting AI assistant analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

# Router Endpoints


@router.get("/files")
async def get_admin_files(current_user: User = Depends(require_admin)):
    """Get list of uploaded files for admin management"""
    try:
        from database_manager import get_db_connection
        from sqlalchemy import text
        
        print("🔍 Fetching admin files from database...")
        with get_db_connection() as conn:
            sql = """
                SELECT id, original_filename as name, file_size as size, file_type as type,
                       category, description, tags, status, upload_date, processed_date,
                       chunks, vectorized
                FROM files 
                ORDER BY upload_date DESC
            """
            print(f"📝 Executing SQL: {sql}")
            result = conn.execute(text(sql))
            files = []
            for row in result:
                files.append({
                    "id": row.id,
                    "name": row.name,
                    "size": row.size,
                    "type": row.type,
                    "category": row.category,
                    "description": row.description,
                    "tags": row.tags or [],
                    "status": row.status,
                    "uploadDate": row.upload_date.isoformat() if row.upload_date else None,
                    "processedDate": row.processed_date.isoformat() if row.processed_date else None,
                    "chunks": row.chunks,
                    "vectorized": row.vectorized
                })
            
            print(f"📊 Found {len(files)} files in database")
        
        return {"files": files, "total_count": len(files)}
    except Exception as e:
        print(f"❌ Error in get_admin_files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_id}")
async def delete_file(file_id: int, current_user: User = Depends(require_admin)):
    """Delete a file from the system"""
    try:
        from database_manager import get_db_connection
        from sqlalchemy import text
        
        with get_db_connection() as conn:
            # Get file info first
            get_sql = "SELECT filename, file_path FROM files WHERE id = :file_id"
            result = conn.execute(text(get_sql), {'file_id': file_id})
            file_info = result.fetchone()
            
            if not file_info:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Delete from database
            delete_sql = "DELETE FROM files WHERE id = :file_id"
            conn.execute(text(delete_sql), {'file_id': file_id})
            
            # Delete physical file
            try:
                file_path = Path(file_info.file_path)
                if file_path.exists():
                    file_path.unlink()
            except Exception as file_error:
                print(f"Error deleting physical file: {file_error}")
        
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-daily-briefing", response_model=DailyBriefingResponse)
async def trigger_daily_briefing(current_user: User = Depends(require_admin)):
    """Manually trigger daily briefing generation for testing"""
    try:
        from scheduler import DailyBriefingScheduler
        import asyncio
        
        scheduler = DailyBriefingScheduler()
        await scheduler.send_daily_briefings()
        
        return DailyBriefingResponse(message="Daily briefing generation completed successfully")
    except Exception as e:
        print(f"Error triggering daily briefing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ingest_router.post("/upload", response_model=DocumentIngestionResponse, tags=["Document Ingestion"])
async def upload_document_for_ingestion(
    file: UploadFile = File(...),
    document_type: str = Form("general"),
    priority: str = Form("normal"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document for ingestion into the RAG system
    """
    try:
        # Validate file type
        if not file.filename or not any(file.filename.lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt']):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT files are allowed.")
        
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        
        # Save file
        file_path = Path(UPLOAD_DIR) / safe_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document for ingestion
        try:
            # Extract text from document
            extracted_text = ""
            if file_extension.lower() == '.pdf':
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() + "\n"
            elif file_extension.lower() == '.docx':
                from docx import Document
                doc = Document(file_path)
                for paragraph in doc.paragraphs:
                    extracted_text += paragraph.text + "\n"
            elif file_extension.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    extracted_text = txt_file.read()
            
            # Store in ChromaDB for RAG
            chunks = []
            rag_service = get_rag_service()
            if rag_service and extracted_text:
                # Split text into chunks
                chunks = [extracted_text[i:i+1000] for i in range(0, len(extracted_text), 1000)]
                
                # Add to ChromaDB
                for i, chunk in enumerate(chunks):
                    rag_service.add_document(
                        document_id=f"{file_id}_chunk_{i}",
                        content=chunk,
                        metadata={
                            "filename": file.filename,
                            "document_type": document_type,
                            "priority": priority,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    )
            
            return DocumentIngestionResponse(
                file_id=file_id,
                filename=file.filename,
                document_type=document_type,
                priority=priority,
                status="uploaded_and_processed",
                chunks_created=len(chunks) if extracted_text else 0,
                file_size=file.size,
                message="Document uploaded and processed successfully"
            )
            
        except Exception as processing_error:
            # If processing fails, still return upload success but with error message
            return DocumentIngestionResponse(
                file_id=file_id,
                filename=file.filename,
                document_type=document_type,
                priority=priority,
                status="uploaded_processing_failed",
                chunks_created=0,
                file_size=file.size,
                message="Document uploaded but processing failed",
                error=str(processing_error)
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
