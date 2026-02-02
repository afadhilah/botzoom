# Architecture Diagram (Simple)

```mermaid
graph TD
    ZOOM[Zoom Meeting] -->|Webhook| BACKEND[Backend API]
    BACKEND -->|Download Record| WHISPERX[WhisperX Service]
    WHISPERX -->|Transcript| DB[(Database)]
    DB --> LLM[LLM Service]
    LLM --> OUTPUT[Output (txt/json)]
```

- **Zoom**: Sumber meeting & recording
- **Webhook**: Trigger ke backend saat meeting selesai/recording siap
- **Backend**: FastAPI, handle webhook, download audio
- **WhisperX**: Proses transkripsi audio
- **Database**: Simpan hasil transkrip
- **LLM**: Proses lanjutan (opsional, misal summary)
- **Output**: File transcript (txt/json)
