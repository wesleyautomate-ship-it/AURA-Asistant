"""
Voice Processing Service
=======================

This service handles voice-to-text processing and audio file management:
- Audio file upload and storage
- Voice-to-text transcription
- Request understanding and processing
- Audio file cleanup and management
"""

import logging
import os
import uuid
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status, UploadFile
import json
import wave
import io
from pathlib import Path

from app.domain.listings.ai_assistant_models import VoiceRequest, AIRequest
from auth.models import User
from app.domain.listings.brokerage_models import Brokerage

logger = logging.getLogger(__name__)


"""
Voice Processing Service
=======================

This service handles voice-to-text processing and audio file management:
- Audio file upload and storage
- Voice-to-text transcription
"""

import logging
import os
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from pathlib import Path
import wave

logger = logging.getLogger(__name__)

class VoiceProcessingService:
    """Service for voice processing and audio file management"""
    
    def __init__(self, db: Session, upload_dir: str = "uploads/voice"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.supported_formats = {
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/mp4': '.m4a',
            'audio/ogg': '.ogg',
            'audio/webm': '.webm'
        }
        
        self.max_file_size = 10 * 1024 * 1024
    
    async def save_audio_file(self, audio_file: UploadFile) -> str:
        """Saves the uploaded audio file and returns the path."""
        if audio_file.content_type not in self.supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported audio format: {audio_file.content_type}"
            )
        
        content = await audio_file.read()
        file_size = len(content)
        
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
            )
        
        file_extension = self.supported_formats[audio_file.content_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        return str(file_path)

from google.cloud import speech

    async def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file to text"""
        try:
            client = speech.SpeechClient()

            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )

            response = client.recognize(config=config, audio=audio)

            if not response.results:
                return {"success": False, "error": "No speech found"}

            result = response.results[0]
            transcript = result.alternatives[0].transcript
            confidence = result.alternatives[0].confidence

            return {
                "success": True,
                "text": transcript,
                "confidence": confidence,
                "language": "en-US"
            }

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                "success": False,
                "error": str(e)
            }
