import torch
import torchaudio

model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad"
)

(get_speech_timestamps, _, _, _) = utils

def merge_segments(segments, min_gap=0.4):
    merged = []
    for s in segments:
        if not merged:
            merged.append(s)
        elif s["start"] - merged[-1]["end"] < min_gap:
            merged[-1]["end"] = s["end"]
        else:
            merged.append(s)
    return merged

def extract_speech(input_wav, output_wav):
    wav, sr = torchaudio.load(input_wav)

    speech = get_speech_timestamps(
        wav,
        model,
        sampling_rate=sr
    )

    speech = merge_segments(speech)

    chunks = [wav[:, s["start"]:s["end"]] for s in speech]
    speech_audio = torch.cat(chunks, dim=1)

    torchaudio.save(output_wav, speech_audio, sr)
