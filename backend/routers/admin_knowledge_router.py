"""
Admin Knowledge Base Router for Dubai Real Estate RAG System

This router handles admin uploads to the knowledge base with intelligent data sorting,
schema conversion, and structured storage for future retrieval.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from typing import Dict, Any, Optional, List
import logging
from pydantic import BaseModel
import uuid
from datetime import datetime
from pathlib import Path
import shutil

from services.intelligent_data_sorter import IntelligentDataSorter
from auth import get_current_user, require_admin
from auth.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/knowledge", tags=["admin-knowledge-base"])

# Initialize intelligent data sorter
data_sorter = IntelligentDataSorter()

# Request/Response Models
class KnowledgeUploadRequest(BaseModel):
    document_category: Optional[str] = None
    priority: str = "normal"
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class KnowledgeUploadResponse(BaseModel):
    upload_id: str
    filename: str
    document_type: str
    confidence: float
    structured_data: Dict[str, Any]
    storage_result: Dict[str, Any]
    rag_result: Dict[str, Any]
    processing_timestamp: str
    status: str

class KnowledgeSearchRequest(BaseModel):
    query: str
    document_type: Optional[str] = None
    limit: int = 50

class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    search_timestamp: str

class KnowledgeStatsResponse(BaseModel):
    total_documents: int
    documents_by_type: Dict[str, int]
    recent_uploads: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]

@router.post("/upload", response_model=KnowledgeUploadResponse)
async def upload_to_knowledge_base(
    file: UploadFile = File(...),
    document_category: Optional[str] = Form(None),
    priority: str = Form("normal"),
    description: Optional[str] = Form(""),
    tags: Optional[str] = Form(""),
    current_user: User = Depends(require_admin)
):
    """
    Upload document to knowledge base with intelligent data sorting and schema conversion
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.csv', '.xlsx']
        if not file.filename or not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (50MB limit for knowledge base)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
        
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        # Save file temporarily
        temp_dir = Path("temp_knowledge_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        file_extension = Path(file.filename).suffix
        temp_filename = f"{upload_id}{file_extension}"
        temp_file_path = temp_dir / temp_filename
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file type
        file_type = file_extension[1:].lower()  # Remove the dot
        
        # Process document with intelligent data sorter
        processing_result = data_sorter.process_document_for_knowledge_base(
            file_path=str(temp_file_path),
            file_type=file_type,
            document_category=document_category
        )
        
        # Clean up temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()
        
        if processing_result["status"] != "success":
            raise HTTPException(
                status_code=500, 
                detail=f"Document processing failed: {processing_result.get('message', 'Unknown error')}"
            )
        
        # Log the upload
        logger.info(f"Knowledge base upload successful: {file.filename} by user {current_user.id}")
        
        return KnowledgeUploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            document_type=processing_result["document_type"],
            confidence=processing_result["confidence"],
            structured_data=processing_result["structured_data"],
            storage_result=processing_result["storage_result"],
            rag_result=processing_result["rag_result"],
            processing_timestamp=processing_result["processing_timestamp"],
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in knowledge base upload: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_base(
    query: str = Query(..., description="Search query"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    limit: int = Query(50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user)
):
    """
    Search the knowledge base for structured data
    """
    try:
        # Search structured data
        results = data_sorter.search_structured_data(query, document_type)
        
        # Limit results
        if len(results) > limit:
            results = results[:limit]
        
        return KnowledgeSearchResponse(
            results=results,
            total_found=len(results),
            search_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats", response_model=KnowledgeStatsResponse)
async def get_knowledge_base_stats(
    current_user: User = Depends(require_admin)
):
    """
    Get knowledge base statistics and processing metrics
    """
    try:
        stats = {
            "total_documents": 0,
            "documents_by_type": {},
            "recent_uploads": [],
            "processing_stats": {
                "successful_uploads": 0,
                "failed_uploads": 0,
                "average_processing_time": 0
            }
        }
        
        # Get document counts by type
        for doc_type, schema_info in data_sorter.document_schemas.items():
            table_name = schema_info['table_name']
            try:
                with data_sorter.engine.connect() as conn:
                    result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = result.scalar()
                    stats["documents_by_type"][doc_type] = count
                    stats["total_documents"] += count
            except Exception as e:
                logger.warning(f"Could not get count for {table_name}: {e}")
                stats["documents_by_type"][doc_type] = 0
        
        # Get recent uploads (last 10)
        recent_uploads = []
        for doc_type in data_sorter.document_schemas.keys():
            recent_data = data_sorter.get_structured_data_by_type(doc_type, limit=5)
            for item in recent_data:
                recent_uploads.append({
                    "document_type": doc_type,
                    "created_at": item.get("created_at"),
                    "id": item.get("id")
                })
        
        # Sort by creation date
        recent_uploads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        stats["recent_uploads"] = recent_uploads[:10]
        
        return KnowledgeStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/data/{document_type}")
async def get_structured_data_by_type(
    document_type: str,
    limit: int = Query(100, description="Maximum number of results"),
    current_user: User = Depends(get_current_user)
):
    """
    Get structured data by document type
    """
    try:
        if document_type not in data_sorter.document_schemas:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document type. Available types: {list(data_sorter.document_schemas.keys())}"
            )
        
        data = data_sorter.get_structured_data_by_type(document_type, limit)
        
        return {
            "document_type": document_type,
            "data": data,
            "total_found": len(data),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting structured data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get data: {str(e)}")

@router.post("/reprocess/{upload_id}")
async def reprocess_document(
    upload_id: str,
    document_category: Optional[str] = Form(None),
    current_user: User = Depends(require_admin)
):
    """
    Reprocess a previously uploaded document with different parameters
    """
    try:
        # This would require storing the original file and reprocessing
        # For now, return a placeholder response
        return {
            "upload_id": upload_id,
            "status": "reprocessing",
            "message": "Document reprocessing feature coming soon",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}")
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")

@router.delete("/data/{document_type}/{record_id}")
async def delete_structured_data(
    document_type: str,
    record_id: int,
    current_user: User = Depends(require_admin)
):
    """
    Delete a specific record from structured data
    """
    try:
        if document_type not in data_sorter.document_schemas:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document type: {document_type}"
            )
        
        table_name = data_sorter.document_schemas[document_type]['table_name']
        
        with data_sorter.engine.connect() as conn:
            result = conn.execute(f"DELETE FROM {table_name} WHERE id = :record_id", 
                                {"record_id": record_id})
            conn.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Record not found")
        
        return {
            "status": "success",
            "message": f"Record {record_id} deleted from {document_type}",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting structured data: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/schemas")
async def get_document_schemas(
    current_user: User = Depends(get_current_user)
):
    """
    Get available document schemas and their structures
    """
    try:
        schemas = {}
        for doc_type, schema_info in data_sorter.document_schemas.items():
            schemas[doc_type] = {
                "table_name": schema_info['table_name'],
                "fields": list(schema_info['schema'].keys()),
                "field_types": schema_info['schema']
            }
        
        return {
            "schemas": schemas,
            "total_schemas": len(schemas),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting document schemas: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get schemas: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for knowledge base service
    """
    return {
        "status": "healthy",
        "service": "admin-knowledge-base",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
