#!/bin/bash
# XCRI API Restart Script
# Usage: ./restart-api.sh
# Run this on the server (web4.ustfccca.org) to restart the XCRI API

set -e

echo "=== XCRI API Restart ==="
echo ""

# Navigate to API directory
API_DIR="/home/web4ustfccca/public_html/iz/xcri/api"
LOG_DIR="/home/web4ustfccca/public_html/iz/xcri/logs"

cd "$API_DIR"

# Stop existing process
echo "1. Stopping existing uvicorn process..."
pkill -f "uvicorn main:app --host 127.0.0.1 --port 8001" || echo "   No existing process found"
sleep 2

# Clear Python bytecode cache
echo "2. Clearing Python bytecode cache..."
find . -name '*.pyc' -delete 2>/dev/null || true
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Activate virtual environment and start
echo "3. Starting new uvicorn process..."
source venv/bin/activate

nohup uvicorn main:app --host 127.0.0.1 --port 8001 \
    >> "$LOG_DIR/api-access.log" \
    2>> "$LOG_DIR/api-error.log" &

UVICORN_PID=$!
echo "   Started with PID: $UVICORN_PID"

# Wait a moment for startup
sleep 3

# Verify it's running
if ps -p $UVICORN_PID > /dev/null; then
    echo "4. Process verification: OK"
else
    echo "4. Process verification: FAILED"
    echo "   Check logs at: $LOG_DIR/api-error.log"
    exit 1
fi

# Test health endpoint
echo "5. Testing health endpoint..."
if curl -s http://127.0.0.1:8001/health > /dev/null; then
    echo "   Health check: OK"
else
    echo "   Health check: FAILED"
    echo "   Check logs at: $LOG_DIR/api-error.log"
    exit 1
fi

echo ""
echo "=== XCRI API Restarted Successfully ==="
echo "PID: $UVICORN_PID"
echo "Logs: $LOG_DIR/api-access.log"
echo "Errors: $LOG_DIR/api-error.log"
echo ""
echo "Test URL: https://web4.ustfccca.org/iz/xcri/api/health"
