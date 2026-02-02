FILLERS = [
"eee", "ee", "eh", "em", "emm", "hmm", "hmmm",
"anu", "anu ya", "anu tuh",
"apa ya", "apa namanya", "apa itu", "apa tadi",
]

def remove_fillers(text):
    for f in FILLERS:
        text = text.replace(f, "")
    return text.strip()

def semantic_cleanup(text):
    if not text:
        return ""
    text = text.strip()
    text = text[0].upper() + text[1:]
    if not text.endswith("."):
        text += "."
    return text

def clean_segments(segments):
    cleaned = []

    for s in segments:
        if s.avg_logprob < -1.2:
            continue
        if s.no_speech_prob > 0.6:
            continue

        text = remove_fillers(s.text)
        text = semantic_cleanup(text)

        if text:
            cleaned.append({
                "start": round(s.start, 2),
                "end": round(s.end, 2),
                "text": text
            })

    return cleaned
