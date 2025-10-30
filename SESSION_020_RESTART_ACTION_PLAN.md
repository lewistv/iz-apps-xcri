# Session 020 API Restart Action Plan

**Date**: October 29, 2025
**Status**: Code committed and deployed on server, API restart required
**Goal**: Restart XCRI API to load 6 new fields from backend code (commits c6ad66e and 6632900)

---

## Executive Summary

**Situation**:
- Session 020 backend code adding 6 new fields has been committed and pushed to GitHub
- Code has been pulled to production server (`/home/web4ustfccca/public_html/iz/xcri/`)
- XCRI API is still running OLD code from Session 019
- New fields are NOT appearing in Team Knockout API responses

**Root Cause**:
API workers are still executing bytecode from previous deployment. When uvicorn processes started, the new code had not yet been deployed. Python bytecode cache (.pyc files) preserves the old code.

**Solution**:
Follow the documented API restart procedure (see API_RESTART_GUIDE.md) to:
1. Enable maintenance mode
2. Kill all 5 uvicorn processes (1 parent + 4 workers)
3. Clear Python bytecode cache (.pyc files and __pycache__ directories)
4. Start fresh uvicorn with 4 workers
5. Verify new code is loaded
6. Test the new fields appear in API responses
7. Disable maintenance mode

---

## Code Changes Summary

### Backend Changes (Commit c6ad66e)

**File**: `api/models.py`
- Added 3 fields to `TeamKnockoutRanking` model:
  - `regl_group_name: Optional[str]` - Regional group name
  - `conf_group_name: Optional[str]` - Conference group name
  - `most_recent_race_date: Optional[str]` - Most recent race date

- Added 3 fields to `TeamKnockoutMatchup` model:
  - `meet_id: Optional[int]` - AthleticNET meet handle
  - `team_a_ko_rank: Optional[int]` - Team A knockout rank at time of race
  - `team_b_ko_rank: Optional[int]` - Team B knockout rank at time of race

**File**: `api/services/team_knockout_service.py`
- Updated 4 SQL queries to include new fields from `team_knockout` and `team_knockout_matchups` tables
- Removed JOIN logic for region/conference names (now direct fields)
- Performance improvement: Direct field access instead of complex JOINs

### Frontend Changes (Commit 6632900)

**File**: `frontend/src/App.jsx`
- Enable server-side region/conference filtering for Team Knockout view
- Filters now functional with backend data

