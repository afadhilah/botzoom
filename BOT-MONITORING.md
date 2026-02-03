# Zoom Bot - Monitoring & Management

## Architecture
Bot Zoom sekarang berjalan sebagai **process terpisah** dari backend. Setiap kali ada request `/zoom/join`, backend akan spawn process baru untuk bot tersebut.

## Log Files
- **Backend:** `/var/log/botzoom/backend.log`
- **Bot:** `/var/log/botzoom/zoom-bot.log` ⭐ (Log khusus bot)

## Monitoring Commands

### 1. Monitor Bot Real-time
```bash
# Cara mudah (gunakan script)
./monitor-bot.sh

# Atau manual
sudo tail -f /var/log/botzoom/zoom-bot.log
```

### 2. Cek Status Bot
```bash
# Cara mudah
./check-bot.sh

# Atau manual - lihat process yang running
ps aux | grep "run_zoom_bot.py" | grep -v grep

# Lihat log terakhir
sudo tail -n 50 /var/log/botzoom/zoom-bot.log
```

### 3. Monitor Backend
```bash
sudo tail -f /var/log/botzoom/backend.log | grep -i "bot\|zoom"
```

## Manual Bot Testing
Untuk testing bot tanpa UI:
```bash
cd /home/cak-seno/botzoom/backend
source venv/bin/activate
python run_zoom_bot.py "https://zoom.us/j/123456789" --bot-name "Test Bot"
```

## Log Output yang Diharapkan

### Saat Bot Start:
```
2026-02-02 23:15:00 - __main__ - INFO - Starting Zoom bot for meeting: https://zoom.us/j/123456789
2026-02-02 23:15:00 - integrations.zoom.bot - INFO - Zoom bot initialized: ID=abc-123, Meeting=123456789
2026-02-02 23:15:01 - integrations.zoom.bot - INFO - Starting Zoom bot...
2026-02-02 23:15:02 - integrations.zoom.bot - INFO - Browser launched successfully
2026-02-02 23:15:03 - integrations.zoom.bot - INFO - Navigating to meeting ID: 123456789
```

### Saat Bot Join Meeting:
```
2026-02-02 23:15:10 - integrations.zoom.bot - INFO - Successfully navigated to meeting
2026-02-02 23:15:12 - integrations.zoom.bot - INFO - Entered bot name: Meeting Transcript Bot
2026-02-02 23:15:13 - integrations.zoom.bot - INFO - Clicked join button
2026-02-02 23:15:15 - integrations.zoom.bot - INFO - Audio connected
2026-02-02 23:15:20 - integrations.zoom.bot - INFO - Admitted to meeting!
2026-02-02 23:15:20 - integrations.zoom.bot - INFO - Monitoring meeting for up to 7200 seconds...
```

### Saat Meeting Selesai:
```
2026-02-02 23:45:00 - integrations.zoom.bot - INFO - Meeting ended - detected end message
2026-02-02 23:45:01 - integrations.zoom.bot - INFO - Cleaning up bot resources...
2026-02-02 23:45:02 - integrations.zoom.bot - INFO - Browser closed
2026-02-02 23:45:02 - __main__ - INFO - Bot session completed successfully
```

## Troubleshooting

### Bot tidak muncul di log
1. Cek apakah backend menerima request:
   ```bash
   sudo tail -f /var/log/botzoom/backend.log
   ```
2. Cek permission log file:
   ```bash
   ls -la /var/log/botzoom/zoom-bot.log
   ```

### Bot crash
Lihat error di log:
```bash
sudo grep -i error /var/log/botzoom/zoom-bot.log
```

### Kill bot yang stuck
```bash
# Lihat PID bot
ps aux | grep "run_zoom_bot.py" | grep -v grep

# Kill specific bot
kill -9 <PID>

# Atau kill semua bot
pkill -f "run_zoom_bot.py"
```

## File Locations
- Bot Script: `/home/cak-seno/botzoom/backend/run_zoom_bot.py`
- Monitor Script: `/home/cak-seno/botzoom/monitor-bot.sh`
- Check Script: `/home/cak-seno/botzoom/check-bot.sh`
- Bot Logs: `/var/log/botzoom/zoom-bot.log`
- Backend Logs: `/var/log/botzoom/backend.log`
