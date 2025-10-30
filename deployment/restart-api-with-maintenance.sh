#!/bin/bash
# XCRI API Restart with Maintenance Mode
# Uses the existing maintenance.html page at /xcri/maintenance.html
#
# Usage: ./deployment/restart-api-with-maintenance.sh

set -e

XCRI_DIR="/home/web4ustfccca/public_html/iz/xcri"
HTACCESS="${XCRI_DIR}/.htaccess"

echo "=== XCRI API Restart with Maintenance Mode ==="
echo ""

# Step 1: Enable maintenance mode by adding redirect rules at top of .htaccess
echo "Step 1: Enabling maintenance mode..."
ssh ustfccca-web4 "cd ${XCRI_DIR} && \
# Backup current .htaccess
cp .htaccess .htaccess.backup && \
# Add maintenance mode redirect at the top
cat > .htaccess.tmp << 'MAINT_EOF'
# === MAINTENANCE MODE - TEMPORARY ===
# Added by restart-api-with-maintenance.sh
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/iz/xcri/maintenance.html$
RewriteCond %{REQUEST_URI} !^/iz/xcri/assets/
RewriteCond %{REQUEST_URI} !^/iz/xcri/.*\.(css|js|png|jpg|jpeg|gif|ico|svg)$
RewriteRule ^(.*)$ /iz/xcri/maintenance.html [R=503,L]
Header always set Retry-After \"60\"
# === END MAINTENANCE MODE ===

MAINT_EOF
# Append original .htaccess content
cat .htaccess >> .htaccess.tmp && \
mv .htaccess.tmp .htaccess"

echo "✅ Maintenance mode enabled - users see maintenance page"
echo ""

# Give users a moment to see the page
sleep 2

# Step 2: Kill all Python processes
echo "Step 2: Stopping API (killing all Python processes)..."
ssh ustfccca-web4 'killall -9 python3.9 2>/dev/null || true'
sleep 3

# Verify all processes are dead
PROCESS_COUNT=$(ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l')
if [ "$PROCESS_COUNT" -ne "0" ]; then
    echo "❌ ERROR: $PROCESS_COUNT processes still running!"
    echo "   Manual cleanup required. Restoring .htaccess..."
    ssh ustfccca-web4 "mv ${HTACCESS}.backup ${HTACCESS}"
    exit 1
fi
echo "✅ All Python processes stopped"
echo ""

# Step 3: Clear Python bytecode cache
echo "Step 3: Clearing Python bytecode cache..."
ssh ustfccca-web4 "cd ${XCRI_DIR}/api && \
  find . -name '*.pyc' -delete 2>/dev/null && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null"
echo "✅ Bytecode cache cleared"
echo ""

# Step 4: Start API with 4 workers
echo "Step 4: Starting API with 4 workers..."
ssh ustfccca-web4 "cd ${XCRI_DIR}/api && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> ../logs/api-live.log 2>&1 &"
echo "✅ API started, waiting for workers to initialize..."
echo ""

# Step 5: Wait for workers to spawn (15 seconds)
echo "Step 5: Waiting 15 seconds for workers to initialize..."
sleep 15
echo ""

# Step 6: Verify API health
echo "Step 6: Verifying API health..."
HEALTH_CHECK=$(curl -s "https://web4.ustfccca.org/iz/xcri/api/health" 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'error'))" 2>/dev/null || echo "error")

if [ "$HEALTH_CHECK" != "healthy" ]; then
    echo "❌ ERROR: API health check failed!"
    echo "   Health status: $HEALTH_CHECK"
    echo "   Maintenance mode still enabled - check logs manually:"
    echo "   ssh ustfccca-web4 'tail -100 ${XCRI_DIR}/logs/api-live.log'"
    echo ""
    echo "   To disable maintenance mode manually:"
    echo "   ssh ustfccca-web4 'mv ${HTACCESS}.backup ${HTACCESS}'"
    exit 1
fi

# Step 7: Verify process count
PROCESS_COUNT=$(ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l')
echo "✅ API is healthy (status: $HEALTH_CHECK)"
echo "   Process count: $PROCESS_COUNT (expected: 5 = 1 parent + 4 workers)"
echo ""

# Step 8: Test the specific endpoint that was fixed
echo "Step 7: Testing matchups endpoint..."
MATCHUP_TEST=$(curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=12&season_year=2025&limit=1" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"OK: {data['total']} matchups, {len(data['matchups'])} returned\")" 2>/dev/null || echo "ERROR")

if [[ "$MATCHUP_TEST" == ERROR* ]]; then
    echo "⚠️  WARNING: Matchups endpoint test failed: $MATCHUP_TEST"
    echo "   API is running but endpoint may have issues"
else
    echo "✅ Matchups endpoint test: $MATCHUP_TEST"
fi
echo ""

# Step 9: Disable maintenance mode
echo "Step 8: Disabling maintenance mode..."
ssh ustfccca-web4 "mv ${HTACCESS}.backup ${HTACCESS}"
echo "✅ Maintenance mode disabled - site restored to normal"
echo ""

echo "========================================="
echo "✅ RESTART COMPLETE"
echo "========================================="
echo ""
echo "API URL:     https://web4.ustfccca.org/iz/xcri/api/health"
echo "Frontend:    https://web4.ustfccca.org/iz/xcri/"
echo "Processes:   $PROCESS_COUNT (expected: 5)"
echo "Health:      $HEALTH_CHECK"
echo ""
echo "Site is now live and accepting user traffic!"
