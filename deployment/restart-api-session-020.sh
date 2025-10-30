#!/bin/bash
# XCRI API Restart Script - Session 020
# Restarts XCRI API to load 6 new fields from backend code
# Usage: Run this script on the server (web4.ustfccca.org)
#
# Purpose:
# - Kill all uvicorn processes (1 parent + 4 workers)
# - Clear Python bytecode cache (.pyc files)
# - Start fresh uvicorn with 4 workers
# - Verify new code (with 6 new fields) is loaded
#
# New Fields Being Deployed:
# - TeamKnockoutRanking: regl_group_name, conf_group_name, most_recent_race_date
# - TeamKnockoutMatchup: meet_id, team_a_ko_rank, team_b_ko_rank

set -e

echo "=========================================="
echo "XCRI API Restart - Session 020"
echo "=========================================="
echo ""

# Configuration
API_DIR="/home/web4ustfccca/public_html/iz/xcri/api"
LOG_DIR="/home/web4ustfccca/public_html/iz/xcri/logs"
WEB_ROOT="/home/web4ustfccca/public_html/iz/xcri"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==========================================
# Phase 1: Enable Maintenance Mode
# ==========================================
echo -e "${YELLOW}Phase 1: Enable Maintenance Mode${NC}"

cd "$WEB_ROOT"

# Backup current .htaccess
cp .htaccess ".htaccess.backup-$(date +%Y%m%d-%H%M%S)"

# Create maintenance mode block
cat > .htaccess.maintenance << 'EOF'
# ==========================================
# MAINTENANCE MODE - Session 020 Restart
# API update in progress
# ==========================================
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/iz/xcri/maintenance\.html$
RewriteCond %{REQUEST_URI} !^/iz/xcri/.*\.(css|js|png|jpg|jpeg|gif|ico|svg)$
RewriteRule ^.*$ /iz/xcri/maintenance.html [R=503,L]
ErrorDocument 503 /iz/xcri/maintenance.html
Header set Retry-After "300"
# END MAINTENANCE MODE
# ==========================================

EOF

# Combine maintenance block with existing .htaccess
cat .htaccess.maintenance .htaccess > .htaccess.new
mv .htaccess.new .htaccess

echo -e "${GREEN}✓ Maintenance mode enabled${NC}"
echo ""

# ==========================================
# Phase 2: Kill All Processes
# ==========================================
echo -e "${YELLOW}Phase 2: Stopping all uvicorn processes${NC}"

KILLED_COUNT=$(ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | wc -l)

if [ "$KILLED_COUNT" -gt 0 ]; then
    ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    echo "   Killed $KILLED_COUNT processes"
else
    echo "   No existing processes found"
fi

sleep 3

# Verify
REMAINING=$(ps aux | grep "[p]ython3.9" | wc -l)
echo -e "${GREEN}✓ Processes stopped (remaining: $REMAINING)${NC}"
echo ""

# ==========================================
# Phase 3: Clear Python Bytecode Cache
# ==========================================
echo -e "${YELLOW}Phase 3: Clearing Python bytecode cache${NC}"

cd "$API_DIR"

PYC_COUNT=$(find . -name "*.pyc" 2>/dev/null | wc -l)
PYCACHE_COUNT=$(find . -type d -name __pycache__ 2>/dev/null | wc -l)

find . -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo "   Deleted $PYC_COUNT .pyc files"
echo "   Deleted $PYCACHE_COUNT __pycache__ directories"

# Verify
REMAINING_PYC=$(find . -name "*.pyc" 2>/dev/null | wc -l)
echo -e "${GREEN}✓ Cache cleared (remaining: $REMAINING_PYC)${NC}"
echo ""

# ==========================================
# Phase 4: Start Uvicorn with 4 Workers
# ==========================================
echo -e "${YELLOW}Phase 4: Starting uvicorn with 4 workers${NC}"

cd "$API_DIR"

# Activate virtual environment
source venv/bin/activate

# Start in background
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> "$LOG_DIR/api-live.log" 2>&1 &

PARENT_PID=$!
echo "   Parent PID: $PARENT_PID"

# Wait for workers to initialize
echo "   Waiting for workers to start (6 seconds)..."
sleep 6

echo -e "${GREEN}✓ Uvicorn started${NC}"
echo ""

# ==========================================
# Phase 5: Verify Process Count
# ==========================================
echo -e "${YELLOW}Phase 5: Verifying process count${NC}"

PROCESS_COUNT=$(ps aux | grep "[p]ython3.9" | wc -l)

if [ "$PROCESS_COUNT" -ge 5 ]; then
    echo -e "${GREEN}✓ Process count OK ($PROCESS_COUNT processes: 1 parent + 4 workers)${NC}"
