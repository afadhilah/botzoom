#!/bin/bash
# Monitor Zoom Bot Logs

echo "=== Monitoring Zoom Bot Logs ==="
echo "Press Ctrl+C to stop"
echo ""

sudo tail -f /var/log/botzoom/zoom-bot.log
