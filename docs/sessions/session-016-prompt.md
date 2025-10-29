# Session 016 Prompt: Server Restart & Deployment Verification

**Date**: October 29, 2025 (or later)
**Estimated Duration**: 1-2 hours
**Session Type**: Server maintenance and deployment verification
**Prerequisites**: Session 015 complete (backend code deployed)

---

## Session Objective

1. **Put server in maintenance mode** to safely restart services
2. **Restart API server** and verify Team Knockout endpoints are operational
3. **Create deployment agent** that knows how to correctly kill and restart the API process
4. **Document future development needs** for backend/frontend work

**Success Criteria**:
- ✅ All 6 Team Knockout endpoints responding correctly
- ✅ Deployment agent created for future use
- ✅ Server back in operational mode
- ✅ Future development roadmap documented

---

## Background

### What Was Done in Session 015
- ✅ Complete backend API implemented (1,549 lines)
  - 6 REST endpoints in `api/routes/team_knockout.py`
  - 7 async service functions in `api/services/team_knockout_service.py`
  - 10 Pydantic models in `api/models.py`
- ✅ Code committed to GitHub (commit: `1cf9f94`)
- ✅ Files deployed to server manually

### Current Problem
- ⚠️ API endpoints returning 404 (not found)
- ⚠️ Uvicorn workers likely not reloaded with new code
- ⚠️ Files are on server: `api/routes/team_knockout.py` (16,452 bytes), `api/services/team_knockout_service.py` (26,710 bytes)

### What Needs to Happen
- Kill existing uvicorn processes properly
- Start fresh uvicorn workers that load new router
- Test all 6 endpoints to confirm functionality
- Create reusable agent for future deployments

---

## Pre-Session Checklist

Before starting Session 016, ensure you have:

- [ ] SSH access to `ustfccca-web4` server
- [ ] Reviewed Session 015 wrap-up document
- [ ] Noted the current server state (check if API is responding)
- [ ] Confirmed files exist on server:
  - `/home/web4ustfccca/public_html/iz/xcri/api/routes/team_knockout.py`
  - `/home/web4ustfccca/public_html/iz/xcri/api/services/team_knockout_service.py`

---

## Phase 1: Server Maintenance Mode (15 minutes)

### Task 1.1: Create Maintenance Page

**Objective**: Show users a friendly message while server is being restarted

**Steps**:
```bash
ssh ustfccca-web4

# Option A: Create simple maintenance HTML
cat > /home/web4ustfccca/public_html/iz/xcri/maintenance.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>XCRI - Maintenance</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }
        h1 { margin: 0 0 1rem 0; }
        p { margin: 0.5rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ System Maintenance</h1>
        <p>XCRI Rankings is being updated with new features.</p>
        <p>We'll be back online in approximately 5-10 minutes.</p>
        <p><small>Team Knockout matchup system deployment in progress...</small></p>
    </div>
</body>
</html>
EOF

# Option B: Update .htaccess to redirect to maintenance (if needed)
# This can be done if you want ALL traffic to see maintenance page
```

**Decision**: For this session, maintenance page is optional since downtime will be < 2 minutes

### Task 1.2: Notify Users (Optional)

If this were a production deployment during business hours:
- Post to status page (if one exists)
- Send notification to stakeholders
- Update monitoring systems

**For this session**: Skip notification (low traffic, brief downtime)

---

## Phase 2: API Server Restart (30 minutes)

### Task 2.1: Identify Running Processes

**Find all uvicorn processes**:
```bash
ssh ustfccca-web4 'ps aux | grep uvicorn | grep -v grep'
```

**Expected output**:
```
web4ust+ 1132178  0.0  0.1 317892 23764 ?  S  13:39  0:00 /home/web4ustfccca/public_html/iz/xcri/api/venv/bin/python3.9 /home/web4ustfccca/public_html/iz/xcri/api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4
web4ust+ 1132181  0.0  0.5 ...
web4ust+ 1132182  0.0  0.5 ...
web4ust+ 1132183  0.0  0.5 ...
web4ust+ 1132184  0.0  0.5 ...
```

