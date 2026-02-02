# Dummy WhisperX Service for Testing
import os
try:
    import whisperx
except ImportError:
    whisperx = None

def transcribe_audio(audio_path: str) -> dict:
    """
    Transkripsi audio menggunakan WhisperX jika tersedia, fallback ke dummy jika gagal.
    """
    if not os.path.isfile(audio_path):
        return {"error": f"File audio tidak ditemukan: {audio_path}"}

    if whisperx is None:
        # Fallback dummy jika whisperx tidak terinstall
        return {
            "audio_path": audio_path,
            "file_size": os.path.getsize(audio_path),
            "transcript": "(Dummy) Ini adalah hasil transkripsi dummy dari WhisperX.",
            "language": "id",
            "segments": [
                {"start": 0, "end": 5, "text": "Halo semua, selamat datang."},
                {"start": 6, "end": 10, "text": "Ini adalah meeting transcript."}
            ]
        }

    # Kode asli WhisperX
    try:
        # Model default: large-v2, device: cpu (atau ganti ke cuda jika ada GPU)
        model = whisperx.load_model("large-v2", device="cpu")
        audio = whisperx.load_audio(audio_path)
        result = model.transcribe(audio)
        return {
            "audio_path": audio_path,
            "file_size": os.path.getsize(audio_path),
            "transcript": result.get("text", ""),
            "language": result.get("language", ""),
            "segments": result.get("segments", [])
        }
    except Exception as e:
        return {"error": f"WhisperX error: {str(e)}"}
