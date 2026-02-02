# # backend/main.py
# import os
# import shutil
# import uuid
# from pathlib import Path
# from typing import Any, Dict

# from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session

# from core.config import settings
# from database.base import Base, engine, get_db
# from domains.auth.utils import get_current_active_user
# from domains.user.model import User
# from api.auth import router as auth_router
# from api.users import router as users_router
# from api.zoom_resume.transcripts import router as transcripts_router
# from domains.zoom_resume.transcript.whisper import transcribe_audio_file
# from domains.zoom_resume.transcript.model import Transcript, TranscriptStatus

# # Create database tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     debug=settings.DEBUG
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(auth_router)
# app.include_router(users_router)
# app.include_router(transcripts_router)

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# @app.get("/")
# def root():
#     """Root endpoint."""
#     return {
#         "message": "Meeting Transcript API",
#         "version": settings.APP_VERSION,
#         "docs": "/docs"
#     }



# # Backward compatibility endpoint for old TranscriptMeeting.vue
# @app.post("/transcribe")
# async def transcribe_endpoint(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_active_user)
# ) -> Dict[str, Any]:
#     """
#     Legacy endpoint for transcription.
#     Now saves to database and processes asynchronously.
    
#     For immediate results, use this endpoint.
#     For async processing with status tracking, use POST /transcripts/upload.
#     """
#     from domains.zoom_resume.transcript.service import TranscriptService
#     from workers.meeting.transcribe_worker import enqueue_transcript
    
#     # Validate file extension
#     ext = os.path.splitext(file.filename or "")[1].lower()
#     if ext not in [".wav", ".mp3", ".m4a", ".flac", ".webm", ".ogg"]:
#         raise HTTPException(status_code=400, detail="Unsupported file type")

#     # Save file
#     file_name = f"{uuid.uuid4().hex}{ext}"
#     file_path = UPLOAD_DIR / file_name
#     transcript = None

#     try:
#         # Save uploaded file
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Create transcript record in database
#         transcript = TranscriptService.create_transcript(
#             db,
#             user_id=current_user.id,
#             audio_url=str(file_path)
#         )
        
#         # Update status to PROCESSING
#         TranscriptService.update_status(db, transcript.id, TranscriptStatus.PROCESSING)
        
#         # Enqueue for async processing (background worker)
#         enqueue_transcript(transcript.id)
        
#         # Return immediately with PROCESSING status
#         # Client should poll GET /transcripts/{id}/status for updates
#         return {
#             "transcript_id": transcript.id,
#             "status": "PROCESSING",
#             "message": "Transcription queued. Poll /transcripts/{id}/status for updates.",
#             # Return empty data for backward compatibility
#             "language": None,
#             "text": "",
#             "segments": [],
#             "model": "small",
#             "device": "cpu"
#         }

#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         # Unexpected error - update transcript if exists
#         if transcript:
#             try:
#                 TranscriptService.update_status(
#                     db,
#                     transcript.id,
#                     TranscriptStatus.FAILED,
#                     error_message=str(e)
#                 )
#             except:
#                 pass
        
#         # Clean up file if exists
#         try:
#             if file_path.exists():
#                 file_path.unlink()
#         except:
#             pass
            
#         raise HTTPException(status_code=500, detail=str(e)) from e


# backend/main.py
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.config import settings
from database.base import Base, engine, get_db
from domains.auth.utils import get_current_active_user
from domains.user.model import User
from api.auth import router as auth_router
from api.users import router as users_router
from api.zoom_resume.transcripts import router as transcripts_router
from api.zoom_bot import router as zoom_bot_router
from domains.zoom_resume.transcript.whisper import transcribe_audio_file
from domains.zoom_resume.transcript.model import Transcript, TranscriptStatus

# 
from domains.zoom_resume.transcript.service import TranscriptService
from workers.meeting.transcribe_worker import enqueue_transcript



# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(transcripts_router)
app.include_router(zoom_bot_router)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "Meeting Transcript API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


# ============================================================
# ✅ 2) LEGACY MANUAL UPLOAD (tetap seperti punyamu)
# ============================================================

@app.get("/transcripts/latest")
def get_latest_transcript(db: Session = Depends(get_db)):
    from domains.zoom_resume.transcript.service import TranscriptService

    transcript = TranscriptService.get_latest_transcript(db)

    if not transcript:
        raise HTTPException(status_code=404, detail="No transcripts yet")

    return transcript

@app.post("/transcribe")
async def transcribe_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Legacy endpoint for transcription.
    Now saves to database and processes asynchronously.
    
    For immediate results, use this endpoint.
    For async processing with status tracking, use POST /transcripts/upload.
    """
    from domains.zoom_resume.transcript.service import TranscriptService
    from workers.meeting.transcribe_worker import enqueue_transcript
    
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".wav", ".mp3", ".m4a", ".flac", ".webm", ".ogg"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save file
    file_name = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_name
    transcript = None

    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create transcript record in database
        transcript = TranscriptService.create_transcript(
            db,
            user_id=current_user.id,
            audio_url=str(file_path)
        )
        
        # Update status to PROCESSING
        TranscriptService.update_status(db, transcript.id, TranscriptStatus.PROCESSING)
        
        # Enqueue for async processing (background worker)
        enqueue_transcript(transcript.id)
        
        # Return immediately with PROCESSING status
        # Client should poll GET /transcripts/{id}/status for updates
        return {
            "transcript_id": transcript.id,
            "status": "PROCESSING",
            "message": "Transcription queued. Poll /transcripts/{id}/status for updates.",
            # Return empty data for backward compatibility
            "language": None,
            "text": "",
            "segments": [],
            "model": "small",
            "device": "cpu"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected error - update transcript if exists
        if transcript:
            try:
                TranscriptService.update_status(
                    db,
                    transcript.id,
                    TranscriptStatus.FAILED,
                    error_message=str(e)
                )
            except:
                pass
        
        # Clean up file if exists
        try:
            if file_path.exists():
                file_path.unlink()
        except:
            pass
            
        raise HTTPException(status_code=500, detail=str(e)) from e
# 3 NODE ZOOM BOT UPLOAD (local recording)
# ============================================================

@app.post("/meetings/upload")
async def upload_meeting_audio(
    audio: UploadFile = File(...),
    meeting_id: str = File(...),
    db: Session = Depends(get_db),
):
    """
    Endpoint untuk Node.js Zoom Bot
    - terima audio hasil puppeteer + ffmpeg
    - simpan ke DB
    - enqueue worker transkripsi
    """

    # validate extension
    ext = os.path.splitext(audio.filename or "")[1].lower()
    if ext not in [".wav", ".mp3", ".m4a", ".flac"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # generate filename
    file_name = f"meeting_{meeting_id}_{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / file_name

    transcript = None

    try:
        # save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # create transcript DB entry
        transcript = TranscriptService.create_transcript(
            db=db,
            user_id=1,  # meeting bot (no user)
            audio_url=str(file_path)
        )

        # update status
        TranscriptService.update_status(
            db,
            transcript.id,
            TranscriptStatus.PROCESSING
        )

        # enqueue async worker
        enqueue_transcript(transcript.id)

        return {
            "status": "queued",
            "source": "zoom-bot",
            "meeting_id": meeting_id,
            "transcript_id": transcript.id,
        }

    except Exception as e:
        if transcript:
            TranscriptService.update_status(
                db,
                transcript.id,
                TranscriptStatus.FAILED,
                error_message=str(e)
            )

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(status_code=500, detail=str(e))