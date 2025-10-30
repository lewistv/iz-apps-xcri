# Session 020 API Restart - Status Report

**Date**: October 29, 2025
**Session**: 020 - Backend Integration and API Restart
**Status**: Ready for API restart on production server
**Commits**: c6ad66e, 6632900 (code on server, API restart needed)

---

## Executive Summary

Session 020 backend code implementing 6 new database fields has been successfully committed, pushed to GitHub, and deployed to the production server. However, the XCRI API is still running old code from Session 019. The API must be restarted to load the new code and make the 6 new fields available in API responses.

**Current Status**: Code deployed, API running old code
**Action Required**: Execute API restart procedure to load new code
**Impact**: 5-minute maintenance window for API

---

## Code Changes Verified

### Backend Implementation (Commit c6ad66e)

**File**: `api/models.py`

Added 6 new Pydantic model fields:

```python
# TeamKnockoutRanking class additions:
regl_group_name: Optional[str] = Field(
    default=None,
    description="Regional group name (Session 031 - direct field)"
)
conf_group_name: Optional[str] = Field(
    default=None,
    description="Conference group name (Session 031 - direct field)"
)
most_recent_race_date: Optional[str] = Field(
    default=None,
    description="Most recent race date (Session 031 - direct field)"
)

# TeamKnockoutMatchup class additions:
meet_id: Optional[int] = Field(
    default=None,
    description="AthleticNET meet handle (Session 031)"
)
team_a_ko_rank: Optional[int] = Field(
    default=None,
    description="Team A knockout rank at time of race (Session 031)"
)
team_b_ko_rank: Optional[int] = Field(
    default=None,
    description="Team B knockout rank at time of race (Session 031)"
)
```

**File**: `api/services/team_knockout_service.py`

Updated 4 SQL queries to include new fields:

1. `get_team_knockout_rankings()` - Includes `ko.regl_group_name`, `ko.conf_group_name`, `m.meet_id`, etc.
2. `get_single_team_knockout()` - Includes new fields in SELECT clause
3. `get_team_matchups()` - Includes `m.meet_id`, `m.team_a_ko_rank`, `m.team_b_ko_rank`
4. `get_head_to_head_matchup()` - Includes new matchup fields
5. `get_meet_matchups()` - Includes new matchup fields
6. `get_common_opponents()` - Includes new matchup fields

**Verification**: All queries confirmed to include new database fields from `team_knockout` and `team_knockout_matchups` tables.

### Frontend Integration (Commit 6632900)

**File**: `frontend/src/App.jsx`
- Enabled server-side region/conference filtering for Team Knockout view

