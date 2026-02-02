"""
Background worker for async transcript processing.
Pure domain logic - NO FastAPI imports.
"""
import sys
from pathlib import Path
from typing import Any, Dict

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from database.base import SessionLocal
from domains.zoom_resume.transcript.service import TranscriptService
from domains.zoom_resume.transcript.model import TranscriptStatus
from domains.zoom_resume.transcript.whisper import transcribe_audio_file


def process_transcript(transcript_id: int) -> Dict[str, Any]:
    """
    Process a transcript asynchronously.
    
    This function:
    1. Updates status to PROCESSING
    2. Runs Whisper transcription
    3. Saves results to database
    4. Updates status to DONE or FAILED
    
    Args:
        transcript_id: ID of the transcript to process
        
    Returns:
        Dict with processing result
    """
    db = SessionLocal()
    
    try:
        # Update status to PROCESSING
        transcript = TranscriptService.update_status(
            db,
            transcript_id,
            TranscriptStatus.PROCESSING
        )
        
        print(f"[WORKER] Processing transcript {transcript_id}: {transcript.audio_url}")
        
        # Check if audio file exists
        audio_path = Path(transcript.audio_url)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {transcript.audio_url}")
        
        # Run Whisper transcription
        result = transcribe_audio_file(str(audio_path))
        
        # Save results
        TranscriptService.save_result(
            db,
            transcript_id,
            language=result["language"],
            full_text=result["text"],
            segments=result["segments"]
        )
        
        print(f"[WORKER] Transcript {transcript_id} completed successfully")
        
        return {
            "status": "success",
            "transcript_id": transcript_id,
            "language": result["language"],
            "segments_count": len(result["segments"])
        }
        
    except Exception as e:
        print(f"[WORKER] Error processing transcript {transcript_id}: {str(e)}")
        
        # Update status to FAILED with error message
        TranscriptService.update_status(
            db,
            transcript_id,
            TranscriptStatus.FAILED,
            error_message=str(e)
        )
        
        return {
            "status": "failed",
            "transcript_id": transcript_id,
            "error": str(e)
        }
        
    finally:
        db.close()


def enqueue_transcript(transcript_id: int) -> None:
    """
    Enqueue a transcript for processing.
    
    For development: Uses threading for simple async
    For production: Replace with Celery/RQ/AWS Lambda
    
    Args:
        transcript_id: ID of the transcript to enqueue
    """
    import threading
    
    # Run in background thread (simple async for development)
    thread = threading.Thread(
        target=process_transcript,
        args=(transcript_id,),
        daemon=True
    )
    thread.start()
    
    print(f"[WORKER] Enqueued transcript {transcript_id} for processing")


# Production-ready Celery example (commented out):
# from celery import Celery
# 
# app = Celery('transcribe_worker', broker='redis://localhost:6379/0')
# 
# @app.task(bind=True, max_retries=3)
# def process_transcript_task(self, transcript_id: int):
#     try:
#         return process_transcript(transcript_id)
#     except Exception as exc:
#         raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
