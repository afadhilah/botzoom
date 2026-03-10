#!/bin/bash
# Manage Cloudflare Tunnel for BotZoom Backend

case "$1" in
  start)
    echo "🚀 Starting Cloudflare Tunnel..."
    nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflared.log 2>&1 &
    sleep 3
    echo ""
    echo "✅ Tunnel started!"
    echo ""
    echo "📡 Public URL:"
    cat /tmp/cloudflared.log | grep -E "https://.*trycloudflare.com" | tail -1
    echo ""
    ;;
    
  stop)
    echo "🛑 Stopping Cloudflare Tunnel..."
    pkill -f cloudflared
    echo "✅ Tunnel stopped"
    ;;
    
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
    
  status)
    if pgrep -f cloudflared > /dev/null; then
      echo "✅ Tunnel is RUNNING"
      echo ""
      echo "📡 Public URL:"
      cat /tmp/cloudflared.log 2>/dev/null | grep -E "https://.*trycloudflare.com" | tail -1
      echo ""
      echo "🔍 Process:"
      pgrep -af cloudflared
    else
      echo "❌ Tunnel is NOT running"
      echo ""
      echo "Run: $0 start"
    fi
    ;;
    
  url)
    cat /tmp/cloudflared.log 2>/dev/null | grep -E "https://.*trycloudflare.com" | tail -1
    ;;
    
  logs)
    tail -f /tmp/cloudflared.log
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|status|url|logs}"
    echo ""
    echo "Commands:"
    echo "  start    - Start CloudflareTunnel"
    echo "  stop     - Stop tunnel"
    echo "  restart  - Restart tunnel"
    echo "  status   - Check tunnel status"
    echo "  url      - Get public URL"
    echo "  logs     - Tail tunnel logs"
    exit 1
    ;;
esac
