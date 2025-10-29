# Session 017 Prompt: Fix Team Knockout Matchups Endpoint (422 Validation Error)

**Date**: October 29, 2025 (or later)
**Estimated Duration**: 30-45 minutes
**Session Type**: Bug fix - API endpoint validation error
**Prerequisites**: Session 016 complete (API restarted, 5/6 endpoints operational)

---

## Session Objective

**Fix the Team Knockout matchups history endpoint** that currently returns HTTP 422 (Unprocessable Entity) validation error instead of matchup data.

**Success Criteria**:
- ✅ GET /team-knockout/matchups endpoint returns HTTP 200 OK
- ✅ Response contains valid matchup data for test team (Iowa State, team_id=714)
- ✅ All 6 Team Knockout endpoints operational (100% success rate)
- ✅ Changes committed to GitHub and deployed to production

---

## Background

### What Was Done in Session 016
- ✅ API server successfully restarted with 4 workers
- ✅ 5/6 Team Knockout endpoints operational (83% success rate)
- ✅ Fixed 3 SQL bugs (ambiguous column references)
- ✅ Comprehensive agent documentation created
- ⚠️ **1 endpoint deferred**: GET /team-knockout/matchups (HTTP 422 validation error)

### Current Problem

**Endpoint**: `GET /team-knockout/matchups?team_id={id}&season_year={year}`

**Expected Behavior**: HTTP 200 OK with JSON array of matchup objects

**Actual Behavior**: HTTP 422 Unprocessable Entity (Pydantic validation error)

**Test Command**:
```bash
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&season_year=2025"
```

**Result**: HTTP 422 (validation error)

### Root Cause (Hypothesis)

**Likely Issue**: Pydantic response model mismatch between:
1. Service function return type in `team_knockout_service.py`
2. Route handler response model in `team_knockout.py`
3. Missing or incorrectly typed fields in response data

**Investigation Needed**:
- Compare service function return structure to expected Pydantic model
- Verify all required fields are present and correctly typed
- Check if MatchupResponse model matches database query results

---

## Pre-Session Checklist

Before starting Session 017, ensure you have:

- [ ] API server is running (verify with health check)
- [ ] 5/6 Team Knockout endpoints confirmed working
- [ ] GitHub Issue #24 reviewed ([BUG] Team Knockout matchups endpoint returns HTTP 422)
- [ ] Session 016 wrap-up document reviewed
- [ ] Local git repository up-to-date with remote

**Quick Verification**:
```bash
# Verify API is running
curl -s https://web4.ustfccca.org/iz/xcri/api/health | python3 -m json.tool

# Confirm 5 processes running on server
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9" | wc -l'  # Should return 5

# Test working endpoint (control)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1"

# Test broken endpoint (should return 422)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&season_year=2025"
```

---

## Phase 1: Investigation & Diagnosis (15 minutes)

### Task 1.1: Examine Route Handler

**File**: `api/routes/team_knockout.py`

**Find the matchups endpoint** (search for "GET /matchups"):
```python
@router.get("/matchups", ...)
async def get_team_matchups(...):
    # Check response_model parameter
    # Check what get_team_matchups() service function is called
    # Check how results are returned
```

**What to look for**:
1. Response model declared in route decorator (e.g., `response_model=MatchupListResponse`)
2. Service function call (e.g., `await team_knockout_service.get_team_matchups(...)`)
3. How service results are returned (direct return vs. wrapped in model)

### Task 1.2: Examine Service Function

**File**: `api/services/team_knockout_service.py`

**Find get_team_matchups function** (search for "async def get_team_matchups"):
```python
async def get_team_matchups(...) -> ???:
    # Check return type annotation
    # Check SQL query SELECT fields
    # Check how results are constructed
```

**What to look for**:
1. Return type annotation (what does function claim to return?)
2. SQL query SELECT clause (what fields are returned from database?)
3. How results are packaged (list of dicts? list of model instances?)
4. Field names and types in return data

