
# ============================================================
# FILE 21: app/services/transcription.py
# ============================================================
import whisper
import torch
import soundfile as sf
from pathlib import Path
from typing import List, Dict
from app.config import settings

class TranscriptionService:
    """
    Speech-to-text using OpenAI Whisper
    """
    
    _model = None
    
    @classmethod
    def get_model(cls):
        """Lazy load Whisper model"""
        if cls._model is None:
            print(f"Loading Whisper model: {settings.WHISPER_MODEL}")
            cls._model = whisper.load_model(settings.WHISPER_MODEL)
            print("✓ Whisper model loaded")
        return cls._model
    
    @classmethod
    async def transcribe_segments(
        cls,
        audio_file: Path,
        segments: List[Dict]
    ) -> List[Dict]:
        """
        Transcribe each speaker segment
        
        Args:
            audio_file: Path to audio file
            segments: List of speaker segments from diarization
            
        Returns:
            List with transcripts
            [{"speaker": "...", "start": 0.0, "end": 15.3, "text": "...", "confidence": 0.95}, ...]
        """
        model = cls.get_model()
        
        # Load full audio
        audio, sr = sf.read(audio_file)
        
        results = []
        total = len(segments)
        
        for i, segment in enumerate(segments, 1):
            print(f"Transcribing segment {i}/{total}", end="\r")
            
            # Extract segment audio
            start_sample = int(segment["start"] * sr)
            end_sample = int(segment["end"] * sr)
            segment_audio = audio[start_sample:end_sample]
            
            # Transcribe
            result = model.transcribe(
                segment_audio,
                language="id",  # Indonesian
                fp16=settings.USE_GPU and torch.cuda.is_available()
            )
            
            # Calculate average confidence from word-level data
            confidence = 0.0
            if "segments" in result and result["segments"]:
                confidences = [
                    s.get("no_speech_prob", 0.0)
                    for s in result["segments"]
                ]
                confidence = 1.0 - (sum(confidences) / len(confidences))
            
            results.append({
                "speaker": segment["speaker"],
                "start": segment["start"],
                "end": segment["end"],
                "text": result["text"].strip(),
                "confidence": round(confidence, 2)
            })
        
        print(f"\nTranscribed {len(results)} segments")
        return results
