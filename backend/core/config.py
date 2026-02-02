"""
Unified configuration for Meeting Transcript & Zoom Bot API
Merged from core/config.py and trynewbot/app/config.py
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import json
from pathlib import Path


class Settings(BaseSettings):
    # ============================================================
    # App Configuration
    # ============================================================
    APP_NAME: str = "Meeting Transcript & Zoom Bot API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # ============================================================
    # Database Configuration
    # ============================================================
    DATABASE_URL: str
    
    # ============================================================
    # JWT & Authentication
    # ============================================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ============================================================
    # Security Configuration
    # ============================================================
    PASSWORD_MIN_LENGTH: int = 8
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    
    # ============================================================
    # CORS Configuration
    # ============================================================
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    ALLOWED_HOSTS: str = '["*"]'
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Parse ALLOWED_HOSTS from JSON string"""
        try:
            return json.loads(self.ALLOWED_HOSTS)
        except (json.JSONDecodeError, TypeError):
            return ["*"]
    
    
    # ============================================================
    # Storage Configuration
    # ============================================================
    STORAGE_TYPE: str = "local"
    RECORDINGS_DIR: str = "./recordings"
    TRANSCRIPTS_DIR: str = "./transcripts"
    UPLOADS_DIR: str = "./uploads"
    
    # ============================================================
    # AI/ML Model Configuration
    # ============================================================
    WHISPER_MODEL: str = "medium"
    USE_GPU: bool = True
    GPU_MEMORY_FRACTION: float = 0.9
    
    # ============================================================
    # LLM Configuration
    # ============================================================
    LLM_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # openai, anthropic, etc.
    
    # ============================================================
    # Diarization Configuration (Speaker Identification)
    # ============================================================
    ENABLE_DIARIZATION: bool = True
    DIARIZATION_MODEL: str = "pyannote/speaker-diarization-3.0"
    HUGGINGFACE_TOKEN: Optional[str] = None
    MAX_SPEAKERS: int = 10
    
    # ============================================================
    # Audio Processing Configuration
    # ============================================================
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_DURATION: int = 30  # seconds
    
    # ============================================================
    # Processing Configuration
    # ============================================================
    ENABLE_TRANSCRIPTION: bool = True
    ENABLE_SUMMARIZATION: bool = True
    ENABLE_DIARIZATION: bool = True
    
    # ============================================================
    # Webhook Configuration
    # ============================================================
    WEBHOOK_VERIFY_TOKEN: Optional[str] = None
    
    # ============================================================
    # Email Configuration (SMTP)
    # ============================================================
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = 587
    MAIL_SERVER: Optional[str] = None
    MAIL_FROM_NAME: str = "Meeting Transcript System"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()

# Create directories if they don't exist
Path(settings.RECORDINGS_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TRANSCRIPTS_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

