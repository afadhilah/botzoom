# backend/api/dummy.py
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    content = await file.read()
    size_kb = len(content) / 1024
    print(f"[LOG] Received file: {file.filename}, size={size_kb:.1f} KB")

    return {
        "status": "ok",
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "speaker": "Speaker LOCAL",
                "text": "Local dummy transcript OK",
            }
        ],
    }
