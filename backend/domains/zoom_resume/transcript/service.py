"""
Transcript service layer - Pure business logic.
NO FastAPI imports, NO HTTP context.
Reusable by API, workers, and Zoom webhook.
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import logging

from domains.zoom_resume.transcript.model import Transcript, TranscriptStatus

logger = logging.getLogger(__name__)


class TranscriptService:
    """Pure domain service for transcript business logic."""
    
    @staticmethod
    def create_transcript(
        db: Session,
        user_id: int,
        audio_url: str
    ) -> Transcript:
        """
        Create a new transcript with PENDING status.
        
        Args:
            db: Database session
            user_id: ID of the user creating the transcript
            audio_url: URL or path to the audio file
            
        Returns:
            Created Transcript instance
        """
        transcript = Transcript(
            user_id=user_id,
            audio_url=audio_url,
            status=TranscriptStatus.PENDING
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        return transcript
    
    @staticmethod
    def update_status(
        db: Session,
        transcript_id: int,
        status: TranscriptStatus,
        error_message: Optional[str] = None
    ) -> Transcript:
        """
        Update transcript status.
        
        Args:
            db: Database session
            transcript_id: ID of the transcript
            status: New status
            error_message: Error message if status is FAILED
            
        Returns:
            Updated Transcript instance
            
        Raises:
            ValueError: If transcript not found
        """
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")
        
        transcript.status = status
        if error_message:
            transcript.error_message = error_message
        transcript.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transcript)
        return transcript
    
    @staticmethod
    def cleanup_audio_file(audio_url: str) -> None:
        """
        Delete audio file from filesystem.
        Called after successful transcription to free disk space.
        
        Args:
            audio_url: Path to audio file
        """
        try:
            file_path = Path(audio_url)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted audio file: {audio_url}")
        except Exception as e:
            logger.warning(f"Failed to delete audio file {audio_url}: {e}")
    
    @staticmethod
    def save_result(
        db: Session,
        transcript_id: int,
        language: str,
        full_text: str,
        segments: List[dict],
        cleanup_file: bool = True
    ) -> Transcript:
        """
        Save transcription results and mark as DONE.
        Optionally cleanup audio file after successful save.
        
        Args:
            db: Database session
            transcript_id: ID of the transcript
            language: Detected language
            full_text: Full transcription text
            segments: List of transcript segments
            cleanup_file: Whether to delete audio file after save (default: True)
            
        Returns:
            Updated Transcript instance
            
        Raises:
            ValueError: If transcript not found
        """
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")
        
        transcript.language = language
        transcript.full_text = full_text
        transcript.segments_json = segments
        transcript.status = TranscriptStatus.DONE
        transcript.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transcript)
        
        # Cleanup audio file after successful save
        if cleanup_file:
            TranscriptService.cleanup_audio_file(transcript.audio_url)
        
        return transcript
    
    @staticmethod
    def get_by_id(
        db: Session,
        transcript_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Transcript]:
        """
        Get transcript by ID with optional user authorization check.
        
        Args:
            db: Database session
            transcript_id: ID of the transcript
            user_id: Optional user ID for authorization check
            
        Returns:
            Transcript instance or None
        """
        query = db.query(Transcript).filter(Transcript.id == transcript_id)
        
        if user_id is not None:
            query = query.filter(Transcript.user_id == user_id)
        
        return query.first()
    
    @staticmethod
    def list_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Transcript], int]:
        """
        List transcripts for a user with pagination.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of transcripts, total count)
        """
        query = db.query(Transcript).filter(Transcript.user_id == user_id)
        
        total = query.count()
        transcripts = query.order_by(Transcript.created_at.desc()).offset(skip).limit(limit).all()
        
        return transcripts, total
    
    @staticmethod
    def get_latest_transcript(db: Session) -> Optional[Transcript]:
        """
        Get the most recent transcript (any user).
        
        Args:
            db: Database session
            
        Returns:
            Latest Transcript instance or None
        """
        return db.query(Transcript).order_by(Transcript.created_at.desc()).first()
