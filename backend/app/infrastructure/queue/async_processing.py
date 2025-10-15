#!/usr/bin/env python3
"""
Async Processing Endpoints for Advanced AI Data Router
Handles asynchronous file processing with detailed reporting
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
import asyncio
import logging
from pathlib import Path
import shutil
from datetime import datetime

from task_manager import task_manager, TaskStatus
from intelligent_processor import IntelligentDataProcessor

logger = logging.getLogger(__name__)

# Initialize the intelligent processor
intelligent_processor = IntelligentDataProcessor()

router = APIRouter(prefix="/async", tags=["Async Processing"])


@router.post("/analyze-file", response_model=Dict[str, Any])
async def analyze_file_async(
    file: UploadFile = File(...), instructions: str = Form("")
):
    """
    Uploads a file and initiates asynchronous processing using the
    Advanced AI Data Router with two-step AI pipeline.
    """
    # Save file temporarily
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get the file type (e.g., 'pdf', 'csv')
        file_type = file.filename.split(".")[-1].lower()

        # Create a new processing task
        task_id = task_manager.create_task(
            file_path=str(file_path), file_type=file_type, instructions=instructions
        )

        # Start the async processing
        asyncio.create_task(
            process_file_async(task_id, str(file_path), file_type, instructions)
        )

        return {
            "task_id": task_id,
            "status": "processing",
            "message": "File processing started. Use the task_id to check status.",
            "filename": file.filename,
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


async def process_file_async(
    task_id: str, file_path: str, file_type: str, instructions: str
):
    """
    Background task for processing files asynchronously.
    """
    try:
        # Process the file using the enhanced intelligent processor
        result = intelligent_processor.process_uploaded_document_async(
            file_path=file_path,
            file_type=file_type,
            instructions=instructions,
            task_id=task_id,
        )

        # Clean up the temporary file
        temp_file = Path(file_path)
        if temp_file.exists():
            temp_file.unlink()

    except Exception as e:
        logger.error(f"Error in async file processing: {e}")
        task_manager.set_task_error(task_id, str(e))

        # Clean up the temporary file even on error
        temp_file = Path(file_path)
        if temp_file.exists():
            temp_file.unlink()


@router.get("/processing-status/{task_id}", response_model=Dict[str, Any])
async def get_processing_status(task_id: str):
    """
    Get the status and results of an asynchronous processing task.
    """
    task_summary = task_manager.get_task_summary(task_id)

    if not task_summary:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_summary
