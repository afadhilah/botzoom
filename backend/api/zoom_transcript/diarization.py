from pyannote.audio import Pipeline
import torch

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token="HF_TOKEN"
)

pipeline.to(torch.device("cuda"))

def diarize(audio_file):
    diarization = pipeline(audio_file)

    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return speakers
