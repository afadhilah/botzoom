def assign_speaker(segments, speakers):
    for seg in segments:
        seg["speaker"] = "UNKNOWN"

        for sp in speakers:
            overlap = min(seg["end"], sp["end"]) - max(seg["start"], sp["start"])
            if overlap > 0:
                seg["speaker"] = sp["speaker"]
                break
    return segments
