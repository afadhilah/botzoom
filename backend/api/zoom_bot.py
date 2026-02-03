"""
API endpoints for Zoom bot integration.
Allows triggering bot to join Zoom meetings and record audio.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import logging
from pathlib import Path

from database.session import get_db
from domains.auth.utils import get_current_active_user
from domains.user.model import User

router = APIRouter(prefix="/zoom", tags=["Zoom Bot"])

# Setup logger with handler for file output
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


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
    Start Zoom bot as independent subprocess.
    
    Args:
        meeting_link: Zoom meeting URL or ID
        bot_name: Name displayed in meeting
        min_record_time: Minimum recording time in seconds
    """
    try:
        import subprocess
        from pathlib import Path
        import uuid
        import json
        
        # Path to bot script
        backend_dir = Path(__file__).parent.parent
        bot_script = backend_dir / "run_zoom_bot.py"
        venv_python = backend_dir / "venv" / "bin" / "python3"
        
        # Generate bot UUID
        bot_uuid = str(uuid.uuid4())
        
        # Build command with bot UUID
        cmd = [
            str(venv_python),
            str(bot_script),
            meeting_link,
            "--bot-id", bot_uuid,
            "--bot-name", bot_name,
            "--duration", str(min_record_time),
            "--output-dir", "storage/zoom_recordings"
        ]
        
        # Run bot as detached subprocess
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # Detach from parent
        )
        
        # Save PID to file for later termination
        pid_file = backend_dir / "out" / f"{bot_uuid}.pid"
        pid_file.parent.mkdir(exist_ok=True)
        pid_file.write_text(str(process.pid))
        
        logger.info(f"Started Zoom bot process {process.pid} (UUID: {bot_uuid}) for meeting: {meeting_link}")
        logger.info(f"PID saved to: {pid_file}")
        
        return bot_uuid
        
    except Exception as e:
        logger.error(f"Failed to start Zoom bot: {e}")
        raise


@router.post("/join", response_model=JoinMeetingResponse)
async def join_zoom_meeting(
    request: JoinMeetingRequest,
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
        
        # Start bot as independent subprocess (non-blocking)
        bot_id = start_zoom_bot_background(
            meeting_link=meeting_link,
            bot_name=request.bot_name or "Meeting Transcript Bot",
            min_record_time=request.min_record_time or 7200
        )
        
        logger.info(f"Zoom bot {bot_id} started for meeting: {meeting_link}")
        
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


class EndBotRequest(BaseModel):
    bot_id: str


@router.post("/end")
async def end_zoom_bot(
    request: EndBotRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    End active Zoom bot session by terminating the process.
    """
    import os
    import signal
    from pathlib import Path
    
    logger.info(f"End bot request received for bot_id: {request.bot_id}")
    print(f"[ZOOM_BOT_API] End bot request received for bot_id: {request.bot_id}", flush=True)
    
    try:
        # Find PID file
        backend_dir = Path(__file__).parent.parent
        pid_file = backend_dir / "out" / f"{request.bot_id}.pid"
        
        if not pid_file.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Bot {request.bot_id} not found or already terminated"
            )
        
        # Create stop signal file for graceful shutdown
        stop_flag_file = backend_dir / "out" / f"{request.bot_id}.stop"
        try:
            stop_flag_file.write_text("stop")
            logger.info(f"Created stop signal file for bot {request.bot_id}")
            print(f"[ZOOM_BOT_API] Created stop signal file: {stop_flag_file}", flush=True)
        except Exception as e:
            logger.warning(f"Failed to create stop signal file: {e}")
            print(f"[ZOOM_BOT_API] Failed to create stop signal file: {e}", flush=True)
        
        # Wait a moment for bot to detect signal and cleanup gracefully
        import time
        time.sleep(2)
        
        # Trigger transcription for the recorded audio file and wait for result
        transcript_result = None
        try:
            from workers.meeting.transcribe_worker import process_transcript
            from domains.zoom_resume.transcript.service import TranscriptService
            
            audio_file = backend_dir / "out" / f"{request.bot_id}.opus"
            
            # Check if audio file exists
            if audio_file.exists():
                # Create transcript record in database
                transcript = TranscriptService.create_transcript(
                    db,
                    user_id=current_user.id,
                    audio_url=str(audio_file)
                )
                
                logger.info(f"Starting transcription for bot {request.bot_id} -> transcript_id={transcript.id}")
                print(f"[ZOOM_BOT_API] Starting transcription: {audio_file} -> transcript_id={transcript.id}", flush=True)
                
                # Process synchronously to get live result
                transcript_result = process_transcript(transcript.id)
                
                logger.info(f"Transcription completed: {transcript_result}")
                print(f"[ZOOM_BOT_API] Transcription result: {transcript_result}", flush=True)
            else:
                logger.warning(f"Audio file not found for bot {request.bot_id}: {audio_file}")
                print(f"[ZOOM_BOT_API] Audio file not found: {audio_file}", flush=True)
                
        except Exception as e:
            logger.error(f"Failed to transcribe for bot {request.bot_id}: {e}")
            print(f"[ZOOM_BOT_API] Failed to transcribe: {e}", flush=True)
            # Continue with bot termination even if transcription fails
        
        # Read PID
        pid = int(pid_file.read_text().strip())
        
        # Kill process and all its children (Chrome, chromedriver, etc.)
        try:
            # First, try to find all child processes
            try:
                import psutil
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                
                # Kill children first
                for child in children:
                    try:
                        child.terminate()
                        logger.info(f"Terminated child process {child.pid}")
                    except psutil.NoSuchProcess:
                        pass
                
                # Then kill parent
                parent.terminate()
                logger.info(f"Terminated parent process {pid}")
                
                # Wait for termination
                import time
                time.sleep(1)
                
                # Force kill if still alive
                for child in children:
                    try:
                        if child.is_running():
                            child.kill()
                            logger.info(f"Force killed child process {child.pid}")
                    except psutil.NoSuchProcess:
                        pass
                
                if parent.is_running():
                    parent.kill()
                    logger.info(f"Force killed parent process {pid}")
                    
            except ImportError:
                # Fallback: try killing process group
                logger.warning("psutil not available, using fallback kill method")
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    logger.info(f"Sent SIGTERM to process group {pid}")
                except Exception as e:
                    logger.warning(f"Failed to kill process group: {e}")
                    os.kill(pid, signal.SIGTERM)
                    logger.info(f"Sent SIGTERM to process {pid}")
                    
        except ProcessLookupError:
            # Process already dead
            logger.warning(f"Process {pid} already terminated")
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            # Try force kill
            try:
                os.kill(pid, signal.SIGKILL)
                logger.info(f"Force killed process {pid} with SIGKILL")
            except ProcessLookupError:
                logger.warning(f"Process {pid} already terminated")
        
        # Remove PID file
        pid_file.unlink(missing_ok=True)
        
        response_data = {
            "message": "Bot session terminated successfully",
            "bot_id": request.bot_id,
            "pid": pid
        }
        
        # Add transcript result if available
        if transcript_result:
            response_data["transcript"] = transcript_result
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating bot {request.bot_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to terminate bot: {str(e)}"
        )
