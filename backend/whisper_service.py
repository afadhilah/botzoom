"""
Whisper Transcription Service
Simplified version for standalone bot_zoom application
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import whisper

# Configuration from environment or defaults
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
FORCE_LANGUAGE: Optional[str] = None  # Set to "id" or "en" to force language

# Initialize model on startup
_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = whisper.load_model(WHISPER_MODEL_NAME, device=_device)
print(f"[WHISPER] Loaded model '{WHISPER_MODEL_NAME}' on device: {_device}")


def transcribe_audio_file(path: str) -> Dict[str, Any]:
    """
    Transcribe an audio file using Whisper.
    
    Args:
        path: Path to audio file
        
    Returns:
        Dictionary containing:
        - audio_file: Original file path
        - model: Whisper model used
        - device: Device used (cuda/cpu)
        - language: Detected language
        - text: Full transcript text
        - segments: List of transcript segments with timestamps
    """
    audio_path = Path(path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[WHISPER] Processing audio file: {audio_path.name}")

    # Transcription options
    kwargs: Dict[str, Any] = {
        "fp16": True if _device == "cuda" else False,
        "verbose": False,
    }
    if FORCE_LANGUAGE is not None:
        kwargs["language"] = FORCE_LANGUAGE

    # Transcribe
    result = _model.transcribe(str(audio_path), **kwargs)

    # Extract results
    language = result.get("language", FORCE_LANGUAGE or "unknown")
    text_full = result.get("text", "").strip()
    segments_raw = result.get("segments", [])

    # Format segments for frontend
    segments: List[Dict[str, Any]] = []
    for seg in segments_raw:
        segments.append({
            "id": int(seg.get("id", 0)),
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text": seg.get("text", "").strip(),
            "speaker": "Speaker 1",  # No diarization in this simple version
        })

    print(f"[WHISPER] Transcription complete: {len(segments)} segments, language: {language}")

    return {
        "audio_file": str(audio_path),
        "model": WHISPER_MODEL_NAME,
        "device": _device,
        "language": language,
        "text": text_full,
        "segments": segments,
    }


def get_model_info() -> Dict[str, str]:
    """Get information about the loaded Whisper model."""
    return {
        "model": WHISPER_MODEL_NAME,
        "device": _device,
        "status": "ready"
    }
