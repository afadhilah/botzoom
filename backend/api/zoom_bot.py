"""
API endpoints for Zoom bot integration.
Allows triggering bot to join Zoom meetings and record audio.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import subprocess
import os
import logging
from pathlib import Path
import sys

from database.session import get_db
from domains.auth.utils import get_current_active_user
from domains.user.model import User

router = APIRouter(prefix="/zoom", tags=["Zoom Bot"])

logger = logging.getLogger(__name__)


class JoinMeetingRequest(BaseModel):
    meeting_link: str
    bot_name: Optional[str] = "Meeting Transcript Bot"
    min_record_time: Optional[int] = 7200  # 2 hours default


class JoinMeetingResponse(BaseModel):
    message: str
    bot_id: str
    meeting_link: str


def start_zoom_bot_background(
    meeting_link: str,
    bot_name: str = "Meeting Transcript Bot",
    min_record_time: int = 7200,
):
    """
    Start Zoom bot in background using integrated bot code.
    
    Args:
        meeting_link: Zoom meeting URL or ID
        bot_name: Name displayed in meeting
        min_record_time: Minimum recording time in seconds
    """
    try:
        from integrations.zoom.bot import ZoomBot
        from integrations.zoom.bot_utils import clean_meeting_link
        
        # Clean meeting link
        cleaned_link = clean_meeting_link(meeting_link)
        
        # Create and run bot
        bot = ZoomBot(
            meeting_link=cleaned_link,
            bot_name=bot_name,
            min_record_time=min_record_time,
            output_dir="storage/zoom_recordings"
        )
        
        bot_id = bot.id
        logger.info(f"Starting Zoom bot {bot_id} for meeting: {cleaned_link}")
        
        # Run bot (this will block, so should be in background task)
        bot.run()
        
        return bot_id
        
    except ImportError as e:
        logger.error(f"Zoom bot dependencies not installed: {e}")
        raise Exception("Zoom bot requires selenium and webdriver-manager. Install with: pip install selenium webdriver-manager")
    except Exception as e:
        logger.error(f"Failed to start Zoom bot: {e}")
        raise


@router.post("/join", response_model=JoinMeetingResponse)
async def join_zoom_meeting(
    request: JoinMeetingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trigger bot to join Zoom meeting and start recording.
    
    The bot will:
    1. Join the meeting via web browser (Selenium)
    2. Record audio during the meeting
    3. Upload recording to storage
    4. Trigger transcription pipeline
    """
    try:
        # Validate meeting link
        if not request.meeting_link:
            raise HTTPException(status_code=400, detail="Meeting link is required")
        
        # Clean up meeting link
        meeting_link = request.meeting_link.strip()
        
        # Generate bot ID for tracking
        import uuid
        bot_id = str(uuid.uuid4())
        
        # Add bot execution to background tasks
        background_tasks.add_task(
            start_zoom_bot_background,
            meeting_link=meeting_link,
            bot_name=request.bot_name or "Meeting Transcript Bot",
            min_record_time=request.min_record_time or 7200
        )
        
        logger.info(f"Zoom bot {bot_id} queued for meeting: {meeting_link}")
        
        return JoinMeetingResponse(
            message="Zoom bot is joining the meeting",
            bot_id=bot_id,
            meeting_link=meeting_link
        )
        
    except Exception as e:
        logger.error(f"Error joining Zoom meeting: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Zoom bot: {str(e)}"
        )
