

# ============================================================
# FILE 9: app/models/transcript.py
# ============================================================
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True)
    
    # Speaker info
    speaker_label = Column(String(50))  # SPEAKER_00, SPEAKER_01, etc.
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    
    # Content
    text = Column(Text, nullable=False)
    language = Column(String(10), default="id")
    
    # Confidence scores
    transcription_confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="transcripts")

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), unique=True)
    
    summary_text = Column(Text, nullable=False)
    summary_type = Column(String(50), default="auto")  # auto, manual
    
    # Metadata
    total_speakers = Column(Integer)
    total_segments = Column(Integer)
    key_points = Column(JSONB)  # Array of key discussion points
    action_items = Column(JSONB)  # Array of action items
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="summary")