# backend/services/whisper_small_service.py
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import whisper

WHISPER_MODEL_NAME = "small"
FORCE_LANGUAGE: Optional[str] = "id"  # Paksa bahasa Indonesia

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = whisper.load_model(WHISPER_MODEL_NAME, device=_device)
print(f"[WHISPER] Loaded model '{WHISPER_MODEL_NAME}' on device: {_device}")


def transcribe_audio_file(path: str) -> Dict[str, Any]:
    """Transkrip satu file audio, return dict siap kirim ke frontend."""
    import subprocess
    import tempfile
    
    audio_path = Path(path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Preprocess audio with ffmpeg to fix compatibility issues
    # Convert to 16kHz mono WAV (Whisper's preferred format)
    # DISABLED: User requested to process webm directly without conversion
    """
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            converted_path = tmp_file.name
        
        # Use ffmpeg to convert audio with better compatibility
        result = subprocess.run([
            'ffmpeg', '-i', str(audio_path),
            '-ar', '16000',      # 16kHz sample rate
            '-ac', '1',          # mono
            '-acodec', 'pcm_s16le',  # PCM 16-bit encoding
            '-y',                # overwrite
            converted_path
        ], check=True, capture_output=True, text=True)
        
        # Use converted file for transcription
        transcribe_path = converted_path
        cleanup_converted = True
        print(f"[WHISPER] Converted {audio_path} to WAV format")
    except subprocess.CalledProcessError as e:
        print(f"[WHISPER] ffmpeg conversion failed: {e.stderr}")
        # Try original file if conversion fails
        transcribe_path = str(audio_path)
        cleanup_converted = False
    except FileNotFoundError:
        # ffmpeg not available, use original file
        print("[WHISPER] ffmpeg not available, using original audio file")
        transcribe_path = str(audio_path)
        cleanup_converted = False
    """
    
    # Use original file directly (no conversion)
    transcribe_path = str(audio_path)
    cleanup_converted = False
    print(f"[WHISPER] Processing audio file directly: {audio_path}")

    try:
        kwargs: Dict[str, Any] = {
            "fp16": True if _device == "cuda" else False,
            "verbose": False,
        }
        if FORCE_LANGUAGE is not None:
            kwargs["language"] = FORCE_LANGUAGE

        result = _model.transcribe(transcribe_path, **kwargs)

        language = result.get("language", FORCE_LANGUAGE or "unknown")
        text_full = result.get("text", "").strip()
        segments_raw = result.get("segments", [])

        segments: List[Dict[str, Any]] = []
        for seg in segments_raw:
            segments.append(
                {
                    "id": int(seg.get("id", 0)),
                    "start": float(seg.get("start", 0.0)),
                    "end": float(seg.get("end", 0.0)),
                    "text": seg.get("text", "").strip(),
                    # belum ada diarization → kasih default speaker
                    "speaker": "Speaker 1",
                }
            )

        return {
            "audio_file": str(audio_path),
            "model": WHISPER_MODEL_NAME,
            "device": _device,
            "language": language,
            "text": text_full,
            "segments": segments,
        }
    finally:
        # Cleanup converted file
        if cleanup_converted:
            try:
                Path(converted_path).unlink()
            except:
                pass
