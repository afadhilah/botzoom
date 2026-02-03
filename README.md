# BotZoom - Meeting Transcript & Zoom Bot System

Aplikasi full-stack untuk transcription meeting dengan AI dan Zoom bot integration.

## 🚀 Quick Start

### Development
```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
pnpm install
pnpm run dev
```

### Production Deployment (Server 10.28.85.33)

**Pertama kali:**
```bash
./install-dependencies.sh  # Install required software
nano backend/.env.production  # Configure environment
./deploy.sh  # Deploy!
```

**Update aplikasi:**
```bash
./deploy.sh
```

Akses: http://10.28.85.33

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Panduan deployment cepat
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Dokumentasi deployment lengkap
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arsitektur sistem
- **[CHECKLIST.md](CHECKLIST.md)** - Checklist deployment

## 🏗️ Tech Stack

**Frontend:** Vue.js 3 + TypeScript + Vite + TailwindCSS  
**Backend:** FastAPI + Python + SQLAlchemy  
**AI/ML:** Whisper (transcription) + Pyannote (diarization)  
**Infrastructure:** Nginx + Systemd + PostgreSQL

## 📁 Project Structure

```
botzoom/
├── backend/          # FastAPI backend
├── frontend/         # Vue.js frontend
├── nginx/            # Nginx configuration
├── systemd/          # Systemd service files
├── storage/          # Audio & transcript storage
├── deploy.sh         # Deployment script
└── docs/             # Additional documentation
```

## 🔧 Configuration Files

### Development
- `backend/.env` - Backend dev config
- `frontend/.env` - Frontend dev config

### Production
- `backend/.env.production` - Backend production config
- `frontend/.env.production` - Frontend production config
- `nginx/botzoom.conf` - Nginx configuration
- `systemd/botzoom-backend.service` - Systemd service

## 🎯 Features

- ✅ User authentication & authorization
- ✅ Audio file upload & transcription (Whisper)
- ✅ Speaker diarization (who spoke when)
- ✅ Meeting summarization (AI-powered)
- ✅ Zoom bot integration
- ✅ RESTful API
- 🚧 Real-time transcription (coming soon)

## 📊 Monitoring

### Backend Logs
```bash
sudo journalctl -u botzoom-backend -f
```

### Nginx Logs
```bash
sudo tail -f /var/log/nginx/botzoom_error.log
```

### Service Status
```bash
sudo systemctl status botzoom-backend nginx
```

## 🛠️ Common Commands

```bash
# Restart services
sudo systemctl restart botzoom-backend nginx

# Stop application
sudo systemctl stop botzoom-backend

# View logs
sudo journalctl -u botzoom-backend -n 100
```

## 🔒 Security

- JWT authentication
- Bcrypt password hashing
- CORS protection
- File upload validation
- Environment-based secrets

## 📝 License

Internal use only.

## 👥 Team

Developed by ICON Plus Team

  cd /home/cak-seno/botzoom/frontend && cat .env.production && echo -e "\n--- Building with production config ---" && npx vite build --mode production
sudo systemctl restart botzoom-backend
npx vite build && sudo systemctl restart nginx