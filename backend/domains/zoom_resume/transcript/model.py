"""
Transcript database model for meeting transcriptions.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from database.base import Base


class TranscriptStatus(str, enum.Enum):
    """Transcript processing status lifecycle."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class Transcript(Base):
    """Transcript model for storing meeting transcription results."""
    
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Audio source
    audio_url = Column(String(500), nullable=False)
    
    # Processing status
    status = Column(
        SQLEnum(TranscriptStatus),
        nullable=False,
        default=TranscriptStatus.PENDING,
        index=True
    )
    
    # Transcription results
    language = Column(String(10), nullable=True)
    full_text = Column(Text, nullable=True)
    segments_json = Column("segments_json", JSON, nullable=True)
    
    @property
    def segments(self):
        """Expose segments_json as segments for Pydantic serialization."""
        return self.segments_json
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="transcripts")
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, user_id={self.user_id}, status={self.status})>"