else
    echo -e "${RED}✗ WARNING: Expected 5+ processes, found $PROCESS_COUNT${NC}"
    echo "   Check logs: tail -50 $LOG_DIR/api-live.log"
fi

echo ""

# ==========================================
# Phase 6: Test Health Endpoint
# ==========================================
echo -e "${YELLOW}Phase 6: Testing health endpoint${NC}"

HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8001/health 2>/dev/null || echo "{\"status\":\"error\"}")
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✓ Health endpoint: OK${NC}"
else
    echo -e "${RED}✗ Health endpoint: $HEALTH_STATUS${NC}"
    echo "   Response: $HEALTH_RESPONSE"
fi

echo ""

# ==========================================
# Phase 7: Verify New Fields Are Loaded
# ==========================================
echo -e "${YELLOW}Phase 7: Verifying new fields in API response${NC}"

TEAM_KO_RESPONSE=$(curl -s "http://127.0.0.1:8001/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1" 2>/dev/null || echo "{\"teams\":[]}")

# Check for new fields
HAS_REGL_GROUP=$(echo "$TEAM_KO_RESPONSE" | grep -q "regl_group_name" && echo "yes" || echo "no")
HAS_CONF_GROUP=$(echo "$TEAM_KO_RESPONSE" | grep -q "conf_group_name" && echo "yes" || echo "no")
HAS_RACE_DATE=$(echo "$TEAM_KO_RESPONSE" | grep -q "most_recent_race_date" && echo "yes" || echo "no")

echo "   New fields check:"
echo "   - regl_group_name: $HAS_REGL_GROUP"
echo "   - conf_group_name: $HAS_CONF_GROUP"
echo "   - most_recent_race_date: $HAS_RACE_DATE"

if [ "$HAS_REGL_GROUP" = "yes" ] && [ "$HAS_CONF_GROUP" = "yes" ] && [ "$HAS_RACE_DATE" = "yes" ]; then
    echo -e "${GREEN}✓ All new fields present${NC}"
else
    echo -e "${RED}✗ WARNING: Some fields missing${NC}"
    echo "   Check logs: tail -100 $LOG_DIR/api-live.log"
fi

echo ""

# ==========================================
# Phase 8: Disable Maintenance Mode
# ==========================================
echo -e "${YELLOW}Phase 8: Disabling maintenance mode${NC}"

cd "$WEB_ROOT"

# Find and remove maintenance mode block
# The block is typically at the beginning of .htaccess
MAINTENANCE_LINES=$(head -20 .htaccess | grep -n "MAINTENANCE MODE" | wc -l)

if [ "$MAINTENANCE_LINES" -gt 0 ]; then
    # Remove lines 2-12 (typical maintenance block)
    sed -i '2,/^# END MAINTENANCE MODE/d' .htaccess
    echo "   Removed maintenance mode block"
    echo -e "${GREEN}✓ Maintenance mode disabled${NC}"
else
    echo "   Maintenance mode block not found"
    echo -e "${YELLOW}⚠ Manual verification needed${NC}"
fi

echo ""

# ==========================================
# Phase 9: Final Verification
# ==========================================
echo -e "${YELLOW}Phase 9: Final verification${NC}"

# Test public URL
PUBLIC_HEALTH=$(curl -s https://web4.ustfccca.org/iz/xcri/api/health 2>/dev/null | grep -q "healthy" && echo "OK" || echo "FAILED")
echo "   Public health endpoint: $PUBLIC_HEALTH"

# Test frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://web4.ustfccca.org/iz/xcri/ 2>/dev/null)
echo "   Frontend HTTP status: $FRONTEND_STATUS"

echo ""

# ==========================================
# Summary
# ==========================================
echo "=========================================="
echo -e "${GREEN}XCRI API Restart Complete${NC}"
echo "=========================================="
echo ""
echo "Key Metrics:"
echo "  - Python processes: $PROCESS_COUNT (expected: 5)"
echo "  - Health endpoint: $HEALTH_STATUS"
echo "  - New fields present: regl_group_name, conf_group_name, most_recent_race_date"
echo "  - Maintenance mode: Disabled"
echo ""
echo "Test URLs:"
echo "  - Health: https://web4.ustfccca.org/iz/xcri/api/health"
echo "  - Team Knockout: https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1"
echo "  - Frontend: https://web4.ustfccca.org/iz/xcri/"
echo ""
echo "Logs:"
echo "  - API: $LOG_DIR/api-live.log"
echo "  - Recent: tail -50 $LOG_DIR/api-live.log"
echo ""

# Exit with success
exit 0
