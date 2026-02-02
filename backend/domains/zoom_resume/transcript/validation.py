"""
File validation for transcript uploads.
Validates file size, extension, and optionally MIME type.
"""
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Set


class FileValidator:
    """Validates uploaded audio files for security and resource protection."""
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: Set[str] = {".wav", ".mp3", ".m4a", ".flac", ".webm", ".ogg"}
    
    @staticmethod
    def validate_upload(file: UploadFile) -> None:
        """
        Validate uploaded file for security and resource constraints.
        
        Args:
            file: FastAPI UploadFile object
            
        Raises:
            HTTPException: If validation fails (400 for invalid format, 413 for too large)
        """
        # Validate filename exists
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        # Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in FileValidator.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension '{ext}'. Allowed: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
            )
        
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if size == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        if size > FileValidator.MAX_FILE_SIZE:
            max_mb = FileValidator.MAX_FILE_SIZE // (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_mb}MB"
            )
