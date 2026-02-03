#!/bin/bash
# Check running Zoom Bot processes

echo "=== Active Zoom Bot Processes ==="
ps aux | grep "run_zoom_bot.py" | grep -v grep

echo ""
echo "=== Recent Bot Activity (last 20 lines) ==="
sudo tail -n 20 /var/log/botzoom/zoom-bot.log