### Task 1.3: Examine Pydantic Models

**File**: `api/models.py`

**Find matchup-related models** (search for "Matchup"):
```python
class MatchupResponse(BaseModel):
    # What fields are required?
    # What fields are optional?
    # What are the field types?

class MatchupListResponse(BaseModel):
    # Is there a list wrapper model?
    # Does it expect total/limit/offset fields?
```

**What to look for**:
1. Required vs. optional fields (check for `Optional[...]` or `field = None`)
2. Field type mismatches (e.g., expecting int but getting str)
3. Missing fields in service return that are required by model
4. Extra fields in service return that model doesn't expect

### Task 1.4: Compare and Identify Mismatch

**Create comparison table**:

| Source | Field Name | Field Type | Required/Optional | Present? |
|--------|-----------|------------|-------------------|----------|
| Service SQL | ... | ... | ... | Yes/No |
| Service Return | ... | ... | ... | Yes/No |
| Pydantic Model | ... | ... | Required/Optional | Yes/No |

**Common Issues**:
- Service returns `opponent_id` but model expects `team_id`
- Service returns `race_date` as string but model expects `datetime`
- Service returns `null` for required field
- Model requires `total` field but service doesn't provide it

---

## Phase 2: Fix Implementation (15 minutes)

### Task 2.1: Apply Fix

**Based on diagnosis, choose appropriate fix**:

**Option A: Fix Service Return**
```python
# If service is missing fields that model requires
# Add missing fields to SQL query or result construction

async def get_team_matchups(...):
    # Add missing SELECT fields
    # OR add fields during result construction
    results.append({
        "field_that_was_missing": value,
        ...existing fields...
    })
```

**Option B: Fix Pydantic Model**
```python
# If model is too strict or has wrong types
class MatchupResponse(BaseModel):
    # Make optional: field_name: Optional[type] = None
    # Fix type: field_name: correct_type
    # Remove field: delete field that isn't in service return
```

**Option C: Fix Route Handler**
```python
# If route handler isn't wrapping results correctly
@router.get("/matchups", response_model=CorrectModel)
async def get_team_matchups(...):
    results = await service.get_team_matchups(...)
    # If model expects wrapped response:
    return {"total": len(results), "results": results}
    # Or if model expects direct list:
    return results
```

### Task 2.2: Test Locally (If Possible)

**If running local dev server**:
```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# In another terminal
curl -s "http://localhost:8001/team-knockout/matchups?team_id=714&season_year=2025"
```

**Expected**: HTTP 200 OK with matchup data

---

## Phase 3: Deployment & Verification (10 minutes)

### Task 3.1: Deploy Fixed Files

**Deploy to production**:
```bash
# If only route handler changed
scp api/routes/team_knockout.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/routes/

# If service changed
scp api/services/team_knockout_service.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/services/

# If models changed
scp api/models.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/
```

### Task 3.2: Restart API (Quick Method)

**Use documented restart procedure** (from Session 016):
```bash
ssh ustfccca-web4 'ps aux | grep "web4ust.*python3.9" | grep -v grep | awk "{print \$2}" | xargs kill -9 2>/dev/null && \
  sleep 3 && \
  cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete 2>/dev/null && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &'

# Wait for workers to start
sleep 6
```

**Note**: For quick bug fix, maintenance mode may not be necessary (use judgment).

### Task 3.3: Verify Fix

**Test all 6 Team Knockout endpoints**:

```bash
# Test 1: List rankings (control - should still work)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=2" | python3 -m json.tool | head -20

# Test 2: Single team (control - should still work)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/714" | python3 -m json.tool | head -20

# Test 3: Matchups history (THE FIX - should now return 200)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&season_year=2025" | python3 -m json.tool | head -30

# Test 4: Head-to-head (control - should still work)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/head-to-head?team_a_id=714&team_b_id=1699&season_year=2025" | python3 -m json.tool | head -20

# Test 5: Meet matchups (control - should still work)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/meet/43308?season_year=2025" | python3 -m json.tool

# Test 6: Common opponents (control - should still work)
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups/common-opponents?team_a_id=714&team_b_id=1699&season_year=2025" | python3 -m json.tool | head -20
```

