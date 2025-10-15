"""
Gemini Transcription Service
============================

Real-time audio transcription service using Google's Gemini API.
Integrates with the existing AURA intelligence pipeline.

Features:
- Audio file upload and validation
- Automatic MIME type detection
- Gemini API integration for speech-to-text
- Error handling and logging
- Support for multiple audio formats
"""

import os
import logging
import mimetypes
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import tempfile

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import requests.exceptions

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiTranscriptionService:
    """Service for audio transcription using Google Gemini API"""

    def __init__(self):
        self.settings = get_settings()
        self._configure_gemini()

        # Supported audio formats
        self.supported_formats = {
            "audio/wav": "wav",
            "audio/mp3": "mp3",
            "audio/mpeg": "mp3",
            "audio/m4a": "m4a",
            "audio/aac": "aac",
            "audio/ogg": "ogg",
            "audio/flac": "flac",
        }

        # File size limit (25MB)
        self.max_file_size = 25 * 1024 * 1024

    def _configure_gemini(self) -> None:
        """Configure Gemini API with the API key"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")

            genai.configure(api_key=api_key)
            logger.info("Gemini API configured successfully for transcription service")

        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise

    async def transcribe_audio(
        self, audio_file_content: bytes, filename: str, mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio content using Gemini API

        Args:
            audio_file_content: Raw audio file bytes
            filename: Original filename for MIME type detection
            mime_type: Optional explicit MIME type

        Returns:
            Dictionary with transcription results
        """
        start_time = datetime.utcnow()

        try:
            # Validate and detect MIME type
            detected_mime_type = self._detect_mime_type(
                audio_file_content, filename, mime_type
            )

            # Validate file size
            self._validate_file_size(len(audio_file_content))

            # Validate format
            self._validate_audio_format(detected_mime_type)

            logger.info(
                f"Starting transcription for file: {filename} (MIME: {detected_mime_type})"
            )

            # Create temporary file for Gemini API
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{self.supported_formats[detected_mime_type]}"
            ) as temp_file:
                temp_file.write(audio_file_content)
                temp_file_path = temp_file.name

            try:
                # Upload file to Gemini
                uploaded_file = genai.upload_file(
                    path=temp_file_path,
                    display_name=f"audio_transcription_{filename}",
                    mime_type=detected_mime_type,
                )

                # Wait for file processing
                import time

                while uploaded_file.state.name == "PROCESSING":
                    logger.debug("Waiting for file processing...")
                    time.sleep(2)
                    uploaded_file = genai.get_file(uploaded_file.name)

                if uploaded_file.state.name == "FAILED":
                    raise Exception(f"File processing failed: {uploaded_file.state}")

                # Initialize Gemini model for transcription
                model = genai.GenerativeModel("gemini-2.0-flash")

                # Create transcription prompt
                prompt = """
                Please transcribe the audio content in this file. 
                
                Provide only the transcribed text without any additional commentary, formatting, or explanations.
                If multiple speakers are present, indicate speaker changes naturally in the flow.
                Maintain proper punctuation and capitalization.
                If you cannot transcribe certain portions, indicate with [inaudible].
                """

                # Generate transcription
                response = model.generate_content([uploaded_file, prompt])

                # Clean up uploaded file
                genai.delete_file(uploaded_file.name)

                # Process response
                transcribed_text = response.text.strip()
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                # Calculate confidence score based on response quality
                confidence = self._calculate_confidence(transcribed_text)

                # Detect language (basic detection)
                detected_language = self._detect_language(transcribed_text)

                result = {
                    "text": transcribed_text,
                    "confidence": confidence,
                    "language_detected": detected_language,
                    "processing_time_ms": processing_time,
                    "audio_format": self.supported_formats[detected_mime_type],
                    "file_size_bytes": len(audio_file_content),
                    "is_mock": False,
                    "model_used": "gemini-2.0-flash",
                }

                logger.info(
                    f"Transcription completed successfully in {processing_time}ms"
                )
                logger.debug(
                    f"Transcribed text length: {len(transcribed_text)} characters"
                )

                return result

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError as e:
                    logger.warning(
                        f"Failed to delete temporary file {temp_file_path}: {e}"
                    )

        except google_exceptions.Unauthenticated as e:
            logger.error(f"Gemini authentication failed: {e}")
            raise Exception("Authentication failed. Please check your API key.")

        except google_exceptions.PermissionDenied as e:
            logger.error(f"Gemini permission denied: {e}")
            raise Exception(
                "Permission denied. Your API key may not have required permissions."
            )

        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Gemini quota exceeded: {e}")
            raise Exception("API quota exceeded. Please try again later.")

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Network connection error: {e}")
            raise Exception(
                "Network connection failed. Please check your internet connection."
            )

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise Exception("Request timed out. Please try again.")

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Transcription failed: {str(e)}")

    def _detect_mime_type(
        self,
        file_content: bytes,
        filename: str,
        explicit_mime_type: Optional[str] = None,
    ) -> str:
        """Detect MIME type from file content and filename"""

        # Use explicit MIME type if provided and valid
        if explicit_mime_type and explicit_mime_type in self.supported_formats:
            return explicit_mime_type

        # Try to guess from filename
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type and guessed_type in self.supported_formats:
            return guessed_type

        # Try to detect from file signature (magic numbers)
        file_signatures = {
            b"RIFF": "audio/wav",
            b"ID3": "audio/mp3",
            b"\xff\xfb": "audio/mp3",
            b"\xff\xf3": "audio/mp3",
            b"\xff\xf2": "audio/mp3",
            b"ftyp": "audio/m4a",  # M4A/AAC
            b"OggS": "audio/ogg",
            b"fLaC": "audio/flac",
        }

        # Check first few bytes for signatures
        for signature, mime_type in file_signatures.items():
            if file_content.startswith(signature) or signature in file_content[:20]:
                return mime_type

        # Default fallback
        return "audio/wav"

    def _validate_file_size(self, file_size: int) -> None:
        """Validate audio file size"""
        if file_size > self.max_file_size:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds maximum limit of {self.max_file_size} bytes"
            )

        if file_size == 0:
            raise ValueError("Audio file is empty")

    def _validate_audio_format(self, mime_type: str) -> None:
        """Validate audio format is supported"""
        if mime_type not in self.supported_formats:
            supported_list = ", ".join(self.supported_formats.keys())
            raise ValueError(
                f"Unsupported audio format: {mime_type}. Supported formats: {supported_list}"
            )

    def _calculate_confidence(self, transcribed_text: str) -> float:
        """Calculate confidence score based on transcription quality indicators"""
        if not transcribed_text:
            return 0.0

        confidence = 0.8  # Base confidence

        # Boost confidence for longer, more complete text
        if len(transcribed_text) > 100:
            confidence += 0.1
        elif len(transcribed_text) < 20:
            confidence -= 0.2

        # Reduce confidence for incomplete markers
        inaudible_count = transcribed_text.lower().count("[inaudible]")
        if inaudible_count > 0:
            confidence -= min(0.3, inaudible_count * 0.1)

        # Ensure confidence is in valid range
        return max(0.0, min(1.0, confidence))

    def _detect_language(self, text: str) -> str:
        """Basic language detection (can be enhanced with more sophisticated detection)"""
        if not text:
            return "unknown"

        # Simple heuristic - check for Arabic characters
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        if arabic_chars > len(text) * 0.3:
            return "ar"

        # Default to English
        return "en"

    def get_supported_formats(self) -> Dict[str, str]:
        """Get list of supported audio formats"""
        return self.supported_formats.copy()
