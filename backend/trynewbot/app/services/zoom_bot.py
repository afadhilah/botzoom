# # ============================================================
# # FILE 19: app/services/zoom_bot.py
# # ============================================================
# import os
# from pathlib import Path
# from datetime import datetime
# from sqlalchemy.orm import Session
# from app.models.meeting import Meeting, Transcript, Summary
# from app.services.transcription import TranscriptionService
# from app.services.diarization import DiarizationService
# from app.services.summarization import SummarizationService
# from app.config import settings

# class ZoomBotService:
#     """
#     Main service for Zoom bot functionality
#     """
    
#     @staticmethod
#     async def join_and_record(meeting_id: str, zoom_meeting_id: str, db: Session):
#         """
#         Join Zoom meeting and start recording
        
#         Args:
#             meeting_id: Database meeting ID
#             zoom_meeting_id: Zoom meeting ID/URL
#             db: Database session
#         """
#         meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
#         try:
#             print(f"[{meeting_id}] Starting bot for Zoom meeting: {zoom_meeting_id}")
            
#             # Update status
#             meeting.status = "joining"
#             meeting.started_at = datetime.utcnow()
#             db.commit()
            
#             # TODO: Implement actual Zoom SDK join
#             # This requires Zoom SDK setup with OAuth
#             # For now, we'll simulate the process
            
#             print(f"[{meeting_id}] Bot joined meeting")
            
#             # Create recording path
#             recording_path = Path(settings.RECORDINGS_DIR) / f"{meeting_id}.wav"
            
#             # Simulate recording (in production, this would use Zoom SDK audio capture)
#             meeting.status = "recording"
#             meeting.recording_file_path = str(recording_path)
#             db.commit()
            
#             print(f"[{meeting_id}] Recording started: {recording_path.name}")
            
#             # In production, this would wait for meeting to end via webhook
#             # For demo, we'll simulate a short meeting
#             await asyncio.sleep(5)  # Simulate 5 second meeting
            
#             # Meeting ended
#             meeting.status = "processing"
#             meeting.ended_at = datetime.utcnow()
#             meeting.recording_duration = 5  # seconds
#             db.commit()
            
#             print(f"[{meeting_id}] Meeting ended, starting processing")
            
#             # Start processing
#             await ZoomBotService.process_recording(meeting_id, db)
            
#         except Exception as e:
#             print(f"[{meeting_id}] Error in join_and_record: {e}")
#             meeting.status = "failed"
#             db.commit()
#             raise
    
#     @staticmethod
#     async def process_recording(meeting_id: str, db: Session):
#         """
#         Process recorded meeting: diarization -> transcription -> summary
        
#         Args:
#             meeting_id: Database meeting ID
#             db: Database session
#         """
#         meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
#         if not meeting:
#             print(f"[{meeting_id}] Meeting not found")
#             return
        
#         try:
#             print(f"[{meeting_id}] Starting processing pipeline")
            
#             meeting.processing_started_at = datetime.utcnow()
#             meeting.status = "processing"
#             db.commit()
            
#             audio_file = Path(meeting.recording_file_path)
            
#             if not audio_file.exists():
#                 raise FileNotFoundError(f"Recording file not found: {audio_file}")
            
#             # Step 1: Speaker Diarization
#             print(f"[{meeting_id}] Step 1/3: Diarization")
#             segments = await DiarizationService.diarize(audio_file)
#             print(f"[{meeting_id}] Found {len(segments)} segments")
            
#             # Step 2: Transcription
#             print(f"[{meeting_id}] Step 2/3: Transcription")
#             transcripts = await TranscriptionService.transcribe_segments(
#                 audio_file, segments
#             )
#             print(f"[{meeting_id}] Transcribed {len(transcripts)} segments")
            
#             # Save transcripts to database
#             for t in transcripts:
#                 db_transcript = Transcript(
#                     meeting_id=meeting.id,
#                     speaker_label=t["speaker"],
#                     start_time=t["start"],
#                     end_time=t["end"],
#                     text=t["text"],
#                     transcription_confidence=t.get("confidence", 0.0)
#                 )
#                 db.add(db_transcript)
            
#             db.commit()
            
#             # Step 3: Generate Summary
#             print(f"[{meeting_id}] Step 3/3: Summarization")
#             summary_result = await SummarizationService.generate_summary(transcripts)
            
#             # Save summary
#             db_summary = Summary(
#                 meeting_id=meeting.id,
#                 summary_text=summary_result["summary"],
#                 total_speakers=len(set(t["speaker"] for t in transcripts)),
#                 total_segments=len(transcripts),
#                 key_points=summary_result.get("key_points", []),
#                 action_items=summary_result.get("action_items", [])
#             )
#             db.add(db_summary)
            
#             # Update meeting status
#             meeting.status = "completed"
#             meeting.processing_completed_at = datetime.utcnow()
            
#             db.commit()
            
#             print(f"[{meeting_id}] Processing completed successfully!")
            
#         except Exception as e:
#             print(f"[{meeting_id}] Error processing meeting: {e}")
#             meeting.status = "failed"
#             db.commit()
#             raise

import subprocess
import time
import jwt

class ZoomBotService:

    @staticmethod
    def _generate_sdk_jwt():
        payload = {
            "appKey": settings.ZOOM_SDK_KEY,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "tokenExp": int(time.time()) + 3600,
        }
        return jwt.encode(
            payload,
            settings.ZOOM_SDK_SECRET,
            algorithm="HS256"
        )

    @staticmethod
    async def join_and_record(meeting_id: str, zoom_meeting_id: str, db: Session):
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise ValueError("Meeting not found")

        recording_path = Path(settings.RECORDINGS_DIR) / f"{meeting_id}.wav"

        meeting.status = "joining"
        meeting.started_at = datetime.utcnow()
        meeting.recording_file_path = str(recording_path)
        db.commit()

        jwt_token = ZoomBotService._generate_sdk_jwt()

        cmd = [
            settings.ZOOM_BOT_BINARY,
            "--meeting-id", zoom_meeting_id,
            "--jwt", jwt_token,
            "--output", str(recording_path),
            "--bot-name", "AI Minutes Bot"
        ]

        process = subprocess.Popen(cmd)

        meeting.status = "recording"
        db.commit()

        # ❗ JANGAN BLOCKING
        # SDK bot akan exit sendiri saat meeting end
        print(f"[{meeting_id}] Zoom SDK bot started (pid={process.pid})")
