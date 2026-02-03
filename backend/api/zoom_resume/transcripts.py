"""
API endpoints for transcript management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil
import uuid

from database.base import get_db
from domains.auth.utils import get_current_active_user
from domains.user.model import User
from domains.zoom_resume.transcript.service import TranscriptService
from domains.zoom_resume.transcript.validation import FileValidator
from domains.zoom_resume.transcript.schemas import (
    TranscriptResponse,
    TranscriptListResponse,
    TranscriptStatusResponse
)

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
async def upload_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload audio file for async transcription.
    
    Flow:
    1. Validate file (extension, size)
    2. Save to uploads/ directory
    3. Create PENDING transcript record
    4. Enqueue background worker
    5. Return transcript_id immediately
    
    Client should poll GET /transcripts/{id}/status for updates.
    
    Args:
        file: Audio file upload
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TranscriptResponse with PENDING status
        
    Raises:
        HTTPException: 400 for invalid file, 413 for too large, 500 for server error
    """
    from workers.meeting.transcribe_worker import enqueue_transcript
    
    # Validate file
    FileValidator.validate_upload(file)
    
    # Generate unique filename
    ext = Path(file.filename or "audio").suffix.lower()
    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_name
    
    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create PENDING transcript record
        transcript = TranscriptService.create_transcript(
            db,
            user_id=current_user.id,
            audio_url=str(file_path)
        )
        
        # Enqueue async worker for background processing
        enqueue_transcript(transcript.id)
        
        # Return immediately with PENDING status
        return TranscriptResponse.from_orm(transcript)
        
    except Exception as e:
        # Cleanup file on failure
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload transcript: {str(e)}"
        )


@router.get("", response_model=TranscriptListResponse)
def list_transcripts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all transcripts for current user with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TranscriptListResponse with items and pagination info
    """
    transcripts, total = TranscriptService.list_by_user(
        db, current_user.id, skip, limit
    )
    
    return TranscriptListResponse(
        total=total,
        items=[TranscriptResponse.from_orm(t) for t in transcripts],
        skip=skip,
        limit=limit
    )


@router.get("/{transcript_id}", response_model=TranscriptResponse)
def get_transcript(
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get single transcript by ID.
    
    Args:
        transcript_id: ID of the transcript
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TranscriptResponse
        
    Raises:
        HTTPException: 404 if transcript not found or unauthorized
    """
    transcript = TranscriptService.get_by_id(db, transcript_id, current_user.id)
    
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    return TranscriptResponse.from_orm(transcript)


@router.get("/{transcript_id}/status", response_model=TranscriptStatusResponse)
def get_transcript_status(
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check transcript processing status.
    
    Args:
        transcript_id: ID of the transcript
        db: Database session
        current_user: Authenticated user
        
    Returns:
        TranscriptStatusResponse with status and error message
        
    Raises:
        HTTPException: 404 if transcript not found or unauthorized
    """
    transcript = TranscriptService.get_by_id(db, transcript_id, current_user.id)
    
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    return TranscriptStatusResponse.from_orm(transcript)


@router.delete("/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcript(
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete transcript and associated files.
    
    Args:
        transcript_id: ID of the transcript to delete
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: 404 if transcript not found or unauthorized
    """
    deleted = TranscriptService.delete_transcript(
        db, 
        transcript_id, 
        user_id=current_user.id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found"
        )
    
    return None
