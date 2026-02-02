# Bot Zoom - Standalone Audio Transcription

Aplikasi standalone untuk transcription audio menggunakan Whisper AI. Tanpa database, authentication, atau security layers - fokus pada core functionality saja.

## 🎯 Features

- **Audio Recording**: Record audio langsung dari browser
- **File Upload**: Upload file audio (mp3, wav, m4a, webm)
- **Real-time Transcription**: Automatic transcription menggunakan OpenAI Whisper
- **Segment View**: Lihat transcript per segment dengan timestamp
- **File-based Storage**: Semua transcript disimpan sebagai JSON files
- **Latest Transcript**: Quick access ke transcript terakhir

## 📁 Project Structure

```
bot_zoom/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── whisper_service.py      # Whisper transcription logic
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── transcripts/           # JSON storage (auto-created)
│   └── uploads/               # Temporary audio files (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.vue            # Main Vue component
│   │   ├── main.js            # Vue entry point
│   │   └── style.css          # Styling
│   ├── index.html             # HTML entry
│   ├── package.json           # Node dependencies
│   └── vite.config.js         # Vite configuration
│
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) CUDA-capable GPU for faster transcription

### Backend Setup

1. Navigate to backend directory:
```bash
cd bot_zoom/backend
```

2. Create virtual environment:
```bash
python -m venv .venv
```

3. Activate virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file from template:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

6. (Optional) Edit `.env` to configure:
   - `WHISPER_MODEL`: Model size (tiny, base, small, medium, large)
   - `DEVICE`: cuda or cpu

7. Run backend server:
```bash
python main.py
```

Backend will start at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd bot_zoom/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will start at `http://localhost:5173`

## 📖 Usage

### Recording Audio

1. Buka browser ke `http://localhost:5173`
2. Pilih tab "Record"
3. Klik tombol microphone (browser akan minta permission)
4. Bicara/rekam audio
5. Klik lagi untuk stop
6. Tunggu processing selesai
7. Transcript akan muncul di panel kanan

### Uploading Audio File

1. Pilih tab "Upload"
2. Klik "Choose File" atau drag & drop file audio
3. Tunggu processing selesai
4. Transcript akan muncul di panel kanan

### Viewing Latest Transcript

1. Pilih tab "Latest"
2. Klik "Load Transcript" untuk melihat transcript terakhir
3. Atau klik "Refresh" untuk update data

## 🔧 API Endpoints

### `POST /api/transcribe`
Upload dan transcribe audio file

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `file` (audio file)

**Response:**
```json
{
  "id": 1675234567890,
  "created_at": "2026-02-02T14:30:00",
  "status": "completed",
  "language": "id",
  "model": "small",
  "device": "cuda",
  "text": "Full transcript text...",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 2.5,
      "text": "Segment text",
      "speaker": "Speaker 1"
    }
  ]
}
```

### `GET /api/transcripts/latest`
Get transcript terakhir

**Response:** Same as transcribe response

### `GET /api/transcripts/{id}`
Get transcript by ID

**Response:** Same as transcribe response

### `GET /api/transcripts?limit=10`
List semua transcripts (metadata only)

**Response:**
```json
{
  "transcripts": [
    {
      "id": 1675234567890,
      "created_at": "2026-02-02T14:30:00",
      "status": "completed",
      "language": "id",
      "model": "small",
      "segment_count": 15
    }
  ],
  "total": 1
}
```

### `GET /health`
Health check endpoint

## ⚙️ Configuration

### Backend (.env)

```env
# Whisper model: tiny, base, small, medium, large
WHISPER_MODEL=small

# Device: cuda or cpu
DEVICE=cuda

# Server
HOST=0.0.0.0
PORT=8000

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# Storage paths
TRANSCRIPTS_DIR=./transcripts
UPLOADS_DIR=./uploads
```

### Frontend (vite.config.js)

API proxy sudah dikonfigurasi untuk forward `/api/*` ke `http://localhost:8000`

## 🎨 Customization

### Mengubah Whisper Model

Edit `.env`:
```env
WHISPER_MODEL=medium  # atau tiny, base, small, large
```

Model yang lebih besar = lebih akurat tapi lebih lambat.

### Mengubah Port

**Backend** - Edit `.env`:
```env
PORT=8001
```

**Frontend** - Edit `vite.config.js`:
```js
server: {
  port: 5174,
  proxy: {
    '/api': {
      target: 'http://localhost:8001',  // sesuaikan dengan backend port
      changeOrigin: true,
    },
  },
}
```

## 🐛 Troubleshooting

### Backend tidak bisa start

- Pastikan virtual environment sudah diaktifkan
- Cek apakah semua dependencies terinstall: `pip list`
- Cek error message di console

### Transcription sangat lambat

- Gunakan GPU jika tersedia (set `DEVICE=cuda`)
- Gunakan model yang lebih kecil (set `WHISPER_MODEL=tiny` atau `base`)
- Pastikan CUDA terinstall jika menggunakan GPU

### Frontend tidak bisa connect ke backend

- Pastikan backend sudah running di `http://localhost:8000`
- Cek CORS configuration di backend `.env`
- Buka browser console untuk lihat error message

### Microphone tidak bisa diakses

- Browser harus menggunakan HTTPS atau localhost
- Pastikan browser punya permission untuk akses microphone
- Coba browser lain (Chrome/Edge recommended)

## 📝 Notes

- Transcript files disimpan di `backend/transcripts/` sebagai JSON
- Uploaded audio files disimpan sementara di `backend/uploads/`
- Tidak ada user management - semua transcript accessible oleh siapa saja
- Tidak ada database - restart server tidak akan hilangkan transcript yang sudah ada

## 🔒 Security Warning

⚠️ **Aplikasi ini TIDAK untuk production!** 

Tidak ada:
- Authentication
- Authorization
- Input validation yang ketat
- Rate limiting
- HTTPS enforcement

Hanya untuk development/testing purposes.

## 📄 License

MIT License - Free to use and modify
