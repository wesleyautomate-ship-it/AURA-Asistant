"""
File Storage Service
===================

This service handles file uploads, storage, and retrieval for the AI request system.
It supports audio files, generated deliverables, and brand assets.
"""

import os
import uuid
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import UploadFile, HTTPException
import aiofiles
from datetime import datetime


class FileStorageService:
    """Service for handling file storage operations"""

    def __init__(self):
        self.base_path = Path(os.getenv("UPLOAD_PATH", "uploads"))
        self.audio_path = self.base_path / "audio"
        self.deliverables_path = self.base_path / "deliverables"
        self.previews_path = self.base_path / "previews"
        self.brand_assets_path = self.base_path / "brand_assets"

        # Create directories if they don't exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for path in [
            self.audio_path,
            self.deliverables_path,
            self.previews_path,
            self.brand_assets_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    async def save_audio_file(
        self, file: UploadFile, request_id: str
    ) -> Dict[str, Any]:
        """Save an audio file for a request"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = self._get_file_extension(file.filename)
            filename = f"{file_id}{file_extension}"

            # Create request-specific directory
            request_dir = self.audio_path / request_id
            request_dir.mkdir(exist_ok=True)

            file_path = request_dir / filename

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Get file info
            file_size = file_path.stat().st_size

            return {
                "file_id": file_id,
                "filename": filename,
                "original_filename": file.filename,
                "file_path": str(file_path),
                "url": f"/uploads/audio/{request_id}/{filename}",
                "file_size": file_size,
                "mime_type": file.content_type,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save audio file: {str(e)}"
            )

    async def save_deliverable(
        self,
        content: bytes,
        request_id: str,
        file_type: str,
        filename: str,
        mime_type: str,
    ) -> Dict[str, Any]:
        """Save a generated deliverable"""
        try:
            # Create request-specific directory
            request_dir = self.deliverables_path / request_id
            request_dir.mkdir(exist_ok=True)

            file_path = request_dir / filename

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            # Generate preview if it's an image
            preview_url = None
            if file_type in ["image", "pdf"]:
                preview_url = await self._generate_preview(
                    file_path, request_id, filename
                )

            return {
                "filename": filename,
                "file_path": str(file_path),
                "url": f"/uploads/deliverables/{request_id}/{filename}",
                "preview_url": preview_url,
                "file_size": len(content),
                "mime_type": mime_type,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save deliverable: {str(e)}"
            )

    async def save_brand_asset(
        self, file: UploadFile, brokerage_id: str, asset_type: str
    ) -> Dict[str, Any]:
        """Save a brand asset"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = self._get_file_extension(file.filename)
            filename = f"{file_id}{file_extension}"

            # Create brokerage-specific directory
            brokerage_dir = self.brand_assets_path / brokerage_id
            brokerage_dir.mkdir(exist_ok=True)

            file_path = brokerage_dir / filename

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            return {
                "file_id": file_id,
                "filename": filename,
                "original_filename": file.filename,
                "file_path": str(file_path),
                "url": f"/uploads/brand_assets/{brokerage_id}/{filename}",
                "file_size": file_path.stat().st_size,
                "mime_type": file.content_type,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save brand asset: {str(e)}"
            )

    async def get_file(self, file_path: str) -> Optional[bytes]:
        """Get file content by path"""
        try:
            path = Path(file_path)
            if path.exists():
                async with aiofiles.open(path, "rb") as f:
                    return await f.read()
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    async def delete_request_files(self, request_id: str) -> bool:
        """Delete all files for a request"""
        try:
            # Delete audio files
            audio_dir = self.audio_path / request_id
            if audio_dir.exists():
                shutil.rmtree(audio_dir)

            # Delete deliverables
            deliverables_dir = self.deliverables_path / request_id
            if deliverables_dir.exists():
                shutil.rmtree(deliverables_dir)

            # Delete previews
            previews_dir = self.previews_path / request_id
            if previews_dir.exists():
                shutil.rmtree(previews_dir)

            return True
        except Exception as e:
            print(f"Error deleting request files {request_id}: {e}")
            return False

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        if filename:
            return Path(filename).suffix
        return ""

    async def _generate_preview(
        self, file_path: Path, request_id: str, filename: str
    ) -> Optional[str]:
        """Generate a preview for a file"""
        try:
            # Create preview directory
            preview_dir = self.previews_path / request_id
            preview_dir.mkdir(exist_ok=True)

            # For now, just return a placeholder preview URL
            # In a real implementation, you would generate actual previews
            preview_filename = f"preview_{Path(filename).stem}.jpg"
            preview_path = preview_dir / preview_filename

            # Create a placeholder preview file
            # In production, you would use libraries like Pillow for images,
            # or pdf2image for PDFs
            preview_path.touch()

            return f"/uploads/previews/{request_id}/{preview_filename}"

        except Exception as e:
            print(f"Error generating preview for {file_path}: {e}")
            return None

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                return {
                    "filename": path.name,
                    "file_size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime),
                    "exists": True,
                }
            return None
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None


# Global instance
file_storage = FileStorageService()
