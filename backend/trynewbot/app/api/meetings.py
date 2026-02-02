
# ============================================================
# FILE 15: app/api/meetings.py
# ============================================================
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.services.zoom_bot import ZoomBotService

router = APIRouter()

@router.post("/", response_model=MeetingResponse, status_code=201)
async def create_meeting(
    meeting: MeetingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Schedule a new meeting to record
    
    This will:
    1. Create a meeting record in the database
    2. Start the bot to join and record the meeting (background task)
    """
    # Create meeting record
    db_meeting = Meeting(
        zoom_meeting_id=meeting.zoom_meeting_id,
        meeting_topic=meeting.meeting_topic,
        bot_name=meeting.bot_name,
        scheduled_at=meeting.scheduled_at,
        status="scheduled"
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    # Start bot in background
    background_tasks.add_task(
        ZoomBotService.join_and_record,
        meeting_id=str(db_meeting.id),
        zoom_meeting_id=meeting.zoom_meeting_id,
        db=db
    )
    
    return db_meeting

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """
    Get meeting details by ID
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all meetings with optional filtering
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by status (scheduled, recording, processing, completed, failed)
    """
    query = db.query(Meeting)
    
    if status:
        query = query.filter(Meeting.status == status)
    
    meetings = query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()
    return meetings

@router.post("/{meeting_id}/process", status_code=202)
async def process_meeting(
    meeting_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger processing for a completed recording
    
    Use this if automatic processing failed or was skipped
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.recording_file_path:
        raise HTTPException(
            status_code=400,
            detail="No recording file found for this meeting"
        )
    
    background_tasks.add_task(
        ZoomBotService.process_recording,
        meeting_id=str(meeting_id),
        db=db
    )
    
    return {
        "message": "Processing started",
        "meeting_id": str(meeting_id),
        "status": "processing"
    }

@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a meeting and all associated data
    
    WARNING: This will also delete:
    - All transcripts
    - Summary
    - Recording file (if exists)
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Delete recording file if exists
    if meeting.recording_file_path:
        from pathlib import Path
        recording_path = Path(meeting.recording_file_path)
        if recording_path.exists():
            recording_path.unlink()
    
    db.delete(meeting)
    db.commit()
    
    return None