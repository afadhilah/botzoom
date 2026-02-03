import os
import json
from pathlib import Path
from typing import List, Dict, Any

import torch
import whisper


# ========= KONFIGURASI =========

# Folder input audio
AUDIO_DIR = r"/home/cak-seno/botzoom/storage/audio"  # ganti sesuai folder lu

# Folder output transcript JSON
OUTPUT_DIR = r"/home/cak-seno/botzoom/storage/transcripts_openai"

# Model Whisper yang dipakai
WHISPER_MODEL_NAME = "small"  # "tiny" | "base" | "small" | "medium" | "large"

# Deteksi bahasa otomatis (True) atau paksa bahasa tertentu, misal "id"
FORCE_LANGUAGE = None  # contoh: "id" kalau mau paksa Indonesia

# ================================


def list_audio_files(folder: str) -> List[Path]:
    """Ambil semua file audio dari folder."""
    exts = {".wav", ".mp3", ".m4a", ".flac", ".opus", ".aac"}
    # exts = {".mp3"}
    p = Path(folder)
    if not p.exists():
        print(f"[WARN] Folder audio belum ada: {folder}")
        return []
    return sorted([f for f in p.iterdir() if f.is_file() and f.suffix.lower() in exts])


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def main() -> None:
    # Pilih device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using device: {device}")

    ensure_dir(OUTPUT_DIR)

    audio_files = list_audio_files(AUDIO_DIR)
    if not audio_files:
        print(f"[WARN] Tidak ada file audio di: {AUDIO_DIR}")
        return

    print(f"[INFO] Ditemukan {len(audio_files)} file audio.")
    for f in audio_files:
        print("   -", f.name)

    # Load model Whisper
    print(f"[INFO] Loading Whisper model: {WHISPER_MODEL_NAME}")
    model = whisper.load_model(WHISPER_MODEL_NAME, device=device)

    for audio_path in audio_files:
        print(f"\n[INFO] Memproses: {audio_path.name}")

        transcribe_kwargs: Dict[str, Any] = {
            "fp16": True if device == "cuda" else False,
            "verbose": False,
        }

        if FORCE_LANGUAGE is not None:
            transcribe_kwargs["language"] = FORCE_LANGUAGE

        # Transkripsi
        print(f"0")
        result = model.transcribe(str(audio_path), **transcribe_kwargs)
        print(f"[DEBUG] Full result: {json.dumps(result, indent=2)}...")  # print sebagian besar hasil
        print(f"2")
        
        # Print result dari transcribe
        print(f"\n[DEBUG] Result keys: {result.keys()}")
        print(f"[DEBUG] Language detected: {result.get('language')}")
        print(f"[DEBUG] Duration: {result.get('duration')} seconds")
        print(f"[DEBUG] Text length: {len(result.get('text', ''))} chars")
        print(f"[DEBUG] Segments count: {len(result.get('segments', []))}")

        language = result.get("language", FORCE_LANGUAGE or "unknown")
        print(f"3")
        text_full = result.get("text", "").strip()
        print(f"4")
        segments_raw = result.get("segments", [])

        print(f"[INFO] Bahasa: {language}")
        print(f"[INFO] Total segmen: {len(segments_raw)}")
        print(f"[INFO] Panjang text: {len(text_full)} karakter")

        # Normalisasi segmen
        segments: List[Dict[str, Any]] = []
        for seg in segments_raw:
            segments.append(
                {
                    "id": int(seg.get("id", 0)),
                    "start": float(seg.get("start", 0.0)),
                    "end": float(seg.get("end", 0.0)),
                    "text": seg.get("text", "").strip(),
                }
            )

        # Simpan ke JSON
        out_name = audio_path.stem + "_whisper_small.json"
        out_path = Path(OUTPUT_DIR) / out_name

        payload = {
            "audio_file": str(audio_path),
            "model": WHISPER_MODEL_NAME,
            "device": device,
            "language": language,
            "text": text_full,
            "segments": segments,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"[INFO] Hasil disimpan ke: {out_path}")

        # preview sedikit
        print("[SNIPPET]")
        for s in segments[:3]:
            print(f"[{s['start']:.1f}s–{s['end']:.1f}s] {s['text']}")


if __name__ == "__main__":
    main()