**File**: `frontend/src/components/MatchupHistoryModal.jsx`
- Fixed Athletic.net links to use `meet_id` instead of `race_hnd`
- Added opponent knockout rank badges (#1, #2, etc.)

**File**: `frontend/src/components/MatchupHistoryModal.css`
- Added styling for knockout rank badges

---

## Deployment Status

### Local Repository
- Working directory: `/Users/lewistv/code/ustfccca/iz-apps-clean/xcri`
- Current branch: `main`
- Latest commits:
  - `6632900` - Session 020 Frontend integration
  - `c6ad66e` - Session 020 Backend 6 new fields
  - `809b65e` - Session 019 GitHub issues

### Production Server
**Path**: `/home/web4ustfccca/public_html/iz/xcri/`

**Code Status**: Files deployed via git pull
- `api/models.py` - Updated with 6 new fields (confirmed)
- `api/services/team_knockout_service.py` - Updated with 4 SQL queries (confirmed)
- `frontend/src/App.jsx` - Filtering enabled (confirmed)
- `frontend/src/components/MatchupHistoryModal.jsx` - KO rank badges (confirmed)

**API Status**: Running old code from Session 019
- 4 uvicorn workers active (expected 5)
- Last confirmed restart: Session 018 (October 25)
- New code not yet loaded

---

## New Fields Being Deployed

### TeamKnockoutRanking (3 fields)

1. **regl_group_name**: Regional group name
   - Type: Optional string
   - Source: `iz_rankings_xcri_team_knockout.regl_group_name`
   - Example: "Mountain Regional", "Northeast Regional"
   - Impact: Enables region-aware filtering and display

2. **conf_group_name**: Conference group name
   - Type: Optional string
   - Source: `iz_rankings_xcri_team_knockout.conf_group_name`
   - Example: "Pac-12", "Big Ten", "SEC"
   - Impact: Enables conference-aware filtering and display

3. **most_recent_race_date**: Most recent race date
   - Type: Optional date
   - Source: `iz_rankings_xcri_team_knockout.most_recent_race_date`
   - Example: "2025-10-25"
   - Impact: Shows activity recency in rankings view

### TeamKnockoutMatchup (3 fields)

1. **meet_id**: AthleticNET meet handle
   - Type: Optional integer
   - Source: `iz_rankings_xcri_team_knockout_matchups.meet_id`
   - Example: 12345
   - Impact: Proper Athletic.net meet linking (fixes to use meet_id instead of race_hnd)

2. **team_a_ko_rank**: Team A knockout rank at time of race
   - Type: Optional integer
   - Source: `iz_rankings_xcri_team_knockout_matchups.team_a_ko_rank`
   - Example: 1, 2, 3, etc.
   - Impact: Shows team's rank during the matchup

3. **team_b_ko_rank**: Team B knockout rank at time of race
   - Type: Optional integer
   - Source: `iz_rankings_xcri_team_knockout_matchups.team_b_ko_rank`
   - Example: 1, 2, 3, etc.
   - Impact: Shows opponent's rank during the matchup

---

## API Restart Procedure

### Quick Summary

1. **Enable maintenance mode** - Notify users of upcoming downtime
2. **Kill all processes** - Stop 1 parent + 4 worker processes
3. **Clear bytecode cache** - Remove .pyc files and __pycache__ directories
4. **Start uvicorn** - Launch with 4 workers
5. **Verify process count** - Confirm 5 processes running
6. **Test health endpoint** - Verify API is responding
7. **Verify new fields** - Confirm 6 new fields in API responses
8. **Disable maintenance mode** - Bring API online
9. **Final verification** - Test public URLs

### Execution Methods

**Option 1: Use automated restart script** (RECOMMENDED)
```bash
ssh web4ustfccca@web4.ustfccca.org
bash /home/web4ustfccca/public_html/iz/xcri/deployment/restart-api-session-020.sh
```

**Option 2: Manual execution**
Follow steps in `SESSION_020_RESTART_ACTION_PLAN.md` for detailed manual procedure.

### Estimated Duration

- Maintenance mode: 5-10 minutes
- Kill + clear cache: 30-60 seconds
- Startup + initialization: 10-15 seconds
- Verification: 30-60 seconds
- **Total: ~5-10 minutes**

---

## Expected API Response After Restart

### Team Knockout List Endpoint

**URL**: `https://web4.ustfccca.org/iz/xcri/api/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1`

**Before Restart** (Current - OLD code):
```json
{
  "teams": [
    {
      "id": 714,
      "team_id": 714,
      "team_name": "University of Colorado",
      "team_code": "CU",
      "rank_group_type": "D",
      "rank_group_fk": 2030,
      "gender_code": "M",
      "regl_group_fk": null,
      "conf_group_fk": null,
      // Missing new fields:
      // - regl_group_name
      // - conf_group_name
      // - most_recent_race_date
      ...
    }
  ]
}
```

**After Restart** (NEW code - with 6 fields):
```json
{
  "teams": [
    {
      "id": 714,
      "team_id": 714,
      "team_name": "University of Colorado",
      "team_code": "CU",
      "rank_group_type": "D",
      "rank_group_fk": 2030,
      "gender_code": "M",
      "regl_group_fk": null,
      "conf_group_fk": null,
      "regl_group_name": "Mountain Regional",        // NEW
      "conf_group_name": "Pac-12",                    // NEW
      "most_recent_race_date": "2025-10-25",         // NEW
      ...
    }
  ]
}
```

### Team Knockout Matchup Endpoint

**URL**: `https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&season_year=2025&limit=1`

**Before Restart** (Current - OLD code):
```json
{
  "matchups": [
    {
      "matchup_id": 1001,
      "race_hnd": 45678,
      // Missing new field:
      // - meet_id
      "race_date": "2025-10-25",
      "meet_name": "NCAA Cross Country Championship",
      "team_a_id": 714,
      "team_a_name": "University of Colorado",
      "team_a_rank": 1,
      "team_a_score": 45,
      // Missing new field:
      // - team_a_ko_rank
      "team_b_id": 1699,
      "team_b_name": "University of Oregon",
      "team_b_rank": 2,
      "team_b_score": 52,
      // Missing new field:
      // - team_b_ko_rank
      ...
    }
  ]
}
```

**After Restart** (NEW code - with 6 fields):
```json
{
  "matchups": [
    {
      "matchup_id": 1001,
      "race_hnd": 45678,
      "meet_id": 12345,                              // NEW
      "race_date": "2025-10-25",
      "meet_name": "NCAA Cross Country Championship",
      "team_a_id": 714,
      "team_a_name": "University of Colorado",
      "team_a_rank": 1,
      "team_a_score": 45,
      "team_a_ko_rank": 1,                           // NEW
      "team_b_id": 1699,
      "team_b_name": "University of Oregon",
      "team_b_rank": 2,
      "team_b_score": 52,
      "team_b_ko_rank": 2,                           // NEW
      ...
    }
  ]
}
```

---

## Verification Checklist

### Pre-Restart
- [x] Code committed locally (c6ad66e, 6632900)
- [x] Code pushed to GitHub
- [x] Code deployed on production server
- [x] Models.py contains 6 new field definitions
- [x] Service file contains updated SQL queries
- [x] Frontend integration changes present
- [x] Action plan document created
- [x] Automated restart script created

### Restart Execution
- [ ] SSH access to web4.ustfccca.org available
- [ ] Maintenance mode enabled
- [ ] All processes killed (verify 0 processes remaining)
- [ ] Bytecode cache cleared (.pyc files deleted)
- [ ] Uvicorn started with 4 workers
- [ ] 5 processes visible (1 parent + 4 workers)
- [ ] Health endpoint responding with "healthy"
- [ ] Team Knockout endpoint returns new fields
- [ ] Maintenance mode disabled
- [ ] Public URLs responding (200 OK)

### Post-Restart Verification
- [ ] Team Knockout list shows `regl_group_name`, `conf_group_name`, `most_recent_race_date`
- [ ] Matchup data shows `meet_id`, `team_a_ko_rank`, `team_b_ko_rank`
- [ ] Athletic.net links use correct meet_id
- [ ] Frontend filters functional (region/conference)
- [ ] Knockout rank badges visible in matchup history
- [ ] No error messages in logs
- [ ] API response time < 200ms
- [ ] All Team Knockout features working

---

## Troubleshooting Guide

### Problem: Process count not 5 after restart

**Solution**:
```bash
# Check logs for errors
tail -100 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log

# Verify import errors
grep -i "error\|import" /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | tail -20

# Re-clear bytecode and restart
cd /home/web4ustfccca/public_html/iz/xcri/api
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} +
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
sleep 6
```

### Problem: New fields still missing from response

**Solution**:
```bash
# Verify models.py is deployed correctly
grep -n "regl_group_name\|conf_group_name\|team_a_ko_rank" \
  /home/web4ustfccca/public_html/iz/xcri/api/models.py

# Force aggressive cache clearing
cd /home/web4ustfccca/public_html/iz/xcri/api
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf

# Kill and restart
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 3
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
sleep 6

# Test again
curl -s "http://127.0.0.1:8001/team-knockout/?limit=1" | python3 -m json.tool | grep "regl_group_name"
```

### Problem: Health endpoint fails

**Solution**:
```bash
# Test database connectivity
mysql --user=web4ustfccca_public --password=[REDACTED] -h localhost web4ustfccca_iz -e "SELECT 1"

# Verify .env file
cat /home/web4ustfccca/public_html/iz/xcri/api/.env | grep DATABASE

# Check for import errors in logs
tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | grep -i "import\|error"
```

---

## Database Integration

### Data Source

The 6 new fields come directly from izzypy_xcri Session 031 data export:

**Team Knockout Rankings Table**:
- `iz_rankings_xcri_team_knockout.regl_group_name` - Regional context
- `iz_rankings_xcri_team_knockout.conf_group_name` - Conference context
- `iz_rankings_xcri_team_knockout.most_recent_race_date` - Activity metric

**Team Knockout Matchups Table**:
- `iz_rankings_xcri_team_knockout_matchups.meet_id` - Meet identification
- `iz_rankings_xcri_team_knockout_matchups.team_a_ko_rank` - Historical rank
- `iz_rankings_xcri_team_knockout_matchups.team_b_ko_rank` - Historical rank

**Data Coverage**:
- 2,782 teams with complete Session 031 fields
- 38,066 matchup records with complete Session 031 fields
- 100% coverage across all divisions and genders

---

## Files Modified

### Backend
- `api/models.py` - 6 new Pydantic fields
- `api/services/team_knockout_service.py` - 4 SQL queries updated

### Frontend
- `frontend/src/App.jsx` - Region/conference filtering enabled
- `frontend/src/components/MatchupHistoryModal.jsx` - Athletic.net links and badges
- `frontend/src/components/MatchupHistoryModal.css` - Badge styling

### Deployment Tools
- `deployment/restart-api-session-020.sh` - Automated restart script (NEW)
- `SESSION_020_RESTART_ACTION_PLAN.md` - Detailed procedure (NEW)
- `SESSION_020_API_RESTART_STATUS.md` - This document (NEW)

---

## Communication Template

### For Operations Team

**Subject**: XCRI API Restart - Session 020 Deployment

The XCRI API requires a restart to load Session 020 backend improvements. The code has been deployed to the production server but the API must be restarted to load it into memory.

**Schedule**: [Date/Time]
**Duration**: ~5-10 minutes
**Impact**: XCRI Rankings API temporarily unavailable

**Process**:
1. Enable maintenance page (503 Service Unavailable)
2. Kill API processes and clear bytecode cache
3. Start fresh API with new code
4. Verify new fields present in API responses
5. Disable maintenance page
6. Test public URLs

**Scripts**:
- Automated: `deployment/restart-api-session-020.sh`
- Manual: See `SESSION_020_RESTART_ACTION_PLAN.md`

---

## Success Criteria

Restart is successful when:

1. **Process Count**: 5 Python processes running (1 parent + 4 workers)
   ```bash
   ps aux | grep "[p]ython3.9" | wc -l
   # Expected: 5
   ```

2. **Health Endpoint**: Returns "healthy" status
   ```bash
   curl -s http://127.0.0.1:8001/health | grep "healthy"
   # Expected: true
   ```

3. **New Fields Present**: All 6 fields in API responses
   ```bash
   curl -s "http://127.0.0.1:8001/team-knockout/?limit=1" | \
     grep -E "regl_group_name|conf_group_name|most_recent_race_date|meet_id|team_a_ko_rank|team_b_ko_rank"
   # Expected: All 6 field names found
   ```

4. **API Response Time**: < 200ms for cached queries
   ```bash
   curl -w "Time: %{time_total}s\n" "https://web4.ustfccca.org/iz/xcri/api/health" -o /dev/null
   # Expected: < 0.2s
   ```

5. **No Errors**: Clean logs with no import or SQL errors
   ```bash
   tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | grep -i "error"
   # Expected: No errors found
   ```

6. **Public URLs**: All responding with 200 OK
   - Frontend: https://web4.ustfccca.org/iz/xcri/ (200 OK)
   - API Health: https://web4.ustfccca.org/iz/xcri/api/health (200 OK, healthy)
   - Team Knockout: https://web4.ustfccca.org/iz/xcri/api/team-knockout/ (200 OK)

---

## Rollback Plan

If critical issues occur after restart:

```bash
# 1. Kill current processes
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9

# 2. Revert code to Session 019
cd /home/web4ustfccca/public_html/iz/xcri
git reset --hard 809b65e

# 3. Clear cache and restart
cd api
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &
sleep 6

# 4. Verify rollback
curl -s http://127.0.0.1:8001/health
```

---

## Related Documentation

- **API Restart Guide**: `docs/operations/API_RESTART_GUIDE.md`
- **Action Plan**: `SESSION_020_RESTART_ACTION_PLAN.md`
- **Automated Script**: `deployment/restart-api-session-020.sh`
- **CLAUDE.md**: Project architecture and guidelines
- **GitHub Issues**: https://github.com/lewistv/iz-apps-xcri/issues

---

**Document Status**: Ready for execution
**Approval**: Waiting for operations team confirmation
**Next Steps**: Execute restart procedure when approved