**Note**: Parent process + 4 worker processes

### Task 2.2: Kill Existing Processes

**Method 1: Kill by process name**
```bash
ssh ustfccca-web4 'pkill -9 -f "uvicorn main:app"'
```

**Method 2: Kill by PID (if Method 1 fails)**
```bash
ssh ustfccca-web4 'kill -9 1132178'  # Parent process will kill workers
```

**Verify processes are gone**:
```bash
ssh ustfccca-web4 'ps aux | grep uvicorn | grep -v grep'
# Should return empty
```

### Task 2.3: Start Fresh API Server

**Start uvicorn with proper configuration**:
```bash
ssh ustfccca-web4 << 'ENDSSH'
cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate

# Start uvicorn in background with 4 workers
nohup uvicorn main:app \
  --host 127.0.0.1 \
  --port 8001 \
  --workers 4 \
  --log-level info \
  > ~/logs/xcri-api.log 2>&1 &

# Wait for startup
sleep 5

# Check if processes are running
ps aux | grep "[u]vicorn main:app"
ENDSSH
```

**Expected output**: 5 processes (1 parent + 4 workers)

**Alternative: Use systemd service (if configured)**
```bash
ssh ustfccca-web4 'systemctl --user restart xcri-api && systemctl --user status xcri-api'
```

### Task 2.4: Check Startup Logs

```bash
ssh ustfccca-web4 'tail -50 ~/logs/xcri-api.log'
```

**Look for**:
- ✅ "Uvicorn running on http://127.0.0.1:8001"
- ✅ "Started server process"
- ✅ "Application startup complete"
- ✅ "XCRI Rankings API - Starting Up"
- ✅ "Async connection pool initialized successfully"
- ❌ NO import errors
- ❌ NO "ModuleNotFoundError"

---

## Phase 3: Endpoint Verification (20 minutes)

### Task 3.1: Test Health Endpoint (Baseline)

```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/health" | jq .
```

**Expected**: `{"status": "healthy", "database": "connected", ...}`

### Task 3.2: Verify Swagger UI

**Open in browser**: https://web4.ustfccca.org/iz/xcri/api/docs

**Check for**:
- [ ] `/team-knockout/` appears in endpoint list
- [ ] "team-knockout" tag exists
- [ ] All 6 endpoints visible:
  - `GET /team-knockout/`
  - `GET /team-knockout/{team_id}`
  - `GET /team-knockout/matchups`
  - `GET /team-knockout/matchups/head-to-head`
  - `GET /team-knockout/matchups/meet/{race_hnd}`
  - `GET /team-knockout/matchups/common-opponents`

### Task 3.3: Test Each Endpoint

**Test 1: List Team Knockout Rankings**
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=5" | jq '.total, (.results | length), .results[0].team_name'
```
**Expected**: Total count, 5 results, first team name

**Test 2: Get Single Team**
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/20690?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M" | jq '.team_name, .knockout_rank'
```
**Expected**: Team name and rank

**Test 3: Team Matchups**
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=20690&season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=5" | jq '.stats, (.matchups | length)'
```
**Expected**: Stats object with wins/losses, 5 matchup records

**Test 4: Head-to-Head**
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/head-to-head?team_a_id=20690&team_b_id=20710&season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M" | jq '.team_a_name, .team_b_name, .total_matchups'
```
**Expected**: Two team names, matchup count

**Test 5: Meet Matchups** (use known race_hnd from database)
```bash
# First get a race_hnd from a matchup
RACE_HND=$(curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=20690&season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1" | jq -r '.matchups[0].race_hnd')

curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/meet/${RACE_HND}?season_year=2025" | jq '.meet_name, .total_matchups'
```
**Expected**: Meet name, matchup count

