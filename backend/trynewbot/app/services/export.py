
# ============================================================
# FILE 23: app/services/export.py
# ============================================================
import json
from pathlib import Path
from datetime import datetime
from typing import List
from app.models.meeting import Meeting
from app.models.transcript import Transcript, Summary
from app.config import settings

class ExportService:
    """
    Export transcripts to various formats
    """
    
    @staticmethod
    def export_to_txt(meeting: Meeting, transcripts: List[Transcript]) -> Path:
        """Export to TXT file"""
        output_dir = Path(settings.TRANSCRIPTS_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_file = output_dir / f"transcript_{meeting.zoom_meeting_id}_{timestamp}.txt"
        
        with open(txt_file, "w", encoding="utf-8") as f:
            # Header
            f.write("=" * 60 + "\n")
            f.write("MEETING TRANSCRIPT\n")
            f.write(f"Meeting ID: {meeting.zoom_meeting_id}\n")
            f.write(f"Topic: {meeting.meeting_topic or 'N/A'}\n")
            f.write(f"Date: {meeting.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if meeting.recording_duration:
                minutes = meeting.recording_duration // 60
                seconds = meeting.recording_duration % 60
                f.write(f"Duration: {minutes:02d}:{seconds:02d}\n")
            
            f.write("=" * 60 + "\n\n")
            
            # Summary (if exists)
            if meeting.summary:
                f.write("SUMMARY\n")
                f.write("-" * 60 + "\n")
                f.write(meeting.summary.summary_text + "\n")
                f.write("=" * 60 + "\n\n")
            
            # Full transcript
            f.write("FULL TRANSCRIPT\n")
            f.write("=" * 60 + "\n\n")
            
            for t in transcripts:
                timestamp_str = f"{int(t.start_time//60):02d}:{int(t.start_time%60):02d}"
                f.write(f"[{timestamp_str}] {t.speaker_label}: {t.text}\n\n")
        
        return txt_file
    
    @staticmethod
    def export_to_json(
        meeting: Meeting,
        transcripts: List[Transcript],
        summary: Summary = None
    ) -> Path:
        """Export to JSON file"""
        output_dir = Path(settings.TRANSCRIPTS_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = output_dir / f"transcript_{meeting.zoom_meeting_id}_{timestamp}.json"
        
        data = {
            "meeting": {
                "id": str(meeting.id),
                "zoom_meeting_id": meeting.zoom_meeting_id,
                "topic": meeting.meeting_topic,
                "started_at": meeting.started_at.isoformat() if meeting.started_at else None,
                "ended_at": meeting.ended_at.isoformat() if meeting.ended_at else None,
                "duration": meeting.recording_duration
            },
            "summary": {
                "text": summary.summary_text if summary else "",
                "key_points": summary.key_points if summary else [],
                "action_items": summary.action_items if summary else []
            } if summary else None,
            "transcripts": [
                {
                    "speaker": t.speaker_label,
                    "start": t.start_time,
                    "end": t.end_time,
                    "text": t.text,
                    "confidence": t.transcription_confidence
                }
                for t in transcripts
            ]
        }
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return json_file