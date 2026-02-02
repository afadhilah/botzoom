# ============================================================
# FILE 11: app/schemas/meeting.py
# ============================================================
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class MeetingCreate(BaseModel):
    zoom_meeting_id: str
    meeting_topic: Optional[str] = None
    bot_name: str = "Meeting Bot"
    scheduled_at: Optional[datetime] = None

class MeetingResponse(BaseModel):
    id: UUID
    zoom_meeting_id: str
    meeting_topic: Optional[str]
    bot_name: str
    status: str
    
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    
    recording_file_path: Optional[str]
    recording_duration: Optional[int]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True