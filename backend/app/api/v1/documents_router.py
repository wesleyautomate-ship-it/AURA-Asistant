#!/usr/bin/env python3
"""
Documents Router for Blueprint 2.0: Proactive AI Copilot
Handles web-based content delivery with HTML viewing endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
import logging
from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv

# Import secure authentication
from auth.middleware import get_current_user
from auth.models import User

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize database connection
db_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
)
engine = create_engine(db_url)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/view/{document_id}", response_class=HTMLResponse)
async def view_document(
    document_id: int, current_user: User = Depends(get_current_user)
):
    """
    Serve HTML content for a generated document
    """
    try:
        # Fetch the document record
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT id, document_type, title, content_html, preview_summary, 
                       agent_id, metadata, created_at
                FROM generated_documents 
                WHERE id = :document_id
            """
                ),
                {"document_id": document_id},
            )

            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Document not found")

            # Check permissions - user can only access their own documents
            if row.agent_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied - you can only view your own documents",
                )

            # Return the HTML content
            return HTMLResponse(content=row.content_html)

    except Exception as e:
        logger.error(f"Error viewing document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving document")


@router.get("/{document_id}/preview")
async def get_document_preview(
    document_id: int, current_user: User = Depends(get_current_user)
):
    """
    Get preview data for a document (for chat interface)
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT id, document_type, title, preview_summary, result_url, 
                       agent_id, metadata, created_at
                FROM generated_documents 
                WHERE id = :document_id
            """
                ),
                {"document_id": document_id},
            )

            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Document not found")

            return {
                "document_id": row.id,
                "document_type": row.document_type,
                "title": row.title,
                "preview_summary": row.preview_summary,
                "result_url": row.result_url,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "metadata": json.loads(row.metadata) if row.metadata else {},
            }

    except Exception as e:
        logger.error(f"Error getting document preview {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving document preview")


@router.get("/")
async def list_documents(
    current_user: User = Depends(get_current_user), limit: int = 20, offset: int = 0
):
    """
    List documents for the current user
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT id, document_type, title, preview_summary, result_url, 
                       agent_id, created_at
                FROM generated_documents 
                WHERE agent_id = :agent_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """
                ),
                {"agent_id": current_user.id, "limit": limit, "offset": offset},
            )

            documents = []
            for row in result.fetchall():
                documents.append(
                    {
                        "document_id": row.id,
                        "document_type": row.document_type,
                        "title": row.title,
                        "preview_summary": row.preview_summary,
                        "result_url": row.result_url,
                        "created_at": row.created_at.isoformat()
                        if row.created_at
                        else None,
                    }
                )

            return {
                "documents": documents,
                "total": len(documents),
                "limit": limit,
                "offset": offset,
            }

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving documents")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int, current_user: User = Depends(get_current_user)
):
    """
    Delete a document (soft delete by updating status)
    """
    try:
        with engine.connect() as conn:
            # Check if document exists and user has permission
            result = conn.execute(
                text(
                    """
                SELECT id, agent_id FROM generated_documents 
                WHERE id = :document_id
            """
                ),
                {"document_id": document_id},
            )

            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Document not found")

            if row.agent_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied - you can only delete your own documents",
                )

            # Soft delete by updating metadata
            conn.execute(
                text(
                    """
                UPDATE generated_documents 
                SET metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb), 
                    '{deleted}', 'true'
                ),
                updated_at = NOW()
                WHERE id = :document_id
            """
                ),
                {"document_id": document_id},
            )

            conn.commit()

            return {"message": "Document deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting document")


@router.get("/stats/summary")
async def get_document_stats(current_user: User = Depends(get_current_user)):
    """
    Get document statistics for the current user
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT 
                    document_type,
                    COUNT(*) as count,
                    MAX(created_at) as latest_created
                FROM generated_documents 
                WHERE agent_id = :agent_id
                GROUP BY document_type
                ORDER BY count DESC
            """
                ),
                {"agent_id": current_user.id},
            )

            stats = []
            total_documents = 0

            for row in result.fetchall():
                stats.append(
                    {
                        "document_type": row.document_type,
                        "count": row.count,
                        "latest_created": row.latest_created.isoformat()
                        if row.latest_created
                        else None,
                    }
                )
                total_documents += row.count

            return {"total_documents": total_documents, "by_type": stats}

    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(
            status_code=500, detail="Error retrieving document statistics"
        )
