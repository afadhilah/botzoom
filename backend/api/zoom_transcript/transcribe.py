from faster_whisper import WhisperModel

def transcribe(audio_file):
    model = WhisperModel(
        "large-v3",
        device="cuda",
        compute_type="float16"
    )

    segments, info = model.transcribe(
        audio_file,
        language="id",
        beam_size=5,
        best_of=5,
        temperature=0.0,
        word_timestamps=True,
        vad_filter=False,
        initial_prompt=(
            "Ini adalah transkrip rapat formal berbahasa Indonesia. "
            "Gunakan bahasa jelas dan baku."
        )
    )

    return segments, info
