# XCRI API Restart Execution Guide - Session 020

**CRITICAL**: This guide explains how to execute the API restart now that all preparation is complete.

**Situation**: Session 020 code is deployed on server but API is running old code. Restart is needed to load new code.

**Solution**: Execute the automated restart script provided.

---

## Quick Start (For Immediate Execution)

### Prerequisites
- SSH access to web4.ustfccca.org
- User: web4ustfccca

### Execution (2 Commands)

```bash
# Step 1: SSH to server
ssh web4ustfccca@web4.ustfccca.org

# Step 2: Run automated restart script
bash /home/web4ustfccca/public_html/iz/xcri/deployment/restart-api-session-020.sh
```

**Done!** Script handles everything automatically (5-10 minutes).

---

## What the Script Does (Automated)

The restart script automatically:

1. **Enables maintenance mode** - 503 Service Unavailable
2. **Kills all API processes** - Forces termination
3. **Clears bytecode cache** - Removes .pyc files
4. **Starts API fresh** - 4 workers with new code
5. **Verifies processes** - Confirms 5 processes running
6. **Tests health endpoint** - Checks API is responding
7. **Verifies new fields** - Confirms 6 new fields in API response
8. **Disables maintenance mode** - Site goes live
9. **Final verification** - Tests public URLs

**Estimated Time**: 5-10 minutes
**Output**: Color-coded, easy to follow

---

## Expected Output

When you run the script, you'll see:

```
==========================================
XCRI API Restart - Session 020
==========================================

Phase 1: Enable Maintenance Mode
✓ Maintenance mode enabled

Phase 2: Stopping all uvicorn processes
   Killed 5 processes
✓ Processes stopped (remaining: 0)

Phase 3: Clearing Python bytecode cache
   Deleted 47 .pyc files
   Deleted 8 __pycache__ directories
✓ Cache cleared (remaining: 0)

Phase 4: Starting uvicorn with 4 workers
   Parent PID: 12345
   Waiting for workers to start (6 seconds)...
✓ Uvicorn started

Phase 5: Verifying process count
✓ Process count OK (5 processes: 1 parent + 4 workers)

Phase 6: Testing health endpoint
✓ Health endpoint: OK

Phase 7: Verifying new fields in API response
   New fields check:
   - regl_group_name: yes
   - conf_group_name: yes
   - most_recent_race_date: yes
✓ All new fields present

Phase 8: Disabling maintenance mode
   Removed maintenance mode block
✓ Maintenance mode disabled

Phase 9: Final verification
   Public health endpoint: OK
   Frontend HTTP status: 200

==========================================
XCRI API Restart Complete
==========================================

Key Metrics:
  - Python processes: 5 (expected: 5)
  - Health endpoint: healthy
  - New fields present: regl_group_name, conf_group_name, most_recent_race_date
  - Maintenance mode: Disabled

Test URLs:
  - Health: https://web4.ustfccca.org/iz/xcri/api/health
  - Team Knockout: https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1
  - Frontend: https://web4.ustfccca.org/iz/xcri/

Logs:
  - API: /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log
  - Recent: tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log
```

---

## What Gets Deployed (The 6 New Fields)

### TeamKnockoutRanking (3 fields)

```json
{
  "team_name": "University of Colorado",
  "regl_group_name": "Mountain Regional",        // NEW
  "conf_group_name": "Pac-12",                    // NEW
  "most_recent_race_date": "2025-10-25"          // NEW
}
```

### TeamKnockoutMatchup (3 fields)

```json
{
  "race_hnd": 45678,
  "meet_id": 12345,                              // NEW
  "team_a_name": "University of Colorado",
  "team_a_ko_rank": 1,                           // NEW
  "team_b_name": "University of Oregon",
  "team_b_ko_rank": 2                            // NEW
}
```

---

## Post-Restart Verification

After the script completes, verify success:

### Test 1: Health Endpoint
```bash
curl https://web4.ustfccca.org/iz/xcri/api/health
```
**Expected**: HTTP 200, `"status": "healthy"`

### Test 2: Team Knockout Rankings
```bash
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1" | python3 -m json.tool
```
**Expected**: Response includes `regl_group_name`, `conf_group_name`, `most_recent_race_date`