**Test 6: Common Opponents**
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/common-opponents?team_a_id=20690&team_b_id=20710&season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M" | jq '.total_common_opponents'
```
**Expected**: Number of common opponents

### Task 3.4: Performance Testing

```bash
# Test response time
curl -w "Response time: %{time_total}s\n" -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=100" -o /dev/null
```

**Target**: < 0.2 seconds (200ms)

### Task 3.5: Error Handling Tests

**Test 404 - Invalid team ID**:
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/99999999?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M" | jq .
```
**Expected**: `{"detail": "Team Knockout ranking not found..."}`

**Test 400 - Same team ID for H2H**:
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/head-to-head?team_a_id=20690&team_b_id=20690&season_year=2025" | jq .
```
**Expected**: `{"detail": "team_a_id and team_b_id must be different"}`

---

## Phase 4: Create Deployment Agent (30 minutes)

### Task 4.1: Define Agent Requirements

**Agent Purpose**: Automate XCRI API server restart process

**Agent Capabilities**:
1. Check if API is running
2. Kill existing uvicorn processes safely
3. Start new uvicorn workers
4. Verify startup was successful
5. Test health endpoint
6. Report status

**Usage**:
```bash
# User invokes agent
/restart-xcri-api

# Agent performs automated restart
# Returns success/failure status
```

### Task 4.2: Create Agent Script

**Location**: `scripts/restart-xcri-api.sh`

**Script Content**:
```bash
#!/bin/bash
# XCRI API Server Restart Script
# Created: Session 016
# Purpose: Safely restart uvicorn API workers

set -e  # Exit on error

echo "============================================"
echo "XCRI API Server Restart"
echo "============================================"
echo ""

# Configuration
API_DIR="/home/web4ustfccca/public_html/iz/xcri/api"
LOG_FILE="$HOME/logs/xcri-api.log"
VENV_PATH="$API_DIR/venv"
HOST="127.0.0.1"
PORT="8001"
WORKERS="4"

# Step 1: Check current status
echo "Step 1: Checking current processes..."
CURRENT_PIDS=$(ps aux | grep "[u]vicorn main:app" | awk '{print $2}' || true)
if [ -n "$CURRENT_PIDS" ]; then
    echo "Found running processes: $CURRENT_PIDS"
else
    echo "No uvicorn processes found"
fi
echo ""

# Step 2: Kill existing processes
echo "Step 2: Stopping existing API server..."
pkill -9 -f "uvicorn main:app" 2>/dev/null || true
sleep 2

# Verify processes are gone
REMAINING=$(ps aux | grep "[u]vicorn main:app" || true)
if [ -n "$REMAINING" ]; then
    echo "ERROR: Failed to kill all processes"
    echo "$REMAINING"
    exit 1
fi
echo "✓ All processes stopped"
echo ""

# Step 3: Start new server
echo "Step 3: Starting new API server..."
cd "$API_DIR"
source "$VENV_PATH/bin/activate"

nohup uvicorn main:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info \
    > "$LOG_FILE" 2>&1 &

NEW_PID=$!
echo "Started parent process: $NEW_PID"
sleep 5
echo ""

# Step 4: Verify startup
echo "Step 4: Verifying startup..."
NEW_PIDS=$(ps aux | grep "[u]vicorn main:app" | wc -l)
if [ "$NEW_PIDS" -eq 0 ]; then
    echo "ERROR: Server failed to start"
    tail -20 "$LOG_FILE"
    exit 1
fi
echo "✓ Found $NEW_PIDS processes (1 parent + workers)"
echo ""

