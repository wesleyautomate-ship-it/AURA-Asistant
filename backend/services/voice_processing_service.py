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

class VoiceProcessingService:
    """Service for voice processing and audio file management"""
    
    def __init__(self, db: Session, upload_dir: str = "uploads/voice"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported audio formats
        self.supported_formats = {
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/mp4': '.m4a',
            'audio/ogg': '.ogg',
            'audio/webm': '.webm'
        }
        
        # Maximum file size (10MB)
        self.max_file_size = 10 * 1024 * 1024
    
    # =====================================================
    # AUDIO FILE UPLOAD AND STORAGE
    # =====================================================
    
    async def upload_audio_file(
        self,
        agent_id: int,
        brokerage_id: int,
        audio_file: UploadFile
    ) -> Dict[str, Any]:
        """Upload and process audio file"""
        try:
            # Validate file type
            if audio_file.content_type not in self.supported_formats:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported audio format: {audio_file.content_type}"
                )
            
            # Validate file size
            file_size = 0
            content = await audio_file.read()
            file_size = len(content)
            
            if file_size > self.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
                )
            
            # Generate unique filename
            file_extension = self.supported_formats[audio_file.content_type]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Get audio duration
            audio_duration = await self._get_audio_duration(file_path)
            
            # Create voice request record
            voice_request = VoiceRequest(
                agent_id=agent_id,
                brokerage_id=brokerage_id,
                audio_file_path=str(file_path),
                audio_duration=audio_duration,
                audio_format=file_extension[1:],  # Remove the dot
                file_size=file_size,
                processing_status="pending"
            )
            
            self.db.add(voice_request)
            self.db.commit()
            self.db.refresh(voice_request)
            
            # Start processing
            await self._process_voice_request(voice_request.id)
            
            logger.info(f"Uploaded audio file for voice request {voice_request.id}")
            
            return {
                "voice_request_id": voice_request.id,
                "file_path": str(file_path),
                "file_size": file_size,
                "audio_duration": audio_duration,
                "processing_status": voice_request.processing_status,
                "message": "Audio file uploaded and processing started"
            }
            
        except Exception as e:
            logger.error(f"Error uploading audio file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload audio file: {str(e)}"
            )
    
    async def _get_audio_duration(self, file_path: Path) -> Optional[int]:
        """Get audio duration in seconds"""
        try:
            if file_path.suffix.lower() == '.wav':
                with wave.open(str(file_path), 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration = frames / sample_rate
                    return int(duration)
            else:
                # For other formats, we'd need additional libraries like librosa or pydub
                # For now, return None and let the transcription service handle it
                return None
                
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return None
    
    # =====================================================
    # VOICE-TO-TEXT PROCESSING
    # =====================================================
    
    async def _process_voice_request(self, voice_request_id: int) -> None:
        """Process voice request (transcription and request creation)"""
        try:
            voice_request = self.db.query(VoiceRequest).filter(
                VoiceRequest.id == voice_request_id
            ).first()
            
            if not voice_request:
                logger.error(f"Voice request {voice_request_id} not found")
                return
            
            # Update status to transcribing
            voice_request.processing_status = "transcribing"
            self.db.commit()
            
            # Perform transcription
            transcription_result = await self._transcribe_audio(voice_request.audio_file_path)
            
            if transcription_result["success"]:
                voice_request.transcription = transcription_result["text"]
                voice_request.transcription_confidence = transcription_result["confidence"]
                voice_request.language_detected = transcription_result.get("language", "en")
                
                # Process the transcription into a structured request
                processed_request = await self._process_transcription(transcription_result["text"])
                voice_request.processed_request = processed_request
                voice_request.processing_status = "processed"
                
                # Create AI request from processed voice request
                await self._create_ai_request_from_voice(voice_request)
                
            else:
                voice_request.processing_status = "failed"
                voice_request.error_message = transcription_result.get("error", "Transcription failed")
            
            self.db.commit()
            
            logger.info(f"Voice request {voice_request_id} processed with status: {voice_request.processing_status}")
            
        except Exception as e:
            logger.error(f"Error processing voice request {voice_request_id}: {e}")
            voice_request = self.db.query(VoiceRequest).filter(VoiceRequest.id == voice_request_id).first()
            if voice_request:
                voice_request.processing_status = "failed"
                voice_request.error_message = str(e)
                self.db.commit()
    
    async def _transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file to text"""
        try:
            # In a real implementation, this would integrate with a speech-to-text service
            # like Google Speech-to-Text, Azure Speech Services, or AWS Transcribe
            
            # For now, we'll simulate the transcription
            # In production, you would:
            # 1. Load the audio file
            # 2. Send it to the speech-to-text service
            # 3. Get the transcription result
            
            # Simulated transcription based on file path
            simulated_transcriptions = [
                "Create a comparative market analysis for the property at 123 Sheikh Zayed Road",
                "Generate a listing presentation for the villa in Palm Jumeirah",
                "Prepare marketing materials for the apartment in Dubai Marina",
                "Check RERA compliance for the office space in Business Bay",
                "Create a follow-up email for the client interested in the townhouse"
            ]
            
            # Simple simulation - in reality, this would be the actual transcription
            import random
            transcription_text = random.choice(simulated_transcriptions)
            confidence = random.uniform(0.8, 0.95)
            
            return {
                "success": True,
                "text": transcription_text,
                "confidence": confidence,
                "language": "en"
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_transcription(self, transcription_text: str) -> str:
        """Process transcription text into a structured request"""
        try:
            # This would use NLP to understand the intent and structure the request
            # For now, we'll do simple keyword matching
            
            text_lower = transcription_text.lower()
            
            # Determine request type based on keywords
            if any(keyword in text_lower for keyword in ['cma', 'comparative market analysis', 'market analysis']):
                request_type = "cma"
            elif any(keyword in text_lower for keyword in ['presentation', 'listing presentation', 'property presentation']):
                request_type = "presentation"
            elif any(keyword in text_lower for keyword in ['marketing', 'marketing materials', 'social media']):
                request_type = "marketing"
            elif any(keyword in text_lower for keyword in ['rera', 'compliance', 'legal', 'document']):
                request_type = "compliance"
            elif any(keyword in text_lower for keyword in ['follow up', 'email', 'client communication']):
                request_type = "follow_up"
            else:
                request_type = "general"
            
            # Clean and structure the request
            processed_request = f"Request Type: {request_type}\nOriginal Request: {transcription_text}\n\nPlease process this request and provide the appropriate deliverable."
            
            return processed_request
            
        except Exception as e:
            logger.error(f"Error processing transcription: {e}")
            return f"Processed request: {transcription_text}"
    
    async def _create_ai_request_from_voice(self, voice_request: VoiceRequest) -> None:
        """Create AI request from processed voice request"""
        try:
            # Import here to avoid circular imports
            from services.ai_request_processing_service import AIRequestProcessingService
            
            ai_service = AIRequestProcessingService(self.db)
            
            # Determine request type from processed request
            processed_text = voice_request.processed_request or ""
            request_type = "general"
            
            if "Request Type: cma" in processed_text:
                request_type = "cma"
            elif "Request Type: presentation" in processed_text:
                request_type = "presentation"
            elif "Request Type: marketing" in processed_text:
                request_type = "marketing"
            elif "Request Type: compliance" in processed_text:
                request_type = "compliance"
            elif "Request Type: follow_up" in processed_text:
                request_type = "follow_up"
            
            # Create AI request
            await ai_service.create_ai_request(
                agent_id=voice_request.agent_id,
                brokerage_id=voice_request.brokerage_id,
                request_type=request_type,
                request_content=processed_text,
                request_metadata={
                    "voice_request_id": voice_request.id,
                    "transcription": voice_request.transcription,
                    "transcription_confidence": float(voice_request.transcription_confidence) if voice_request.transcription_confidence else None,
                    "audio_duration": voice_request.audio_duration,
                    "language_detected": voice_request.language_detected
                },
                priority="normal",
                output_format="text"
            )
            
            logger.info(f"Created AI request from voice request {voice_request.id}")
            
        except Exception as e:
            logger.error(f"Error creating AI request from voice request: {e}")
    
    # =====================================================
    # VOICE REQUEST MANAGEMENT
    # =====================================================
    
    async def get_voice_request_status(
        self,
        voice_request_id: int,
        agent_id: int
    ) -> Dict[str, Any]:
        """Get voice request status"""
        try:
            voice_request = self.db.query(VoiceRequest).filter(
                and_(
                    VoiceRequest.id == voice_request_id,
                    VoiceRequest.agent_id == agent_id
                )
            ).first()
            
            if not voice_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Voice request not found"
                )
            
            return {
                "voice_request_id": voice_request.id,
                "processing_status": voice_request.processing_status,
                "audio_duration": voice_request.audio_duration,
                "file_size": voice_request.file_size,
                "transcription": voice_request.transcription,
                "transcription_confidence": float(voice_request.transcription_confidence) if voice_request.transcription_confidence else None,
                "processed_request": voice_request.processed_request,
                "language_detected": voice_request.language_detected,
                "error_message": voice_request.error_message,
                "created_at": voice_request.created_at,
                "updated_at": voice_request.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting voice request status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get voice request status: {str(e)}"
            )
    
    async def get_agent_voice_requests(
        self,
        agent_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get agent's voice requests"""
        try:
            query = self.db.query(VoiceRequest).filter(VoiceRequest.agent_id == agent_id)
            
            if status:
                query = query.filter(VoiceRequest.processing_status == status)
            
            total = query.count()
            voice_requests = query.order_by(desc(VoiceRequest.created_at)).offset(offset).limit(limit).all()
            
            return {
                "voice_requests": [
                    {
                        "voice_request_id": req.id,
                        "processing_status": req.processing_status,
                        "audio_duration": req.audio_duration,
                        "file_size": req.file_size,
                        "transcription": req.transcription,
                        "transcription_confidence": float(req.transcription_confidence) if req.transcription_confidence else None,
                        "language_detected": req.language_detected,
                        "error_message": req.error_message,
                        "created_at": req.created_at
                    }
                    for req in voice_requests
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting agent voice requests: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get voice requests: {str(e)}"
            )
    
    # =====================================================
    # AUDIO FILE MANAGEMENT
    # =====================================================
    
    async def cleanup_old_audio_files(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old audio files"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find old voice requests
            old_requests = self.db.query(VoiceRequest).filter(
                VoiceRequest.created_at < cutoff_date
            ).all()
            
            deleted_files = 0
            deleted_requests = 0
            
            for request in old_requests:
                # Delete audio file
                if os.path.exists(request.audio_file_path):
                    try:
                        os.remove(request.audio_file_path)
                        deleted_files += 1
                    except Exception as e:
                        logger.warning(f"Could not delete audio file {request.audio_file_path}: {e}")
                
                # Delete database record
                self.db.delete(request)
                deleted_requests += 1
            
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_files} audio files and {deleted_requests} voice requests")
            
            return {
                "deleted_files": deleted_files,
                "deleted_requests": deleted_requests,
                "cutoff_date": cutoff_date,
                "message": f"Cleanup completed successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up old audio files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup audio files: {str(e)}"
            )
    
    async def get_audio_file_info(self, voice_request_id: int, agent_id: int) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            voice_request = self.db.query(VoiceRequest).filter(
                and_(
                    VoiceRequest.id == voice_request_id,
                    VoiceRequest.agent_id == agent_id
                )
            ).first()
            
            if not voice_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Voice request not found"
                )
            
            file_path = Path(voice_request.audio_file_path)
            file_exists = file_path.exists()
            
            return {
                "voice_request_id": voice_request_id,
                "file_path": voice_request.audio_file_path,
                "file_exists": file_exists,
                "file_size": voice_request.file_size,
                "audio_duration": voice_request.audio_duration,
                "audio_format": voice_request.audio_format,
                "created_at": voice_request.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting audio file info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get audio file info: {str(e)}"
            )
    
    # =====================================================
    # ANALYTICS AND REPORTING
    # =====================================================
    
    async def get_voice_processing_analytics(
        self,
        brokerage_id: Optional[int] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get voice processing analytics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            query = self.db.query(VoiceRequest).filter(
                VoiceRequest.created_at >= start_date
            )
            
            if brokerage_id:
                query = query.filter(VoiceRequest.brokerage_id == brokerage_id)
            
            voice_requests = query.all()
            
            # Calculate statistics
            total_requests = len(voice_requests)
            successful_requests = len([req for req in voice_requests if req.processing_status == "processed"])
            failed_requests = len([req for req in voice_requests if req.processing_status == "failed"])
            
            # Average transcription confidence
            confidences = [req.transcription_confidence for req in voice_requests if req.transcription_confidence]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Average audio duration
            durations = [req.audio_duration for req in voice_requests if req.audio_duration]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Language breakdown
            languages = {}
            for req in voice_requests:
                if req.language_detected:
                    languages[req.language_detected] = languages.get(req.language_detected, 0) + 1
            
            return {
                "period_days": period_days,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "average_confidence": round(avg_confidence, 3),
                "average_duration_seconds": round(avg_duration, 2),
                "language_breakdown": languages,
                "brokerage_id": brokerage_id
            }
            
        except Exception as e:
            logger.error(f"Error getting voice processing analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get analytics: {str(e)}"
            )
