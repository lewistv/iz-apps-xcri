# Session 015 Prompt: Team Knockout Ranking Implementation

**Date**: October 29, 2025 (or later)
**Estimated Duration**: 2-3 hours
**Session Type**: Feature development and deployment

---

## Session Objective

Implement a new **Team Knockout ranking** system for the XCRI web application. This involves:

1. **Gathering requirements** - Understand the Team Knockout ranking methodology
2. **Database investigation** - Determine if data exists or if new tables are needed
3. **API implementation** - Create `/team-knockout/` endpoints
4. **Frontend development** - Build UI for Team Knockout rankings
5. **Deployment** - Deploy complete feature to production

---

## Background Context

### Current Team Ranking Systems

The XCRI application currently has two team ranking approaches:

1. **Team Five Rankings** (`/team-five/`)
   - Traditional top-5 scoring method
   - Uses athletes 1-5 from each team
   - Endpoint created in Session 013b

2. **Team Rankings** (`/teams/`)
   - Original team ranking endpoint
   - Current production system

### New System: Team Knockout

**User Request**: "The next session will concentrate on getting details about the new Team Knockout ranking and implementing a new API tract and deploying to the server."

**Key Questions to Answer**:
- What is the Team Knockout ranking methodology?
- How is it calculated differently from Team Five?
- What data is required?
- Is the algorithm ready in `izzypy_xcri`?
- What database tables exist or are needed?

---

## Pre-Session Checklist

Before starting Session 015, ensure you have:

- [ ] Access to `izzypy_xcri` repository (`/Users/lewistv/code/ustfccca/izzypy_xcri`)
- [ ] Understanding of Team Knockout ranking algorithm
- [ ] Database schema knowledge (existing tables for Team Knockout data)
- [ ] User clarification on requirements and timeline

---

## Phase 1: Requirements Gathering (30-45 minutes)

### Task 1.1: Understand Team Knockout Algorithm

**Questions to ask user**:

1. **Methodology**:
   - What is the Team Knockout ranking algorithm?
   - How does it differ from Team Five rankings?
   - What athletes/performances count toward the ranking?
   - Are there specific rules or edge cases?

2. **Data Sources**:
   - Does the data already exist in the database?
   - What table(s) contain Team Knockout rankings?
   - Is the data current (2025 season)?
   - How frequently is it updated?

3. **Algorithm Status**:
   - Is the algorithm implemented in `izzypy_xcri`?
   - What script/module calculates Team Knockout rankings?
   - Has it been run for the current season?
   - What's the export format (MySQL, Excel, both)?

4. **Feature Requirements**:
   - Should it mirror Team Five features (filters, pagination, search)?
   - Any unique features needed for Team Knockout?
   - Should historical snapshots include Team Knockout?

### Task 1.2: Database Investigation

**Check for existing tables**:

```bash
# Connect to database
mysql -h localhost -u web4ustfccca_public -p web4ustfccca_iz

# Search for Team Knockout tables
SHOW TABLES LIKE '%knockout%';
SHOW TABLES LIKE '%team%';

# Check existing team ranking tables
DESCRIBE xcri_team_rankings_current;
DESCRIBE xcri_team_rankings_2024;
DESCRIBE xcri_team_rankings_2025;

# Look for knockout-specific columns
SHOW COLUMNS FROM xcri_team_rankings_current LIKE '%knockout%';
```

**Expected findings**:
- Existing table: `xcri_team_knockout_rankings_current` (or similar)
- OR: Knockout score as column in `xcri_team_rankings_current`
- OR: Needs new table creation (coordinate with izzypy_xcri)

### Task 1.3: Review izzypy_xcri Code

**Check algorithm implementation**:

```bash
cd /Users/lewistv/code/ustfccca/izzypy_xcri

# Search for knockout-related code
grep -r "knockout" --include="*.py"
grep -r "team_knockout" --include="*.py"

# Check batch ranking scripts
ls -la batch_*.py
cat batch_xcri_rankings.py | grep -A 10 "knockout"

# Check for database export scripts
ls -la database/
grep -r "team_knockout" database/
```

