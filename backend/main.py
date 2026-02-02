"""
Standalone Bot Zoom Backend
FastAPI application for audio transcription using Whisper
No database, no authentication - just simple file-based storage
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from whisper_service import transcribe_audio_file, get_model_info

# Load environment variables
load_dotenv()

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
TRANSCRIPTS_DIR = Path(os.getenv("TRANSCRIPTS_DIR", "./transcripts"))
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", "./uploads"))

# Create directories
TRANSCRIPTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# FastAPI app
app = FastAPI(
    title="Bot Zoom Transcription API",
    description="Standalone audio transcription service using Whisper",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bot Zoom Transcription API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_info = get_model_info()
    return {
        "status": "healthy",
        "whisper": model_info,
        "storage": {
            "transcripts": str(TRANSCRIPTS_DIR),
            "uploads": str(UPLOADS_DIR)
        }
    }


@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Upload and transcribe an audio file
    
    Returns:
        Transcript with segments and metadata
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix if file.filename else ".webm"
        upload_filename = f"audio_{timestamp}{file_ext}"
        upload_path = UPLOADS_DIR / upload_filename
        
        # Save uploaded file
        async with aiofiles.open(upload_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        print(f"[API] Saved uploaded file: {upload_filename}")
        
        # Transcribe
        result = transcribe_audio_file(str(upload_path))
        
        # Generate transcript ID
        transcript_id = int(datetime.now().timestamp() * 1000)
        
        # Save transcript to JSON file
        transcript_data = {
            "id": transcript_id,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "language": result["language"],
            "model": result["model"],
            "device": result["device"],
            "text": result["text"],
            "segments": result["segments"],
            "audio_file": upload_filename,
        }
        
        transcript_file = TRANSCRIPTS_DIR / f"transcript_{transcript_id}.json"
        async with aiofiles.open(transcript_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(transcript_data, ensure_ascii=False, indent=2))
        
        print(f"[API] Saved transcript: transcript_{transcript_id}.json")
        
        # Clean up uploaded file (optional - comment out to keep files)
        # upload_path.unlink()
        
        return JSONResponse(content=transcript_data)
        
    except Exception as e:
        print(f"[API] Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transcripts/latest")
async def get_latest_transcript():
    """
    Get the most recent transcript
    
    Returns:
        Latest transcript data or 404 if none exist
    """
    try:
        # Find all transcript files
        transcript_files = list(TRANSCRIPTS_DIR.glob("transcript_*.json"))
        
        if not transcript_files:
            raise HTTPException(status_code=404, detail="No transcripts found")
        
        # Get the most recent file
        latest_file = max(transcript_files, key=lambda p: p.stat().st_mtime)
        
        # Read and return
        async with aiofiles.open(latest_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
        
        return JSONResponse(content=data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting latest transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transcripts/{transcript_id}")
async def get_transcript(transcript_id: int):
    """
    Get a specific transcript by ID
    
    Args:
        transcript_id: Transcript ID
        
    Returns:
        Transcript data or 404 if not found
    """
    try:
        transcript_file = TRANSCRIPTS_DIR / f"transcript_{transcript_id}.json"
        
        if not transcript_file.exists():
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        async with aiofiles.open(transcript_file, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
        
        return JSONResponse(content=data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transcripts")
async def list_transcripts(limit: int = 10):
    """
    List all transcripts (most recent first)
    
    Args:
        limit: Maximum number of transcripts to return
        
    Returns:
        List of transcript metadata
    """
    try:
        transcript_files = list(TRANSCRIPTS_DIR.glob("transcript_*.json"))
        
        # Sort by modification time (newest first)
        transcript_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Limit results
        transcript_files = transcript_files[:limit]
        
        # Read metadata from each file
        transcripts = []
        for file in transcript_files:
            async with aiofiles.open(file, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                # Return only metadata, not full segments
                transcripts.append({
                    "id": data["id"],
                    "created_at": data["created_at"],
                    "status": data["status"],
                    "language": data["language"],
                    "model": data["model"],
                    "segment_count": len(data.get("segments", [])),
                })
        
        return JSONResponse(content={"transcripts": transcripts, "total": len(transcripts)})
        
    except Exception as e:
        print(f"[API] Error listing transcripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print(f"[SERVER] Starting on {HOST}:{PORT}")
    print(f"[SERVER] CORS origins: {CORS_ORIGINS}")
    uvicorn.run(app, host=HOST, port=PORT)
