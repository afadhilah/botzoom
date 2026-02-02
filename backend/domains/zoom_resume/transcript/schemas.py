"""
Pydantic schemas for Transcript domain.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    """Single transcript segment with timestamp and speaker."""
    id: int
    start: float
    end: float
    text: str
    speaker: str = "Speaker 1"


class TranscriptCreate(BaseModel):
    """Request schema for creating a new transcript."""
    audio_url: str = Field(..., description="URL or path to audio file")


class TranscriptResponse(BaseModel):
    """Response schema for single transcript."""
    id: int
    user_id: int
    audio_url: str
    status: str
    language: Optional[str] = None
    full_text: Optional[str] = None
    segments: Optional[List[TranscriptSegment]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TranscriptStatusResponse(BaseModel):
    """Response schema for status check."""
    id: int
    status: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class TranscriptListResponse(BaseModel):
    """Response schema for paginated transcript list."""
    total: int
    items: List[TranscriptResponse]
    skip: int
    limit: int
