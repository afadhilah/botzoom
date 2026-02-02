def qa_coverage(segments, duration):
    spoken = sum(s["end"] - s["start"] for s in segments)
    return spoken / duration

def detect_gaps(segments, threshold=2.0):
    gaps = []
    segments = sorted(segments, key=lambda x: x["start"])

    for i in range(len(segments) - 1):
        gap = segments[i+1]["start"] - segments[i]["end"]
        if gap > threshold:
            gaps.append({
                "gap_start": segments[i]["end"],
                "gap_end": segments[i+1]["start"],
                "duration": gap
            })
    return gaps


def low_confidence_segments(raw_segments):
    suspicious = []
    for s in raw_segments:
        if s.avg_logprob < -1.4:
            suspicious.append({
                "start": s.start,
                "end": s.end,
                "text": s.text
            })
    return suspicious
