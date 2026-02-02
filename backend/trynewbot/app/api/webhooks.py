# from fastapi import APIRouter, Request, HTTPException
# from datetime import datetime
# from app.models.meeting import Meeting
# from app.database import SessionLocal

# router = APIRouter()

# @router.post("/zoom/meeting-ended")
# async def zoom_meeting_ended(request: Request):
#     """
#     Webhook endpoint for Zoom meeting ended event
    
#     Zoom will call this when a meeting ends
#     Configure in Zoom App settings
#     """
#     payload = await request.json()
    
#     # Verify webhook (implement HMAC verification in production)
#     # verification_token = request.headers.get("x-zm-signature")
    
#     event_type = payload.get("event")
    
#     if event_type == "meeting.ended":
#         meeting_id = payload["payload"]["object"]["id"]
        
#         db = SessionLocal()
#         try:
#             # Find meeting by zoom_meeting_id
#             meeting = db.query(Meeting).filter(
#                 Meeting.zoom_meeting_id == meeting_id
#             ).first()
            
#             if meeting:
#                 meeting.status = "processing"
#                 meeting.ended_at = datetime.utcnow()
#                 db.commit()
                
#                 # Trigger processing
#                 from app.services.zoom_bot import ZoomBotService
#                 await ZoomBotService.process_recording(str(meeting.id), db)
                
#                 return {"status": "success", "message": "Processing started"}
            
#             return {"status": "warning", "message": "Meeting not found in database"}
            
#         finally:
#             db.close()
    
#     return {"status": "ignored", "event": event_type}


@router.post("/zoom/meeting-ended")
async def zoom_meeting_ended(request: Request):
    payload = await request.json()

    if payload.get("event") != "meeting.ended":
        return {"status": "ignored"}

    zoom_id = payload["payload"]["object"]["id"]

    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(
            Meeting.zoom_meeting_id == zoom_id
        ).first()

        if not meeting:
            return {"status": "not_found"}

        if meeting.status == "completed":
            return {"status": "already_done"}

        meeting.status = "processing"
        meeting.ended_at = datetime.utcnow()
        db.commit()

        from app.services.zoom_bot import ZoomBotService
        await ZoomBotService.process_recording(str(meeting.id), db)

        return {"status": "processing_started"}

    finally:
        db.close()
