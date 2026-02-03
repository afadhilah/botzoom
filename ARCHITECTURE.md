# BotZoom Production Architecture
Server: 10.28.85.33

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Browser                           │
│                 (User di network)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Request
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               Server 10.28.85.33                            │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │           NGINX (Port 80)                             │ │
│  │  - Reverse Proxy                                      │ │
│  │  - Static File Server                                 │ │
│  │  - Load Balancer                                      │ │
│  └───────────┬──────────────────────┬────────────────────┘ │
│              │                      │                       │
│              │ / (Root)             │ /api                  │
│              │                      │                       │
│              ▼                      ▼                       │
│  ┌─────────────────────┐  ┌───────────────────────────┐   │
│  │  Frontend Static    │  │   FastAPI Backend         │   │
│  │  (Vue.js Build)     │  │   (uvicorn)               │   │
│  │                     │  │   localhost:8000          │   │
│  │  /dist/index.html   │  │                           │   │
│  │  /dist/assets/*     │  │  - REST API               │   │
│  └─────────────────────┘  │  - Authentication         │   │
│                           │  - Transcription          │   │
│                           │  - Summarization          │   │
│                           └────────────┬──────────────┘   │
│                                        │                   │
│                                        │                   │
│                           ┌────────────┴──────────────┐   │
│                           │                           │   │
│                           ▼                           ▼   │
│                  ┌────────────────┐         ┌──────────────────┐
│                  │   Database     │         │  External APIs   │
│                  │                │         │                  │
│                  │  SQLite/       │         │  - OpenAI        │
│                  │  PostgreSQL    │         │  - Zoom          │
│                  └────────────────┘         │  - HuggingFace   │
│                                             └──────────────────┘
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           Systemd Service                             │   │
│  │  - Auto-start on boot                                 │   │
│  │  - Auto-restart on failure                            │   │
│  │  - Logging to /var/log/botzoom/                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Request Flow

### 1. Frontend Request (GET /)
```
Browser → NGINX:80 → /home/cak-seno/botzoom/frontend/dist/index.html
```

### 2. API Request (POST /api/transcribe)
```
Browser → NGINX:80/api → Proxy to localhost:8000 → FastAPI
```

### 3. File Upload Flow
```
Browser Upload → NGINX → FastAPI → Save to /uploads/ 
                                   → Process with Whisper
                                   → Save to Database
                                   → Return Result
```

## Technology Stack

### Frontend
- **Framework**: Vue.js 3 + TypeScript
- **Build Tool**: Vite
- **UI**: TailwindCSS, Reka UI
- **State**: Pinia
- **Build Output**: `/home/cak-seno/botzoom/frontend/dist/`

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **Workers**: 4 workers
- **Host**: 127.0.0.1:8000 (internal only)

### Infrastructure
- **Reverse Proxy**: Nginx
- **Process Manager**: Systemd
- **Database**: SQLite (default) / PostgreSQL (recommended)
- **OS**: Linux (Ubuntu/Debian)

### AI/ML
- **Transcription**: Whisper (OpenAI)
- **Diarization**: Pyannote
- **Summarization**: OpenAI GPT / LLM

## Directory Structure (Production)

```
/home/cak-seno/botzoom/
├── backend/
│   ├── .venv/                    # Python virtual environment
│   ├── .env.production           # Production config
│   ├── main.py                   # FastAPI app
│   ├── requirements.txt
│   ├── uploads/                  # Uploaded files
│   └── ...
├── frontend/
│   ├── dist/                     # Built files (served by Nginx)
│   │   ├── index.html
│   │   └── assets/
│   ├── .env.production           # Production API URL
│   └── ...
├── storage/
│   ├── audio/                    # Audio recordings
│   └── transcripts/              # Generated transcripts
├── nginx/
│   └── botzoom.conf              # Nginx config
├── systemd/
│   └── botzoom-backend.service   # Systemd service
├── deploy.sh                     # Deployment script
└── DEPLOYMENT.md                 # Full documentation
```

## Nginx Configuration

**Location Blocks:**
- `/` → Frontend static files
- `/api` → Backend proxy
- `/docs` → API documentation
- `/health` → Health check

## Systemd Service

**Service Name**: `botzoom-backend.service`

**Features:**
- Auto-start on boot
- Auto-restart on failure
- Environment from `.env.production`
- Logging to `/var/log/botzoom/`

**Commands:**
```bash
sudo systemctl start botzoom-backend    # Start
sudo systemctl stop botzoom-backend     # Stop
sudo systemctl restart botzoom-backend  # Restart
sudo systemctl status botzoom-backend   # Status
```

## Security

### Network
- Backend ONLY listens on `127.0.0.1:8000` (not public)
- All public access through Nginx
- CORS configured for `10.28.85.33`

### Authentication
- JWT tokens
- Bcrypt password hashing
- OTP email verification

### File Uploads
- Max size: 100MB
- Validated extensions
- Scanned path traversal

## Monitoring & Logs

### Backend Logs
```bash
sudo journalctl -u botzoom-backend -f
/var/log/botzoom/backend.log
/var/log/botzoom/backend-error.log
```

### Nginx Logs
```bash
/var/log/nginx/botzoom_access.log
/var/log/nginx/botzoom_error.log
```

## Scalability Considerations

### Current Setup (Single Server)
- Good for: Small to medium usage
- Max concurrent users: ~100-500

### Future Improvements
1. **Horizontal Scaling**: Multiple backend instances
2. **Load Balancing**: Nginx upstream with multiple backends
3. **Database**: PostgreSQL with connection pooling
4. **Caching**: Redis for session/results
5. **CDN**: Static asset delivery
6. **Queue**: Celery/RQ for async transcription
7. **Docker**: Containerization for easier deployment

## Backup Strategy

### What to Backup
- Database (SQLite/PostgreSQL)
- Uploaded files (`uploads/`, `storage/`)
- Configuration files (`.env.production`)

### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/botzoom_$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database
cp /home/cak-seno/botzoom/backend/meeting_transcript.db $BACKUP_DIR/

# Storage
tar -czf $BACKUP_DIR/storage.tar.gz /home/cak-seno/botzoom/storage/

# Config
cp /home/cak-seno/botzoom/backend/.env.production $BACKUP_DIR/
```

## Performance Optimization

### Nginx
- Gzip compression: ON
- Static file caching: 1 year
- Client max body: 100MB

### Backend
- Workers: 4 (CPU cores)
- Timeout: 300s (for long transcription)
- Connection pool: Enabled

### Database
- Indexes on frequently queried fields
- Regular VACUUM (SQLite) or VACUUM ANALYZE (PostgreSQL)

## High Availability (Future)

```
                    ┌──────────┐
                    │  Nginx   │
                    │  (LB)    │
                    └────┬─────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌────────┐      ┌────────┐      ┌────────┐
    │Backend │      │Backend │      │Backend │
    │Server 1│      │Server 2│      │Server 3│
    └────┬───┘      └────┬───┘      └────┬───┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                  ┌─────────────┐
                  │ PostgreSQL  │
                  │  (Primary)  │
                  └─────────────┘
```