# Step 5: Test health endpoint
echo "Step 5: Testing health endpoint..."
sleep 3
HEALTH_RESPONSE=$(curl -s "http://$HOST:$PORT/health" || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✓ Health check passed"
else
    echo "ERROR: Health check failed"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Step 6: Summary
echo "============================================"
echo "✅ XCRI API Server Restart Complete"
echo "============================================"
echo "Processes: $NEW_PIDS"
echo "Log file: $LOG_FILE"
echo "API URL: https://web4.ustfccca.org/iz/xcri/api/"
echo ""
echo "To view logs: tail -f $LOG_FILE"
echo "To check status: ps aux | grep uvicorn"
```

**Make executable**:
```bash
ssh ustfccca-web4 'chmod +x /home/web4ustfccca/public_html/iz/xcri/scripts/restart-xcri-api.sh'
```

### Task 4.3: Test Agent

```bash
ssh ustfccca-web4 '/home/web4ustfccca/public_html/iz/xcri/scripts/restart-xcri-api.sh'
```

**Expected output**: All 5 steps complete with ✓ marks

### Task 4.4: Document Agent Usage

Add to `CLAUDE.md` under "Service Management" section:

```markdown
### Automated Restart (Recommended)

Use the restart script (Session 016):
```bash
ssh ustfccca-web4
/home/web4ustfccca/public_html/iz/xcri/scripts/restart-xcri-api.sh
```

This script safely:
1. Checks current processes
2. Kills existing uvicorn workers
3. Starts new workers with proper configuration
4. Verifies startup
5. Tests health endpoint
```

---

## Phase 5: Document Future Development Needs (15 minutes)

### Task 5.1: Create Backend Development Roadmap

**File**: `docs/roadmap/backend-future-work.md`

**Content**:
```markdown
# Backend Development - Future Work

## Team Knockout Enhancements

### Phase 1: Data Expansion (Low Priority)
- [ ] Regional Team Knockout rankings (rank_group_type='R')
- [ ] Conference Team Knockout rankings (rank_group_type='C')
- [ ] Historical snapshots for Team Knockout (checkpoint_date support)

**Effort**: 2-3 hours
**Benefit**: Complete feature parity across all ranking types

### Phase 2: Additional Endpoints (Medium Priority)
- [ ] GET `/team-knockout/standings` - Tournament-style standings view
- [ ] GET `/team-knockout/rankings-comparison` - Batch compare Team Knockout vs Team Five
- [ ] GET `/team-knockout/team/{team_id}/strength-of-schedule` - SOS analysis

**Effort**: 3-4 hours
**Benefit**: Enhanced analytics capabilities

### Phase 3: Performance Optimizations (Low Priority)
- [ ] Redis caching for frequently accessed rankings
- [ ] Materialized views for common queries
- [ ] GraphQL endpoint for flexible queries

**Effort**: 4-6 hours
**Benefit**: Improved response times for high-traffic scenarios

## Other Backend Needs

### API Versioning
- [ ] Implement `/v2/` endpoint versioning
- [ ] Deprecation notices for old endpoints
- [ ] Migration guides

### Authentication (If Needed)
- [ ] API key system for rate limiting
- [ ] OAuth for protected endpoints
- [ ] Admin-only endpoints

### Documentation
- [ ] API usage examples
- [ ] Rate limiting documentation
- [ ] Error code reference guide
```

### Task 5.2: Create Frontend Development Roadmap

**File**: `docs/roadmap/frontend-future-work.md`

**Content**:
```markdown
# Frontend Development - Future Work

## Team Knockout UI (HIGH PRIORITY - Deferred from Session 015)

### Estimated Effort: 4-6 hours

### Phase 1: Rankings Table (2 hours)
- [ ] Create `TeamKnockoutRankings.jsx` component
- [ ] Add toggle to switch between Team Five and Team Knockout views
- [ ] Display columns: Rank, Team, W-L Record, Win %, Team Five Rank (for comparison)
- [ ] Highlight rank differences (> 5 positions)
- [ ] Add sorting and filtering

### Phase 2: Matchup Display Components (2 hours)
- [ ] Create `MatchupHistory.jsx` - Team's complete matchup list
- [ ] Create `MatchupCard.jsx` - Individual matchup display
- [ ] Color-code wins (green) and losses (red)
- [ ] Show opponent name, date, score, result
- [ ] Add pagination for long histories

### Phase 3: Head-to-Head Comparison (1 hour)
- [ ] Create `HeadToHeadModal.jsx` - H2H comparison popup
- [ ] Show overall record (Team A: X-Y, Team B: Y-X)
- [ ] Display complete matchup timeline
- [ ] Latest matchup highlighted

### Phase 4: Common Opponent Analysis (1 hour)
- [ ] Create `CommonOpponentsPanel.jsx`
- [ ] List shared opponents with records
- [ ] Visual comparison chart
- [ ] Sorting by matchup count

### Phase 5: Navigation & Integration (30 min)
- [ ] Add "Team Knockout Rankings" to main navigation
- [ ] Update routing in `App.jsx`
- [ ] Add breadcrumb support
- [ ] Link from team profiles

### Phase 6: User Education (30 min)
- [ ] Add tooltips explaining Team Knockout concept
- [ ] Create FAQ section
- [ ] Add explainer box on rankings page
- [ ] Link to methodology documentation

## Other Frontend Enhancements

### Performance
- [ ] Implement virtual scrolling for long lists
- [ ] Lazy load components
- [ ] Optimize bundle size

### UX Improvements
- [ ] Dark mode support
- [ ] Mobile-specific layouts
- [ ] Print-friendly views
- [ ] Export to CSV/PDF

### Analytics
- [ ] Track user interactions with Team Knockout features
- [ ] A/B test different UI layouts
- [ ] Monitor component performance
```

---

## Phase 6: Cleanup & Verification (10 minutes)

### Task 6.1: Remove Maintenance Mode

If maintenance page was created:
```bash
ssh ustfccca-web4 'rm /home/web4ustfccca/public_html/iz/xcri/maintenance.html'
```

### Task 6.2: Final Verification Checklist

- [ ] All 6 Team Knockout endpoints responding
- [ ] Swagger UI showing new endpoints
- [ ] Health endpoint returning healthy status
- [ ] No errors in API logs
- [ ] Restart script working correctly
- [ ] Documentation updated

### Task 6.3: Update Server Status

Update any status pages or monitoring systems to show:
- ✅ Server operational
- ✅ New Team Knockout API live
- ✅ All systems normal

---

## Success Criteria

Session 016 is successful when:

1. ✅ **API Server Restarted**:
   - Uvicorn processes running cleanly
   - No import errors in logs
   - Health endpoint responding

2. ✅ **Team Knockout Endpoints Operational**:
   - All 6 endpoints return 200 OK
   - Sample data retrieved successfully
   - Error handling working correctly

3. ✅ **Deployment Agent Created**:
   - Script created and tested
   - Documented in CLAUDE.md
   - Reusable for future deployments

4. ✅ **Future Work Documented**:
   - Backend roadmap created
   - Frontend roadmap created
   - Priorities and estimates defined

---

## Post-Session Tasks

1. **Commit and Push**:
   ```bash
   git add scripts/restart-xcri-api.sh docs/roadmap/
   git commit -m "[XCRI] Session 016 - Server restart, agent creation, roadmap documentation"
   git push origin main
   ```

2. **Update CLAUDE.md**: Add Session 016 to session history

3. **Create Session 016 Wrap-Up**: Document restart procedure and results

4. **Close GitHub Issues**: If any related to deployment automation

---

## Expected Deliverables

- ✅ XCRI API server running with Team Knockout endpoints
- ✅ Restart script (`scripts/restart-xcri-api.sh`)
- ✅ Backend roadmap (`docs/roadmap/backend-future-work.md`)
- ✅ Frontend roadmap (`docs/roadmap/frontend-future-work.md`)
- ✅ Updated documentation (CLAUDE.md)
- ✅ Session 016 wrap-up document

---

## Troubleshooting Guide

### Issue: Processes won't die
**Solution**: Use `kill -9` with specific PIDs, or reboot server

### Issue: Port 8001 already in use
**Solution**: `lsof -ti:8001 | xargs kill -9`

### Issue: Import errors on startup
**Solution**: Check `tail -100 ~/logs/xcri-api.log`, verify venv activated

### Issue: Health endpoint fails
**Solution**: Check database connection, verify .env file

---

**Prompt Status**: ✅ Ready for Session 016
**Duration**: 1-2 hours
**Focus**: Server restart, verification, agent creation
**Outcome**: Fully operational Team Knockout API