**Success Criteria**:
- All 6 tests return HTTP 200 OK
- Test 3 (matchups) returns valid JSON with matchup data
- No 422, 404, or 500 errors

---

## Phase 4: Documentation & Commit (10 minutes)

### Task 4.1: Update GitHub Issue

**Update Issue #24** with resolution:
```bash
gh issue comment 24 --repo lewistv/iz-apps-xcri --body "## Fixed in Session 017

**Root Cause**: [describe what was wrong]

**Fix Applied**: [describe what was changed]

**Testing**: All 6 Team Knockout endpoints now operational (100% success rate)

**Commit**: [commit hash]"
```

**Close Issue #24**:
```bash
gh issue close 24 --repo lewistv/iz-apps-xcri --comment "Resolved - all Team Knockout endpoints operational"
```

### Task 4.2: Update Issue #23

**Update parent issue** with Session 017 completion:
```bash
gh issue comment 23 --repo lewistv/iz-apps-xcri --body "## Session 017 Update: ✅ All 6 Endpoints Operational (100%)

**Status**: Backend 100% complete

All Team Knockout API endpoints now operational:
- ✅ GET /team-knockout/ (list)
- ✅ GET /team-knockout/{id} (single)
- ✅ GET /team-knockout/matchups (FIXED in Session 017)
- ✅ GET /team-knockout/matchups/head-to-head
- ✅ GET /team-knockout/matchups/meet/{race_hnd}
- ✅ GET /team-knockout/matchups/common-opponents

**Next**: Frontend UI implementation (deferred - extensive component work)"
```

### Task 4.3: Git Commit

**Commit the fix**:
```bash
git add api/routes/team_knockout.py api/services/team_knockout_service.py api/models.py
# (Only add files that were actually changed)

git commit -m "[XCRI] Session 017 - Fix Team Knockout matchups endpoint validation error

## Session 017 Summary
Fixed HTTP 422 validation error in Team Knockout matchups history endpoint.
All 6 Team Knockout endpoints now operational (100% success rate).

## Root Cause
[Describe specific issue - e.g., 'Pydantic model expected total field but service did not provide it']

## Fix Applied
[Describe specific changes - e.g., 'Updated service to return total count in response']

## Files Changed
- api/routes/team_knockout.py (if changed)
- api/services/team_knockout_service.py (if changed)
- api/models.py (if changed)

## Testing
All 6 Team Knockout endpoints verified:
- GET /team-knockout/ - HTTP 200 ✅
- GET /team-knockout/{id} - HTTP 200 ✅
- GET /team-knockout/matchups - HTTP 200 ✅ (FIXED)
- GET /team-knockout/matchups/head-to-head - HTTP 200 ✅
- GET /team-knockout/matchups/meet/{race_hnd} - HTTP 200 ✅
- GET /team-knockout/matchups/common-opponents - HTTP 200 ✅

## Related Issues
- Fixes #24
- Updates #23

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

### Task 4.4: Update CLAUDE.md

**Update Current Status section**:
```markdown
**Recent Session (017)**: Team Knockout matchups endpoint debug
- ✅ Fixed 422 validation error in /team-knockout/matchups endpoint
- ✅ All 6 Team Knockout endpoints operational (100% success rate)
- ✅ Root cause: [specific issue]
- ✅ Changes committed and deployed

**Previous Session (016)**: Server restart and Team Knockout deployment verification
- ✅ API server restarted with 4 workers
- ✅ Fixed 3 SQL bugs
- ✅ 5/6 endpoints operational
- ✅ Comprehensive agent documentation created

