
# ============================================================
# FILE 8: app/models/meeting.py
# ============================================================
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    zoom_meeting_id = Column(String(255), nullable=False, index=True)
    meeting_topic = Column(String(500))
    bot_name = Column(String(255), default="Meeting Bot")
    
    # Status: scheduled, joining, recording, processing, completed, failed
    status = Column(String(50), default="scheduled", index=True)
    
    # Timestamps
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    # Recording info
    recording_file_path = Column(Text)
    recording_duration = Column(Integer)  # seconds
    
    # Processing info
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="meetings")
    transcripts = relationship("Transcript", back_populates="meeting", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
