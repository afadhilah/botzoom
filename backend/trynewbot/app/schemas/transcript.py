# ============================================================
# FILE 12: app/schemas/transcript.py
# ============================================================
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

class TranscriptResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    speaker_label: str
    start_time: float
    end_time: float
    text: str
    language: str
    transcription_confidence: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    summary_text: str
    summary_type: str
    total_speakers: Optional[int]
    total_segments: Optional[int]
    key_points: Optional[List[str]]
    action_items: Optional[List[Dict[str, Any]]]
    created_at: datetime
    
    class Config:
        from_attributes = True