### Test 3: Team Knockout Matchups
```bash
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&limit=1" | python3 -m json.tool
```
**Expected**: Response includes `meet_id`, `team_a_ko_rank`, `team_b_ko_rank`

### Test 4: Frontend
```bash
curl https://web4.ustfccca.org/iz/xcri/
```
**Expected**: HTTP 200, page loads without errors

---

## Troubleshooting (If Script Reports Issues)

### Issue: "Process count: WARNING (Expected 5 processes, found X)"

**Solution**:
```bash
# Check logs for startup errors
tail -100 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log

# Look for: ImportError, ModuleNotFoundError, database connection error

# Manually restart with aggressive cache clearing
cd /home/web4ustfccca/public_html/iz/xcri/api
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null
sleep 3

# Extra aggressive cache clearing
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf

# Start again
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
sleep 6

# Check if fixed
ps aux | grep "[p]ython3.9" | wc -l  # Should be 5
curl -s http://127.0.0.1:8001/health  # Should work
```

### Issue: "Health endpoint: FAILED"

**Solution**:
```bash
# Test database connection
mysql --user=web4ustfccca_public --password=[REDACTED] -h localhost web4ustfccca_iz -e "SELECT 1"

# Check if database is responsive
# If no output, database may be unreachable

# Check API logs
tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | grep -i "database\|error"

# Verify .env file has correct credentials
cat /home/web4ustfccca/public_html/iz/xcri/api/.env | grep DATABASE_
```

### Issue: "All new fields present: NO"

**Solution**:
```bash
# Force aggressive restart
cd /home/web4ustfccca/public_html/iz/xcri/api
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 3

# Triple-check bytecode is gone
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Verify files are deployed
grep -c "regl_group_name\|conf_group_name" models.py
# Should find references

# Restart
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
sleep 6

# Test
curl -s "http://127.0.0.1:8001/team-knockout/?limit=1" | python3 -m json.tool | grep "regl_group_name"
```

---

## If Restart Fails Critically

### Rollback to Session 019 (< 5 minutes)

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/public_html/iz/xcri

# Revert code to Session 019
git reset --hard 809b65e

# Kill processes
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 3

# Clear cache
cd api
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Restart
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
sleep 6

# Verify
curl -s http://127.0.0.1:8001/health
```

---

## Success Checklist

After restart completes and verification passes:

- [ ] Script reported: "XCRI API Restart Complete"
- [ ] Process count: 5 (1 parent + 4 workers)
- [ ] Health endpoint: healthy
- [ ] All 6 new fields present: YES
- [ ] Maintenance mode: Disabled
- [ ] Public URLs: 200 OK
- [ ] No errors in logs
- [ ] Team Knockout endpoint responds
- [ ] Matchup data includes new fields
- [ ] Frontend loads without errors

---

## Documentation Files

For detailed information, see:

1. **SESSION_020_FINAL_REPORT.md** - Executive summary
2. **SESSION_020_API_RESTART_STATUS.md** - Complete status and verification
3. **SESSION_020_RESTART_ACTION_PLAN.md** - Detailed 9-phase procedure
4. **docs/operations/API_RESTART_GUIDE.md** - Production guide

---

## Summary

**Restart Script Location**:
```
/home/web4ustfccca/public_html/iz/xcri/deployment/restart-api-session-020.sh
```

**Execution Command**:
```bash
ssh web4ustfccca@web4.ustfccca.org
bash /home/web4ustfccca/public_html/iz/xcri/deployment/restart-api-session-020.sh
```

**Expected Duration**: 5-10 minutes
**Success Indicator**: All 6 new fields in API response
**Risk Level**: LOW (fully automated, verification built-in)
**Rollback**: < 5 minutes if needed

---

**Ready to Execute?**

1. ✓ Review this guide
2. ✓ SSH to web4.ustfccca.org
3. ✓ Run the restart script
4. ✓ Monitor output
5. ✓ Verify success
6. ✓ Test public URLs

**Questions?** Check SESSION_020_RESTART_ACTION_PLAN.md for detailed steps.

