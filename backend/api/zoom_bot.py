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
        
        logger.info(f"Started Zoom bot process {process.pid} (UUID: {bot_uuid}) for meeting: {meeting_link}")
        
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
        
        # Read PID first
        pid = int(pid_file.read_text().strip())
        
        # Step 1: Try graceful shutdown with stop signal
        stop_flag_file = backend_dir / "out" / f"{request.bot_id}.stop"
        try:
            stop_flag_file.write_text("stop")
            logger.info(f"Created stop signal file for bot {request.bot_id}")
            print(f"[ZOOM_BOT_API] Created stop signal, waiting for graceful exit...", flush=True)
        except Exception as e:
            logger.warning(f"Failed to create stop signal file: {e}")
        
        # Step 2: Wait for graceful shutdown (max 5 seconds)
        import time
        max_wait = 5
        wait_interval = 0.5
        elapsed = 0
        
        try:
            import psutil
            process_alive = True
            while elapsed < max_wait and process_alive:
                try:
                    proc = psutil.Process(pid)
                    if not proc.is_running():
                        process_alive = False
                        logger.info(f"Process {pid} exited gracefully after {elapsed}s")
                        print(f"[ZOOM_BOT_API] Bot exited gracefully in {elapsed}s", flush=True)
                        break
                except psutil.NoSuchProcess:
                    process_alive = False
                    break
                
                time.sleep(wait_interval)
                elapsed += wait_interval
            
            # Step 3: Force kill if still alive
            if process_alive:
                logger.warning(f"Process {pid} didn't exit gracefully, force killing...")
                print(f"[ZOOM_BOT_API] Timeout, force killing process {pid}...", flush=True)
                
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                
                # Kill all children
                for child in children:
                    try:
                        child.kill()
                        logger.info(f"Killed child process {child.pid}")
                    except psutil.NoSuchProcess:
                        pass
                
                # Kill parent
                parent.kill()
                logger.info(f"Killed parent process {pid}")
                
        except ImportError:
            # Fallback without psutil - just wait and kill
            logger.warning("psutil not available, using basic kill after timeout")
            time.sleep(max_wait)
            import signal
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except Exception:
                os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            logger.info(f"Process {pid} already terminated")
        
        # Clean up files
        pid_file.unlink(missing_ok=True)
        stop_flag_file.unlink(missing_ok=True)
        
        logger.info(f"Bot {request.bot_id} terminated successfully")
        print(f"[ZOOM_BOT_API] Bot terminated, starting transcription...", flush=True)
        
        # Trigger transcription asynchronously (enqueue for background processing)
        transcript_result = None
        try:
            from domains.zoom_resume.transcript.service import TranscriptService
            from workers.meeting.transcribe_worker import enqueue_transcript
            
            audio_file = backend_dir / "out" / f"{request.bot_id}.opus"
            
            # Check if audio file exists
            if audio_file.exists():
                # Create transcript record in database with PENDING status
                transcript = TranscriptService.create_transcript(
                    db,
                    user_id=current_user.id,
                    audio_url=str(audio_file)
                )
                
                # Enqueue worker for background transcription processing
                enqueue_transcript(transcript.id)
                
                logger.info(f"Enqueued transcription for bot {request.bot_id} -> transcript_id={transcript.id}")
                print(f"[ZOOM_BOT_API] Enqueued transcription: transcript_id={transcript.id}", flush=True)
                
                # Return transcript info immediately (client will poll for status)
                transcript_result = {
                    'status': 'enqueued',
                    'transcript_id': transcript.id,
                    'language': None,
                    'segments_count': 0
                }
            else:
                logger.warning(f"Audio file not found for bot {request.bot_id}: {audio_file}")
                print(f"[ZOOM_BOT_API] Audio file not found: {audio_file}", flush=True)
                
        except Exception as e:
            logger.error(f"Failed to enqueue transcription for bot {request.bot_id}: {e}")
            print(f"[ZOOM_BOT_API] Failed to enqueue transcription: {e}", flush=True)
            # Continue even if transcription fails
        
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
