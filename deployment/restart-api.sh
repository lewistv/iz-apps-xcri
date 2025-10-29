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

# Stop existing processes (parent + all workers)
echo "1. Stopping existing uvicorn processes..."
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || echo "   No existing processes found"
sleep 3

# Clear Python bytecode cache
echo "2. Clearing Python bytecode cache..."
find . -name '*.pyc' -delete 2>/dev/null || true
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Activate virtual environment and start with 4 workers
echo "3. Starting uvicorn with 4 workers..."
source venv/bin/activate

nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> "$LOG_DIR/api-live.log" 2>&1 &

UVICORN_PID=$!
echo "   Started with PID: $UVICORN_PID"

# Wait for workers to start
sleep 6

# Verify processes are running (1 parent + 4 workers = 5 total)
PROCESS_COUNT=$(ps aux | grep "[p]ython3.9" | wc -l)
if [ "$PROCESS_COUNT" -ge 5 ]; then
    echo "4. Process verification: OK ($PROCESS_COUNT Python processes running)"
else
    echo "4. Process verification: WARNING (Expected 5 processes, found $PROCESS_COUNT)"
fi

# Test health endpoint
echo "5. Testing health endpoint..."
if curl -s http://127.0.0.1:8001/health > /dev/null; then
    echo "   Health check: OK"
else
    echo "   Health check: FAILED"
    echo "   Check logs at: $LOG_DIR/api-live.log"
    exit 1
fi

echo ""
echo "=== XCRI API Restarted Successfully ==="
echo "Parent PID: $UVICORN_PID"
echo "Workers: 4"
echo "Logs: $LOG_DIR/api-live.log"
echo ""
echo "Test URL: https://web4.ustfccca.org/iz/xcri/api/health"
