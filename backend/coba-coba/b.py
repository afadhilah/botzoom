import os
import json
from pathlib import Path
from typing import List, Dict, Any

import torch
import whisperx


# ---------- KONFIGURASI ----------
# Folder tempat file .wav / .mp3 disimpan
AUDIO_DIR = r"D:\Project\PLN\Meeting-Transcript\storage\audio"  # ganti sesuai folder lu

# Folder output untuk simpan hasil transkrip (.json)
OUTPUT_DIR = r"D:\Project\PLN\Meeting-Transcript\storage\transcripts"

# Model whisperx (semakin besar semakin berat)
WHISPER_MODEL_NAME = "small"  # "tiny" / "base" / "small" / "medium" / "large-v2"

# Kalau mau diarization (speaker), wajib True
USE_DIARIZATION = True

# Kalau diarization butuh token HF untuk beberapa model
HUGGINGFACE_TOKEN = None  # isi kalau punya, kalau tidak biarkan None
# -------------------------------


def list_audio_files(folder: str) -> List[Path]:
    """Ambil semua file audio dari folder."""
    # exts = {".wav", ".mp3", ".m4a", ".flac"}
    exts = {".wav"}
    p = Path(folder)
    files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in exts]
    return sorted(files)


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def main():
    # Cek device
    device = "cpu"
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using device: {device}")

    ensure_dir(OUTPUT_DIR)

    audio_files = list_audio_files(AUDIO_DIR)
    if not audio_files:
        print(f"[WARN] Tidak ada file audio di folder: {AUDIO_DIR}")
        return

    print(f"[INFO] Ditemukan {len(audio_files)} file audio.")

    # Load model WhisperX
    print(f"[INFO] Loading WhisperX model: {WHISPER_MODEL_NAME}")
    model = whisperx.load_model(
        WHISPER_MODEL_NAME,
        device=device,
        # compute_type="float32" if device == "cuda" else "int8"
        compute_type="int8"
    )

    align_model = None
    metadata = None
    diarize_model = None

    for audio_path in audio_files:
        print(f"\n[INFO] Memproses: {audio_path.name}")

        # 1. Transkripsi dasar
        result = model.transcribe(str(audio_path))
        segments = result.get("segments", [])
        language = result.get("language", "unknown")

        print(f"[INFO] Bahasa terdeteksi: {language}")
        print(f"[INFO] Jumlah segmen awal: {len(segments)}")

        # 2. Alignment (opsional tapi disarankan)
        print("[INFO] Loading alignment model...")
        if align_model is None:
            align_model, metadata = whisperx.load_align_model(
                language_code=language,
                device=device
            )

        aligned_result = whisperx.align(
            segments,
            align_model,
            metadata,
            str(audio_path),
            device,
            return_char_alignments=False,
        )

        final_segments: List[Dict[str, Any]] = aligned_result["segments"]

        # 3. Diarization (speaker) kalau diaktifkan
        # if USE_DIARIZATION:
        #     print("[INFO] Running diarization (speaker detection)...")
        #     if diarize_model is None:
        #         diarize_model = whisperx.DiarizationPipeline(
        #             use_auth_token=HUGGINGFACE_TOKEN,
        #             device=device
        #         )

        #     diarize_segments = diarize_model(str(audio_path))

        #     # Assign speaker ke setiap segmen
        #     final_segments, _ = whisperx.assign_word_speakers(
        #         diarize_segments,
        #         aligned_result["segments"]
        #     )

        # 4. Bentuk hasil final ke format sederhana
        output_items = []
        for seg in final_segments:
            start = seg.get("start", 0.0)
            end = seg.get("end", 0.0)
            text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "Speaker")

            output_items.append(
                {
                    "start": float(start),
                    "end": float(end),
                    "speaker": str(speaker),
                    "text": text,
                }
            )

        # 5. Simpan ke file JSON
        out_name = audio_path.stem + "_whisperx.json"
        out_path = Path(OUTPUT_DIR) / out_name

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "audio_file": str(audio_path),
                    "language": language,
                    "segments": output_items,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"[INFO] Hasil disimpan ke: {out_path}")
        # Cetak sedikit cuplikan
        if output_items:
            print("[SNIPPET]")
            for s in output_items[:3]:
                print(
                    f"{s['speaker']} ({s['start']:.1f}s–{s['end']:.1f}s): {s['text']}"
                )

    print("\n[INFO] Selesai memproses semua file audio.")


if __name__ == "__main__":
    main()
