"""
💾 [Storage] Local Asset Storage Service

Handles local file storage and serving for property photos, brochure PDFs, and other assets.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageService:
    """Local file storage service for assets"""
    
    def __init__(self):
        self.storage_type = settings.asset_storage
        self.local_dir = Path(settings.asset_local_dir)
        
        # Ensure storage directory exists
        if self.storage_type == "local":
            self.local_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 [Storage] Local storage initialized at {self.local_dir}")
    
    async def save_bytes(self, namespace: str, filename: str, data: bytes) -> str:
        """
        Save bytes to storage and return public URL
        
        Args:
            namespace: Directory namespace (e.g., 'properties', 'brochures')
            filename: Filename to save as
            data: File bytes
            
        Returns:
            Public URL to access the file
        """
        if self.storage_type != "local":
            raise HTTPException(status_code=500, detail="Only local storage supported")
            
        # Create namespace directory
        namespace_dir = self.local_dir / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename to avoid collisions
        file_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{file_id}{ext}"
        
        file_path = namespace_dir / unique_filename
        
        try:
            # Write file
            with open(file_path, 'wb') as f:
                f.write(data)
            
            # Return public URL
            public_url = f"{settings.api_base}/assets/{namespace}/{unique_filename}"
            logger.info(f"📝 [Storage] Saved {len(data)} bytes to {file_path} -> {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"❌ [Storage] Failed to save file {filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    def resolve_url(self, path: str) -> str:
        """
        Resolve storage path to public URL
        
        Args:
            path: Storage path (e.g., 'properties/photo.jpg')
            
        Returns:
            Public URL
        """
        return f"{settings.api_base}/assets/{path}"
    
    def get_file_path(self, asset_path: str) -> Path:
        """
        Get local file path for an asset URL path
        
        Args:
            asset_path: Asset URL path (e.g., 'properties/photo.jpg')
            
        Returns:
            Local file path
        """
        if self.storage_type != "local":
            raise HTTPException(status_code=500, detail="Only local storage supported")
            
        # Remove leading slash if present
        asset_path = asset_path.lstrip('/')
        
        file_path = self.local_dir / asset_path
        
        # Security check: ensure file is within storage directory
        try:
            file_path.resolve().relative_to(self.local_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid asset path")
            
        return file_path
    
    def file_exists(self, asset_path: str) -> bool:
        """Check if file exists in storage"""
        try:
            file_path = self.get_file_path(asset_path)
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False
    
    async def delete_file(self, asset_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            asset_path: Asset URL path
            
        Returns:
            True if deleted successfully, False if file didn't exist
        """
        try:
            file_path = self.get_file_path(asset_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"🗑️ [Storage] Deleted {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ [Storage] Failed to delete {asset_path}: {e}")
            return False
    
    def serve_file(self, asset_path: str) -> FileResponse:
        """
        Serve file via FileResponse
        
        Args:
            asset_path: Asset URL path
            
        Returns:
            FileResponse for the file
        """
        file_path = self.get_file_path(asset_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
            
        # Determine media type based on extension
        media_type = self._get_media_type(file_path.suffix.lower())
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=file_path.name
        )
    
    def _get_media_type(self, extension: str) -> str:
        """Get media type for file extension"""
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg', 
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.json': 'application/json',
        }
        return media_types.get(extension, 'application/octet-stream')


# Global storage service instance
storage_service = StorageService()


def get_storage_service() -> StorageService:
    """Get storage service instance for dependency injection"""
    return storage_service