**Next Session**: Team Knockout frontend UI implementation
```

---

## Expected Outcomes

### If Session Goes Well (30-45 minutes)

1. **Diagnosis complete** (15 min):
   - Root cause identified (Pydantic model mismatch)
   - Specific field or type issue documented

2. **Fix applied** (15 min):
   - Code updated in appropriate file(s)
   - Local testing confirms fix (if possible)

3. **Deployed and verified** (10 min):
   - Files deployed to production
   - API restarted
   - All 6 endpoints tested and operational

4. **Documented** (10 min):
   - GitHub issues updated and closed
   - Git commit with clear explanation
   - CLAUDE.md updated

### If Session Encounters Issues

**Issue: Can't reproduce 422 error locally**
- Solution: Test directly on production, use API logs to debug

**Issue: Fix doesn't work on first attempt**
- Solution: Check API logs for detailed Pydantic validation error message
- May reveal additional fields or type mismatches

**Issue: Multiple fields are problematic**
- Solution: Fix one at a time, test after each change
- May require iterative deployment

---

## Key Files Reference

### Primary Investigation Files
- `api/routes/team_knockout.py` (lines ~200-250) - Matchups route handler
- `api/services/team_knockout_service.py` (lines ~250-350) - get_team_matchups function
- `api/models.py` - Search for "Matchup" models

### Supporting Files
- `docs/operations/API_RESTART_GUIDE.md` - Restart procedures
- `docs/sessions/session-016-wrap-up.md` - Previous session context
- `/Users/lewistv/code/ustfccca/izzypy_xcri/docs/integration/TEAM_KNOCKOUT_COMPLETE_REFERENCE.md` - Data model reference

### Test Data
- **Iowa State** (team_id=714): 29 matchups, 29-0 record, #1 D1 Men
- **Virginia** (team_id=1699): 43 matchups, 42-1 record, #2 D1 Men
- **Season**: 2025
- **Date range**: Aug 22 - Oct 26, 2025

---

## Quick Start Commands

**One-liner diagnosis**:
```bash
# Get detailed error from production
curl -v "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&season_year=2025" 2>&1 | grep -A 20 "HTTP/"

# Check API logs for Pydantic error details
ssh ustfccca-web4 'tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | grep -A 10 "ValidationError"'
```

**Quick fix and test cycle**:
```bash
# 1. Edit file locally
# 2. Deploy
scp api/routes/team_knockout.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/routes/

# 3. Quick restart (no maintenance mode for bug fix)
ssh ustfccca-web4 'ps aux | grep "web4ust.*python3.9" | grep -v grep | awk "{print \$2}" | xargs kill -9 && \
  sleep 3 && cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete 2>/dev/null && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 >> logs/api-live.log 2>&1 &'

# 4. Wait and test
sleep 6 && curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/matchups?team_id=714&season_year=2025" | python3 -m json.tool | head -20
```

---

## Success Checklist

At the end of Session 017, verify:

- [ ] GET /team-knockout/matchups returns HTTP 200 OK
- [ ] Response contains valid matchup data (not validation error)
- [ ] All 6 Team Knockout endpoints tested and operational
- [ ] Root cause documented and understood
- [ ] Fix deployed to production
- [ ] API restarted successfully (5 processes running)
- [ ] GitHub Issue #24 closed with resolution
- [ ] GitHub Issue #23 updated with 100% completion status
- [ ] Git commit created with clear explanation
- [ ] Git commit pushed to GitHub
- [ ] CLAUDE.md updated with Session 017 info

---

## Post-Session Notes

**Expected Session Result**: 100% Team Knockout API operational (6/6 endpoints)

**Next Major Milestone**: Frontend UI implementation for Team Knockout rankings and matchup displays (extensive component work, 4-6 hours)

**Future Considerations**:
- Monitor matchups endpoint performance with larger datasets
- Consider caching frequently requested matchup comparisons
- Evaluate need for pagination on matchup history (teams with 50+ matchups)

---

**Session 017 Quick Summary**: Fix 422 validation error, achieve 100% Team Knockout API operational status.
