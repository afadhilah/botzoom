from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import engine, Base
from app.api import meetings, transcripts, webhooks
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create directories
Path(settings.RECORDINGS_DIR).mkdir(exist_ok=True)
Path(settings.TRANSCRIPTS_DIR).mkdir(exist_ok=True)

app = FastAPI(
    title="Zoom Meeting Bot API",
    description="Backend for automated meeting recording and transcription",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (recordings, transcripts)
app.mount("/recordings", StaticFiles(directory=settings.RECORDINGS_DIR), name="recordings")
app.mount("/transcripts", StaticFiles(directory=settings.TRANSCRIPTS_DIR), name="transcripts")

# Include routers
app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
app.include_router(transcripts.router, prefix="/api/transcripts", tags=["Transcripts"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
async def root():
    return {
        "message": "Zoom Meeting Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "models": {
            "whisper": settings.WHISPER_MODEL,
            "gpu": settings.USE_GPU
        }
    }