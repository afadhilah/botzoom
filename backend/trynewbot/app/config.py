from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # API Keys
    HUGGINGFACE_TOKEN: str = None
    ZOOM_CLIENT_ID: str = None
    ZOOM_CLIENT_SECRET: str = None
    # config real to zoom SDK
    ZOOM_SDK_KEY=...
    ZOOM_SDK_SECRET=...
    ZOOM_BOT_BINARY="/opt/zoom-bot/zoom_bot"
    RECORDINGS_DIR="/data/recordings"

    
    # App Settings
    SECRET_KEY: str
    DEBUG: bool = False
    ALLOWED_HOSTS: str = '["*"]'
    
    # Storage
    STORAGE_TYPE: str = "local"
    RECORDINGS_DIR: str = "./recordings"
    TRANSCRIPTS_DIR: str = "./transcripts"
    
    # AI Models
    WHISPER_MODEL: str = "medium"
    USE_GPU: bool = True
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        return json.loads(self.ALLOWED_HOSTS)
    
    class Config:
        env_file = ".env"

settings = Settings()