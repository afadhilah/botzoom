
# ============================================================
# FILE 16: app/api/transcripts.py
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pathlib import Path
from app.database import get_db
from app.models.meeting import Meeting
from app.models.transcript import Transcript, Summary
from app.schemas.transcript import TranscriptResponse, SummaryResponse

router = APIRouter()

@router.get("/meeting/{meeting_id}", response_model=List[TranscriptResponse])
async def get_meeting_transcripts(meeting_id: UUID, db: Session = Depends(get_db)):
    """
    Get all transcripts for a meeting
    """
    transcripts = db.query(Transcript).filter(
        Transcript.meeting_id == meeting_id
    ).order_by(Transcript.start_time).all()
    
    if not transcripts:
        raise HTTPException(status_code=404, detail="No transcripts found for this meeting")
    
    return transcripts

@router.get("/meeting/{meeting_id}/summary", response_model=SummaryResponse)
async def get_meeting_summary(meeting_id: UUID, db: Session = Depends(get_db)):
    """
    Get summary for a meeting
    """
    summary = db.query(Summary).filter(Summary.meeting_id == meeting_id).first()
    
    if not summary:
        raise HTTPException(status_code=404, detail="No summary found for this meeting")
    
    return summary

@router.get("/meeting/{meeting_id}/export/txt")
async def export_transcript_txt(meeting_id: UUID, db: Session = Depends(get_db)):
    """
    Export transcript as TXT file
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    transcripts = db.query(Transcript).filter(
        Transcript.meeting_id == meeting_id
    ).order_by(Transcript.start_time).all()
    
    if not transcripts:
        raise HTTPException(status_code=404, detail="No transcripts found")
    
    # Generate TXT file
    from app.services.export import ExportService
    txt_file = ExportService.export_to_txt(meeting, transcripts)
    
    return FileResponse(
        txt_file,
        media_type="text/plain",
        filename=f"transcript_{meeting.zoom_meeting_id}.txt"
    )

@router.get("/meeting/{meeting_id}/export/json")
async def export_transcript_json(meeting_id: UUID, db: Session = Depends(get_db)):
    """
    Export transcript as JSON file
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    transcripts = db.query(Transcript).filter(
        Transcript.meeting_id == meeting_id
    ).order_by(Transcript.start_time).all()
    
    summary = db.query(Summary).filter(Summary.meeting_id == meeting_id).first()
    
    if not transcripts:
        raise HTTPException(status_code=404, detail="No transcripts found")
    
    # Generate JSON file
    from app.services.export import ExportService
    json_file = ExportService.export_to_json(meeting, transcripts, summary)
    
    return FileResponse(
        json_file,
        media_type="application/json",
        filename=f"transcript_{meeting.zoom_meeting_id}.json"
    )
