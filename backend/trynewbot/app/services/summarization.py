
# ============================================================
# FILE 22: app/services/summarization.py
# ============================================================
import torch
from typing import List, Dict
from transformers import pipeline
from app.config import settings

class SummarizationService:
    """
    Meeting summarization using IndoBERT
    """
    
    _summarizer = None
    
    @classmethod
    def get_summarizer(cls):
        """Lazy load summarization model"""
        if cls._summarizer is None:
            try:
                cls._summarizer = pipeline(
                    "summarization",
                    model="indobenchmark/indobart-v2",
                    device=0 if (settings.USE_GPU and torch.cuda.is_available()) else -1
                )
                print("✓ Summarization model loaded")
            except Exception as e:
                print(f"⚠️  Failed to load summarizer: {e}")
                return None
        
        return cls._summarizer
    
    @classmethod
    async def generate_summary(cls, transcripts: List[Dict]) -> Dict:
        """
        Generate meeting summary
        
        Args:
            transcripts: List of transcript segments
            
        Returns:
            Dict with summary and metadata
            {
                "summary": "...",
                "key_points": [...],
                "action_items": [...]
            }
        """
        # Combine all text
        full_text = " ".join([t["text"] for t in transcripts])
        
        summarizer = cls.get_summarizer()
        
        if summarizer and len(full_text) > 100:
            try:
                # Limit input length (IndoBART max = 1024 tokens)
                max_input = 900
                summary = summarizer(
                    full_text[:max_input],
                    max_length=150,
                    min_length=30,
                    do_sample=False
                )[0]["summary_text"]
                
            except Exception as e:
                print(f"⚠️  Summarization failed: {e}")
                summary = cls._fallback_summary(transcripts)
        else:
            summary = cls._fallback_summary(transcripts)
        
        # Extract key points (simple heuristic: look for questions and statements)
        key_points = cls._extract_key_points(transcripts)
        
        # Extract action items (simple heuristic: look for "akan", "harus", etc.)
        action_items = cls._extract_action_items(transcripts)
        
        return {
            "summary": summary,
            "key_points": key_points,
            "action_items": action_items
        }
    
    @staticmethod
    def _fallback_summary(transcripts: List[Dict]) -> str:
        """Simple summary when AI model fails"""
        num_speakers = len(set(t["speaker"] for t in transcripts))
        num_segments = len(transcripts)
        duration = transcripts[-1]["end"] if transcripts else 0
        minutes = int(duration // 60)
        
        return (
            f"Meeting berlangsung selama {minutes} menit dengan {num_speakers} pembicara. "
            f"Total {num_segments} segmen percakapan tercatat."
        )
    
    @staticmethod
    def _extract_key_points(transcripts: List[Dict]) -> List[str]:
        """Extract key discussion points"""
        key_points = []
        keywords = ["penting", "utama", "kesimpulan", "keputusan", "hasil"]
        
        for t in transcripts:
            text_lower = t["text"].lower()
            if any(keyword in text_lower for keyword in keywords):
                key_points.append(f"{t['speaker']}: {t['text'][:100]}...")
        
        return key_points[:5]  # Top 5 key points
    
    @staticmethod
    def _extract_action_items(transcripts: List[Dict]) -> List[Dict]:
        """Extract action items"""
        action_items = []
        keywords = ["akan", "harus", "perlu", "sebaiknya", "tugas"]
        
        for t in transcripts:
            text_lower = t["text"].lower()
            if any(keyword in text_lower for keyword in keywords):
                action_items.append({
                    "speaker": t["speaker"],
                    "text": t["text"],
                    "timestamp": f"{int(t['start']//60):02d}:{int(t['start']%60):02d}"
                })
        
        return action_items[:10]  # Top 10 action items
