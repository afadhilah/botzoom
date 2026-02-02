import json
from zoom_audio import download_zoom_audio
from audio_preprocess import preprocess_audio
from vad import extract_speech
from transcribe import transcribe
from cleanup import clean_segments
from diarization import diarize
from speaker_align import assign_speaker
from qualityasurance import qa_coverage, detect_gaps, low_confidence_segments

#harus integrasi ke zoom
ZOOM_TOKEN = "YOUR_ZOOM_TOKEN"
DOWNLOAD_URL = "ZOOM_AUDIO_DOWNLOAD_URL"

def main():
    raw_audio = "meeting.m4a"
    clean_audio = "clean.wav"
    speech_audio = "speech.wav"

    download_zoom_audio(DOWNLOAD_URL, ZOOM_TOKEN, raw_audio)
    preprocess_audio(raw_audio, clean_audio)
    extract_speech(clean_audio, speech_audio)

    segments, info = transcribe(speech_audio)
    final_transcript = clean_segments(segments)

    with open("output/transcript.json", "w", encoding="utf-8") as f:
        json.dump(final_transcript, f, indent=2, ensure_ascii=False)

    coverage = sum(
        s["end"] - s["start"] for s in final_transcript
    ) / info.duration

    print(f"Transcript coverage: {coverage:.2%}")

    segments, info = transcribe(speech_audio)
    cleaned = clean_segments(segments)

    speakers = diarize(speech_audio)
    final_transcript = assign_speaker(cleaned, speakers)

    qa = {
        "coverage": qa_coverage(final_transcript, info.duration),
        "missing_speech_segments": detect_gaps(final_transcript),
        "low_confidence_segments": low_confidence_segments(segments)
    }

    with open("output/transcript.json", "w", encoding="utf-8") as f:
        json.dump(final_transcript, f, indent=2, ensure_ascii=False)

    with open("output/qa_report.json", "w", encoding="utf-8") as f:
        json.dump(qa, f, indent=2)

if __name__ == "__main__":
    main()
