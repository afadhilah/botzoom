#!/bin/bash
# Expose BotZoom backend to internet using Serveo
# This will create a public HTTPS URL that forwards to localhost:8000

echo "🚀 Starting Serveo tunnel..."
echo "📡 Exposing localhost:8000 to internet..."
echo ""

# Loop to auto-reconnect if connection drops
while true; do
    echo "🔄 Connecting to serveo.net..."
    ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R 80:localhost:8000 serveo.net
    
    echo "⚠️  Connection lost, reconnecting in 5 seconds..."
    sleep 5
done