**File**: `frontend/src/components/MatchupHistoryModal.jsx`
- Fix Athletic.net links to use `meet_id` instead of `race_hnd`
- Add opponent knockout rank badges (#1, #2, etc.)

**File**: `frontend/src/components/MatchupHistoryModal.css`
- Add styling for knockout rank badges

---

## Verification: Code is Ready on Server

The code is confirmed deployed on production server:

```bash
# Check files exist and are recent
ls -lh /home/web4ustfccca/public_html/iz/xcri/api/models.py
ls -lh /home/web4ustfccca/public_html/iz/xcri/api/services/team_knockout_service.py
ls -lh /home/web4ustfccca/public_html/iz/xcri/api/main.py

# Confirm repository is on correct commits
cd /home/web4ustfccca/public_html/iz/xcri
git log --oneline -3
# Should show: 6632900, c6ad66e, 809b65e
```

---

## Expected Test Result After Restart

### Before Restart (Current State)
```bash
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1"
```

**Current response** (OLD code):
```json
{
  "teams": [
    {
      "id": 714,
      "team_id": 714,
      "team_name": "University of Colorado",
      "rank_group_type": "D",
      "rank_group_fk": 2030,
      "gender_code": "M",
      // Missing: regl_group_name, conf_group_name, most_recent_race_date
    }
  ]
}
```

### After Restart (Expected)
```json
{
  "teams": [
    {
      "id": 714,
      "team_id": 714,
      "team_name": "University of Colorado",
      "rank_group_type": "D",
      "rank_group_fk": 2030,
      "gender_code": "M",
      "regl_group_name": "Mountain Regional",
      "conf_group_name": "Pac-12",
      "most_recent_race_date": "2025-10-25"
      // New fields now present!
    }
  ]
}
```

---

## Step-by-Step Restart Procedure

### Phase 1: Enable Maintenance Mode (User-Friendly)

SSH to server and edit `.htaccess` to add maintenance redirect:

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/public_html/iz/xcri

# Backup current .htaccess
cp .htaccess .htaccess.backup-20251029

# Add maintenance mode block at top of .htaccess
cat > .htaccess.maintenance << 'EOF'
# ==========================================
# MAINTENANCE MODE - Session 020 Restart
# API update in progress, expected downtime: 5 minutes
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

# Combine with existing .htaccess
cat .htaccess.maintenance .htaccess > .htaccess.new
mv .htaccess.new .htaccess

# Verify (should get 503 response)
curl -I https://web4.ustfccca.org/iz/xcri/
# Expected: HTTP/1.1 503 Service Temporarily Unavailable
```

### Phase 2: Kill All Running Processes

```bash
# Pattern match to kill all uvicorn processes
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# Wait for full termination
sleep 3

# Verify all killed (should return 0 or near 0)
ps aux | grep "[p]ython3.9" | wc -l
```

### Phase 3: Clear Python Bytecode Cache

```bash
cd /home/web4ustfccca/public_html/iz/xcri/api

# Delete all .pyc files
find . -name "*.pyc" -delete 2>/dev/null

# Delete all __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Verify cache cleared
find . -name "*.pyc" | wc -l  # Should return 0
find . -type d -name __pycache__ | wc -l  # Should return 0
```

### Phase 4: Start Uvicorn with 4 Workers

```bash
cd /home/web4ustfccca/public_html/iz/xcri/api

# Activate virtual environment
source venv/bin/activate

# Start uvicorn with 4 workers in background
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &

# Wait for workers to initialize (6-8 seconds)
sleep 6

echo "Uvicorn startup command executed"
```

### Phase 5: Verification - Process Count

```bash
# Check process count (expect 5: 1 parent + 4 workers)
ps aux | grep "[p]ython3.9" | wc -l

# Expected: 5
# If less: Check logs (see Troubleshooting)
# If more: Old processes not killed (repeat Phase 2)
```

**Success Criteria**:
```bash
ps aux | grep "[p]ython3.9"
# Should show 5 lines with approximately similar timestamps
```

### Phase 6: Verification - Health Endpoint

```bash
# Test localhost (direct to uvicorn)
curl -s http://127.0.0.1:8001/health | python3 -m json.tool

# Expected response:
# {
#     "status": "healthy",
#     "api_version": "2.0.0",
#     "database_connected": true,
#     ...
# }
```

### Phase 7: Verification - New Fields in API Response

Test the Team Knockout endpoint to confirm new fields are present:

```bash
# Test 1: Direct to uvicorn (localhost)
curl -s "http://127.0.0.1:8001/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1" | python3 -m json.tool

# Test 2: Through public URL
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1" | python3 -m json.tool
```

**Success Criteria** - Response includes new fields:
```json
{
  "teams": [
    {
      "id": 714,
      "team_name": "University of Colorado",
      "regl_group_name": "Mountain Regional",        // NEW
      "conf_group_name": "Pac-12",                    // NEW
      "most_recent_race_date": "2025-10-25"          // NEW
    }
  ]
}
```

### Phase 8: Disable Maintenance Mode

Only proceed AFTER all verification passes successfully!

```bash
cd /home/web4ustfccca/public_html/iz/xcri

# Remove maintenance mode block (typically lines 2-12 of .htaccess)
# Manual approach: Edit .htaccess and remove the maintenance block

# Or automatic approach: restore backup and manually re-add production rules
# cp .htaccess.backup-20251029 .htaccess

# Verify removal
head -20 /home/web4ustfccca/public_html/iz/xcri/.htaccess
# Should NOT contain "MAINTENANCE MODE" text
```

### Phase 9: Final Public URL Verification

```bash
# Test frontend
curl -I https://web4.ustfccca.org/iz/xcri/
# Expected: HTTP/1.1 200 OK

# Test API health through public URL
curl -s https://web4.ustfccca.org/iz/xcri/api/health | python3 -m json.tool

# Test Team Knockout with new fields
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1" | python3 -m json.tool
```

---

## Troubleshooting

### Issue: Process count is less than 5

**Symptom**: `ps aux | grep [p]ython3.9 | wc -l` returns 1-4

**Cause**: Workers failed to start (likely import error or missing dependency)

**Fix**:
```bash
# 1. Check logs for error messages
tail -100 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log

# Look for:
# - ImportError: cannot import name...
# - ModuleNotFoundError...
# - Database connection failed
# - Missing environment variable

# 2. If import error related to Session 020 changes:
# - Verify models.py was deployed correctly
# - Check that team_knockout_service.py references new fields

# 3. Re-run Phase 3 (bytecode clearing) aggressively
cd /home/web4ustfccca/public_html/iz/xcri/api
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# 4. Restart again (repeat Phase 2-4)
```

### Issue: Health endpoint fails or shows "Database not connected"

**Symptom**:
```
curl: (7) Failed to connect to 127.0.0.1 port 8001
# OR
{"status": "unhealthy", "database_connected": false}
```

**Cause**: Database connection issue or API didn't start

**Fix**:
```bash
# 1. Test database connectivity manually
mysql --user=web4ustfccca_public --password=[REDACTED] -h localhost web4ustfccca_iz -e "SELECT 1"

# 2. Check .env file in api directory
cat /home/web4ustfccca/public_html/iz/xcri/api/.env | grep DATABASE
# Should show valid connection parameters

# 3. Check log for detailed error
tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | grep -i error

# 4. Verify venv is properly activated
source /home/web4ustfccca/public_html/iz/xcri/api/venv/bin/activate
python --version  # Should be 3.9+
```

### Issue: New fields still not in API response

**Symptom**: Response shows new fields as `null` or fields missing entirely

**Cause**:
- Code didn't reload (workers still running old bytecode)
- Database schema missing new fields
- Service file not properly updated

**Fix**:
```bash
# 1. Force aggressive bytecode clearing
cd /home/web4ustfccca/public_html/iz/xcri/api
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf

# 2. Verify deployment of modified files
grep -n "regl_group_name\|conf_group_name\|most_recent_race_date" \
  /home/web4ustfccca/public_html/iz/xcri/api/models.py

# Should find references in both TeamKnockoutRanking and TeamKnockoutMatchup classes

# 3. Kill and restart processes
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null
sleep 3

cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &

sleep 6

# 4. Verify new code is loaded
curl -s http://127.0.0.1:8001/team-knockout/?limit=1 | python3 -m json.tool | grep -E "regl_group_name|conf_group_name|most_recent_race_date"
```

---

## Maintenance Window Communication

**For Users**:
- Expected downtime: 5 minutes
- Operations: API server restart to load new features
- Users will see maintenance page during restart
- No data loss - all rankings preserved

**Communication Template**:
```
Subject: XCRI Scheduled Maintenance - Session 020 API Restart

The XCRI Rankings API will be temporarily unavailable for approximately 5 minutes on October 29, 2025 while we deploy Session 020 improvements.

Expected Downtime: ~13:00-13:05 UTC

What's New:
- Regional and Conference filtering now fully functional
- Team Knockout rankings include regional/conference context
- Head-to-head matchup data now includes knockout rank at time of match
- Athletic.net meet links improved with meet_id

We apologize for any inconvenience.
```

---

## Post-Restart Verification Checklist

- [ ] All 5 Python processes running (1 parent + 4 workers)
- [ ] Health endpoint returns "healthy" status
- [ ] Team Knockout endpoint returns 200 OK
- [ ] New field `regl_group_name` present in response
- [ ] New field `conf_group_name` present in response
- [ ] New field `most_recent_race_date` present in response
- [ ] New field `meet_id` present in matchup response
- [ ] New fields `team_a_ko_rank` and `team_b_ko_rank` present in matchup response
- [ ] Frontend loads without errors
- [ ] Maintenance mode disabled
- [ ] Public URL testing successful
- [ ] No errors in logs
- [ ] API responding within acceptable time (<100ms for cached queries)

---

## Files Deployed

**Backend**:
- `api/models.py` - 6 new Pydantic fields added
- `api/services/team_knockout_service.py` - 4 SQL queries updated
- `api/main.py` - Router registration (unchanged)

**Frontend**:
- `frontend/src/App.jsx` - Region/conference filtering enabled
- `frontend/src/components/MatchupHistoryModal.jsx` - Athletic.net links fixed, KO rank badges added
- `frontend/src/components/MatchupHistoryModal.css` - Badge styling

**Configuration**:
- `.htaccess` - No changes needed for Session 020
- `api/.env` - No changes needed

---

## Rollback Procedure (If Needed)

If restart causes critical issues:

```bash
# 1. Kill current processes
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9

# 2. Restore previous code
cd /home/web4ustfccca/public_html/iz/xcri
git reset --hard 809b65e  # Revert to Session 019 commit

# 3. Clear cache
cd api
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# 4. Restart API
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &

sleep 6

# 5. Verify health
curl -s http://127.0.0.1:8001/health
```

---

## Success Criteria

**Restart is successful when**:
1. API starts without errors
2. 5 Python processes visible: `ps aux | grep [p]ython3.9 | wc -l` returns 5
3. Health endpoint: `curl http://127.0.0.1:8001/health` returns JSON with `"status": "healthy"`
4. Team Knockout endpoint includes 6 new fields in response
5. Public URLs respond correctly
6. No error messages in logs
7. Maintenance mode disabled
8. All Team Knockout features functional (filtering, sorting, modals)

---

**Document Version**: 1.0
**Created**: October 29, 2025 (Session 020)
**Purpose**: Complete API restart action plan with verification steps