**Document findings**:
- Algorithm location and status
- Database export capability
- Data freshness and update schedule

---

## Phase 2: API Implementation (60-90 minutes)

### Task 2.1: Create Database Service

**File**: `api/services/team_knockout_service.py`

**Requirements**:
- Async database queries using aiomysql
- Similar structure to `team_service.py`
- Support for filters: division, gender, region, conference
- Pagination support
- Search functionality
- Error handling

**Key Functions**:
```python
async def get_team_knockout_rankings(
    division: Optional[str] = None,
    gender: Optional[str] = None,
    region: Optional[str] = None,
    conference: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 25
) -> Dict[str, Any]

async def get_team_knockout_by_id(
    team_hnd: int,
    season_year: Optional[int] = None,
    division: Optional[str] = None,
    gender: Optional[str] = None
) -> Optional[Dict[str, Any]]
```

### Task 2.2: Create API Routes

**File**: `api/routes/team_knockout.py`

**Pattern**: Follow existing `team_five.py` structure

**Endpoints**:
1. `GET /team-knockout/` - List team knockout rankings
2. `GET /team-knockout/{team_hnd}` - Get specific team
3. `GET /team-knockout/{team_hnd}/resume` - Get season resume (if applicable)

**Router Configuration**:
```python
router = APIRouter(
    prefix="/team-knockout",
    tags=["team-knockout"],
    responses={
        404: {"model": ErrorResponse, "description": "Team not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
```

### Task 2.3: Register Routes in main.py

**File**: `api/main.py`

**Changes**:
1. Import team_knockout router
2. Include router in application
3. Add to API documentation

```python
# Line ~35: Add to imports
from routes import athletes, teams, team_five, team_knockout, metadata, snapshots, scs, components, feedback

# Line ~250: Register router
app.include_router(team_knockout.router)  # Session 015: Team Knockout Rankings API
```

### Task 2.4: Update Pydantic Models (if needed)

**File**: `api/models.py`

**Check if new models needed**:
- TeamKnockoutRanking (if structure differs from TeamRanking)
- TeamKnockoutListResponse (if additional fields needed)

**Most likely**: Can reuse existing TeamRanking models

---

## Phase 3: Frontend Implementation (45-60 minutes)

### Task 3.1: Update API Service

**File**: `frontend/src/services/api.js`

**Add functions**:
```javascript
// Team Knockout Rankings
export const getTeamKnockout = async (params = {}) => {
  const response = await apiClient.get('/team-knockout/', { params });
  return response.data;
};

export const getTeamKnockoutById = async (teamHnd, params = {}) => {
  const response = await apiClient.get(`/team-knockout/${teamHnd}`, { params });
  return response.data;
};

export const getTeamKnockoutResume = async (teamHnd, params = {}) => {
  const response = await apiClient.get(`/team-knockout/${teamHnd}/resume`, { params });
  return response.data;
};
```

### Task 3.2: Add Navigation

**File**: `frontend/src/App.jsx`

**Update navigation**:
- Add "Team Knockout Rankings" link to main menu
- Position appropriately (likely after Team Five Rankings)
- Update breadcrumb system

### Task 3.3: Create/Update Components

**Determine approach**:

**Option A**: Reuse existing TeamTable component
- Pass `rankingType="team-knockout"` prop
- Component calls appropriate API based on type
- Minimal code changes

**Option B**: Create dedicated TeamKnockoutTable component
- Full control over display and features
- Easier to customize if Knockout differs significantly
- More code duplication

**Recommendation**: Start with Option A (reuse), move to Option B if needed

**File**: `frontend/src/components/TeamTable.jsx` (if Option A)

**Changes**:
- Add `rankingType` prop (default: "team-five")
- Use appropriate API call based on rankingType
- Update title/description based on type

