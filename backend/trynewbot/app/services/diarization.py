

# ============================================================
# FILE 20: app/services/diarization.py
# ============================================================
import torch
from pathlib import Path
from typing import List, Dict
from app.config import settings

class DiarizationService:
    """
    Speaker diarization using pyannote.audio
    """
    
    _pipeline = None
    
    @classmethod
    def get_pipeline(cls):
        """Lazy load diarization pipeline"""
        if cls._pipeline is None:
            if not settings.HUGGINGFACE_TOKEN:
                print("⚠️  No HuggingFace token - skipping diarization")
                return None
            
            try:
                from pyannote.audio import Pipeline
                
                cls._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=settings.HUGGINGFACE_TOKEN
                )
                
                # Use GPU if available
                if settings.USE_GPU and torch.cuda.is_available():
                    cls._pipeline.to(torch.device("cuda"))
                    print("✓ Diarization pipeline loaded (GPU)")
                else:
                    print("✓ Diarization pipeline loaded (CPU)")
                    
            except Exception as e:
                print(f"⚠️  Failed to load diarization: {e}")
                return None
        
        return cls._pipeline
    
    @classmethod
    async def diarize(cls, audio_file: Path) -> List[Dict]:
        """
        Perform speaker diarization
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            List of segments with speaker labels
            [{"start": 0.0, "end": 15.3, "speaker": "SPEAKER_00"}, ...]
        """
        pipeline = cls.get_pipeline()
        
        if pipeline is None:
            # No diarization - return single speaker for whole file
            import soundfile as sf
            audio_info = sf.info(audio_file)
            return [{
                "start": 0.0,
                "end": audio_info.duration,
                "speaker": "SPEAKER_00"
            }]
        
        # Run diarization
        diarization = pipeline(str(audio_file))
        
        # Convert to list of segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        
        # Merge consecutive segments from same speaker
        merged = []
        for seg in segments:
            if merged and merged[-1]["speaker"] == seg["speaker"]:
                # Extend previous segment
                merged[-1]["end"] = seg["end"]
            else:
                merged.append(seg)
        
        return merged