### Task 3.4: Add Route

**File**: `frontend/src/App.jsx`

**Add route**:
```jsx
<Route
  path="/team-knockout"
  element={<TeamTable rankingType="team-knockout" title="Team Knockout Rankings" />}
/>
```

---

## Phase 4: Testing (30 minutes)

### Task 4.1: Backend API Testing

**Test all endpoints**:

```bash
# Health check
curl https://web4.ustfccca.org/iz/xcri/api/health

# List team knockout rankings
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?division=2030&gender=M&limit=10"

# Get specific team
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/123?season_year=2025&division=2030&gender=M"

# Test filters
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?region=3&conference=Atlantic%20Coast"

# Test pagination
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?page=2&limit=25"

# Test search
curl "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?search=Stanford"
```

**Verify**:
- [ ] 200 OK responses
- [ ] Correct data returned
- [ ] Pagination works
- [ ] Filters apply correctly
- [ ] Search finds teams
- [ ] Error handling (404 for invalid IDs)

### Task 4.2: Frontend Testing

**Test in browser**:

1. **Navigation**:
   - [ ] Link appears in menu
   - [ ] Clicking navigates to Team Knockout page
   - [ ] Breadcrumb shows correct path

2. **Data Display**:
   - [ ] Table loads with data
   - [ ] Columns display correctly
   - [ ] Rankings show properly
   - [ ] Team names are clickable

3. **Filters**:
   - [ ] Division filter works
   - [ ] Gender filter works
   - [ ] Region filter works (if implemented)
   - [ ] Conference filter works (if implemented)
   - [ ] Filters persist in URL

4. **Pagination**:
   - [ ] Next/Previous buttons work
   - [ ] Page numbers update correctly
   - [ ] First/Last buttons work (if implemented)
   - [ ] Items per page selector works

5. **Search**:
   - [ ] Search input appears
   - [ ] Search filters results
   - [ ] Clear (X) button works
   - [ ] Debouncing works (doesn't search on every keystroke)

6. **Team Details**:
   - [ ] Clicking team name opens detail page
   - [ ] Team information displays
   - [ ] Season resume appears (if applicable)
   - [ ] Back navigation works

### Task 4.3: Performance Testing

**Measure response times**:

```bash
# Backend API
curl -w "Response time: %{time_total}s\n" -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/" -o /dev/null

# Frontend page load
# Use browser DevTools Network tab
# Target: < 2 seconds total load time
```

**Targets**:
- API response: < 200ms (database query)
- Page load: < 2 seconds (complete render)
- Filter changes: < 300ms (client-side + API)

---

## Phase 5: Deployment (30 minutes)

### Task 5.1: Backend Deployment

**Steps**:

```bash
# 1. Commit backend changes
git add api/services/team_knockout_service.py
git add api/routes/team_knockout.py
git add api/main.py
git commit -m "[XCRI] Session 015 - Add Team Knockout ranking API endpoints

Implements new Team Knockout ranking system with full API support.

Changes:
- NEW: api/services/team_knockout_service.py - Team Knockout data service
- NEW: api/routes/team_knockout.py - /team-knockout/ API endpoints
- UPDATED: api/main.py - Register team_knockout router

Endpoints:
- GET /team-knockout/ - List team knockout rankings
- GET /team-knockout/{team_hnd} - Get specific team
- GET /team-knockout/{team_hnd}/resume - Get season resume

Features:
- Division, gender, region, conference filtering
- Pagination and search
- Async/await with connection pooling
- Consistent with existing team endpoints

Session: 015 - Team Knockout Ranking Implementation

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main

# 2. Deploy to server
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
  api/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/

# 3. Restart API workers
ssh ustfccca-web4
cd /home/web4ustfccca/public_html/iz/xcri/api
pkill -f "uvicorn main:app"
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 > /dev/null 2>&1 &
exit
```

### Task 5.2: Frontend Deployment

**Steps**:

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Deploy build to server
rsync -avz dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

# 3. Verify deployment
curl https://web4.ustfccca.org/iz/xcri/

# 4. Commit frontend changes
cd ..
git add frontend/src/services/api.js
git add frontend/src/App.jsx
git add frontend/src/components/TeamTable.jsx
git commit -m "[XCRI] Session 015 - Add Team Knockout frontend implementation

Adds Team Knockout ranking display to frontend.

Changes:
- UPDATED: frontend/src/services/api.js - Team Knockout API methods
- UPDATED: frontend/src/App.jsx - Navigation and routing
- UPDATED: frontend/src/components/TeamTable.jsx - Support for knockout type

Features:
- Team Knockout rankings table
- Full filter/search/pagination support
- Navigation integration
- Reuses existing components

Session: 015 - Team Knockout Ranking Implementation

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

### Task 5.3: Post-Deployment Verification

**Complete testing checklist**:

- [ ] API endpoints respond (https://web4.ustfccca.org/iz/xcri/api/docs)
- [ ] Frontend loads Team Knockout page
- [ ] Data displays correctly
- [ ] Filters work
- [ ] Pagination works
- [ ] Search works
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Performance acceptable (< 2s page load)

---

## Phase 6: Documentation (20 minutes)

### Task 6.1: Update API Documentation

**File**: Update OpenAPI/Swagger docs (automatically generated)

**Verify**:
- [ ] `/team-knockout/` endpoints appear in docs
- [ ] Request/response schemas documented
- [ ] Examples provided
- [ ] Filters documented

### Task 6.2: Update README and CLAUDE.md

**File**: `README.md`

**Add section**:
```markdown
### Team Knockout Rankings

Endpoint: `/team-knockout/`

Features:
- Team knockout ranking methodology
- Full filtering (division, gender, region, conference)
- Pagination and search
- Individual team details
```

**File**: `CLAUDE.md`

**Update current status section**:
- Update "Current Status" with Session 015
- Add Team Knockout to feature list
- Update endpoint count (now 18 total)

### Task 6.3: Create Session Wrap-Up

**File**: `docs/sessions/session-015-wrap-up.md`

**Contents**:
- Objective and background
- Team Knockout algorithm explanation
- Database tables used
- API endpoints created
- Frontend changes
- Testing results
- Deployment details
- Session statistics

---

## Expected Deliverables

At the end of Session 015, you should have:

### Code Deliverables
- ✅ `api/services/team_knockout_service.py` - Data service
- ✅ `api/routes/team_knockout.py` - API routes
- ✅ `api/main.py` - Router registration
- ✅ `frontend/src/services/api.js` - API client methods
- ✅ `frontend/src/App.jsx` - Navigation and routing
- ✅ `frontend/src/components/TeamTable.jsx` - Component updates (if Option A)
- ✅ `docs/sessions/session-015-wrap-up.md` - Session documentation

### Deployment Deliverables
- ✅ Backend deployed to production
- ✅ Frontend built and deployed
- ✅ API workers restarted
- ✅ All tests passing

### Documentation Deliverables
- ✅ API documentation (auto-generated Swagger)
- ✅ README.md updated
- ✅ CLAUDE.md updated
- ✅ Session wrap-up document

### GitHub Deliverables
- ✅ 2 commits pushed (backend + frontend)
- ✅ Descriptive commit messages
- ✅ No new issues (unless bugs found)

---

## Commit Message Templates

### Backend Commit
```
[XCRI] Session 015 - Add Team Knockout ranking API endpoints

Implements new Team Knockout ranking system with full API support.

Changes:
- NEW: api/services/team_knockout_service.py - Team Knockout data service
- NEW: api/routes/team_knockout.py - /team-knockout/ API endpoints
- UPDATED: api/main.py - Register team_knockout router

Endpoints:
- GET /team-knockout/ - List team knockout rankings
- GET /team-knockout/{team_hnd} - Get specific team
- GET /team-knockout/{team_hnd}/resume - Get season resume

Features:
- Division, gender, region, conference filtering
- Pagination and search
- Async/await with connection pooling
- Consistent with existing team endpoints

Session: 015 - Team Knockout Ranking Implementation

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Frontend Commit
```
[XCRI] Session 015 - Add Team Knockout frontend implementation

Adds Team Knockout ranking display to frontend.

Changes:
- UPDATED: frontend/src/services/api.js - Team Knockout API methods
- UPDATED: frontend/src/App.jsx - Navigation and routing
- UPDATED: frontend/src/components/TeamTable.jsx - Support for knockout type

Features:
- Team Knockout rankings table
- Full filter/search/pagination support
- Navigation integration
- Reuses existing components

Session: 015 - Team Knockout Ranking Implementation

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Troubleshooting Guide

### Issue: No data returned from API

**Diagnosis**:
```bash
# Check if table exists
mysql -h localhost -u web4ustfccca_public -p web4ustfccca_iz
SHOW TABLES LIKE '%knockout%';

# Check if data exists
SELECT COUNT(*) FROM xcri_team_knockout_rankings_current;
```

**Solutions**:
- Table doesn't exist → Coordinate with izzypy_xcri to create
- Table exists but empty → Run ranking calculation script
- Wrong table name → Update service.py with correct table

### Issue: API returns 500 error

**Diagnosis**:
```bash
# Check API logs
ssh ustfccca-web4
tail -f /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log

# Check worker status
ps aux | grep uvicorn
```

**Solutions**:
- Import error → Check service/route imports in main.py
- Database error → Verify connection, table name, columns
- Python error → Check syntax, async/await usage

### Issue: Frontend shows no data

**Diagnosis**:
- Open browser DevTools → Network tab
- Check API requests to `/team-knockout/`
- Look for 404, 500, or CORS errors

**Solutions**:
- 404 error → Route not registered (check main.py)
- 500 error → See API troubleshooting above
- CORS error → Check CORS settings (shouldn't happen for same domain)
- No request → Frontend not calling API (check api.js)

---

## Key Success Criteria

Session 015 is successful when:

1. ✅ **Backend Complete**:
   - API endpoints operational
   - Database queries working
   - Filters and pagination functional
   - Error handling robust

2. ✅ **Frontend Complete**:
   - Team Knockout page loads
   - Data displays correctly
   - All features working (filters, search, pagination)
   - Navigation integrated

3. ✅ **Deployed to Production**:
   - Backend deployed and workers restarted
   - Frontend built and deployed
   - All tests passing in production
   - No errors in logs

4. ✅ **Documented**:
   - API documentation complete
   - README and CLAUDE.md updated
   - Session wrap-up written
   - Commits pushed to GitHub

5. ✅ **Quality Standards Met**:
   - Response times < 200ms (API)
   - Page load < 2 seconds
   - Mobile responsive
   - No console errors
   - Code follows existing patterns

---

## Notes

### Algorithm Coordination

**Important**: Team Knockout ranking algorithm must be:
1. **Implemented in izzypy_xcri** first
2. **Data exported to MySQL** (via batch script)
3. **Table structure documented** before API development

**If algorithm not ready**:
- Pause Session 015 until algorithm complete
- Focus on understanding requirements
- Create placeholder API structure
- Use mock data for frontend testing

### Database Considerations

**Best Practice**: Use same pattern as Team Five rankings
- Separate table for knockout rankings
- Same structure as `xcri_team_rankings_current`
- Additional columns for knockout-specific metrics

**Table naming convention**:
- Current: `xcri_team_knockout_rankings_current`
- Historical: `xcri_team_knockout_rankings_2024`, `xcri_team_knockout_rankings_2025`

---

**Prompt Status**: ✅ Ready for Session 015

**Next Step**: User starts Session 015 by providing Team Knockout algorithm details
