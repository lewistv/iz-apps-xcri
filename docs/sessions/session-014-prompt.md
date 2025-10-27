# XCRI Session 014 - Frontend Migration to Team-Five Endpoint

**Date**: TBD
**Session Type**: Frontend Development & Deployment
**Prerequisites**: Session 013b complete (backend `/team-five` endpoint deployed)

---

## Objective

Complete the migration from `/teams` to `/team-five` API endpoints in the frontend. This is the second half of the terminology update to prepare for future deployment of additional team ranking methodologies.

---

## Background

**Session 013** (Complete):
- Updated all UI text from "Team Rankings" → "Team Five Rankings"
- Frontend, documentation, tooltips, FAQ all updated
- Deployed to production

**Session 013b** (Complete):
- Created `/team-five` API endpoint (backend)
- Deployed backend to production
- API endpoints available and tested

**Session 014** (This Session):
- Migrate frontend to use `/team-five` endpoints
- Build and deploy frontend
- Restart API workers
- End-to-end testing

---

## Tasks

### 1. Frontend API Service Updates

**File**: `frontend/src/services/api.js`

Add new methods that use `/team-five` endpoint:
```javascript
// Add these methods (keep existing getTeams methods for now)
export const getTeamFive = (params) => api.get('/team-five/', { params });
export const getTeamFiveById = (id, params) => api.get(`/team-five/${id}`, { params });
export const getTeamFiveResume = (teamHnd, params) => api.get(`/team-five/${teamHnd}/resume`, { params });
export const getTeamFiveRoster = (teamHnd, params) => api.get(`/athletes/team/${teamHnd}/roster`, { params });
```

### 2. Component Updates

**Files to Update**:
- `frontend/src/components/TeamTable.jsx`
- `frontend/src/pages/TeamProfile.jsx` (if exists)
- Any other components using team endpoints

**Changes**:
- Replace `getTeams()` with `getTeamFive()`
- Replace `getTeamsById()` with `getTeamFiveById()`
- Replace `getTeamResume()` with `getTeamFiveResume()`

**Search Pattern**: Grep for `api.getTeams` to find all usages

### 3. Navigation Updates

Verify these already say "Team Five Rankings" (from Session 013):
- `frontend/src/App.jsx` - Navigation menu
- Page titles and breadcrumbs
- ExplainerBox titles

### 4. Build & Test Locally

```bash
cd frontend
npm run build
```

Test the build output works correctly.

### 5. Deploy to Production

```bash
# Deploy frontend (NO --delete flag!)
cd frontend
rsync -avz dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

# Deploy backend (if any changes)
rsync -avz ../api/routes/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/routes/
rsync -avz ../api/main.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/

# Restart API workers
ssh ustfccca-web4 'pgrep -f "uvicorn main:app" | xargs kill -15 2>/dev/null; sleep 4; cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &'

# Wait and verify
sleep 5
curl https://web4.ustfccca.org/iz/xcri/api/health
```

### 6. Testing Checklist

After deployment, verify:

- [ ] Team Five Rankings page loads
- [ ] Division filter works (D1, D2, D3, NAIA)
- [ ] Gender filter works (Men, Women)
- [ ] Region filter works
- [ ] Conference filter works
- [ ] Search works
- [ ] Pagination works
- [ ] Team detail page loads
- [ ] Team roster displays correctly
- [ ] Season resume loads
- [ ] API docs show team-five endpoints
- [ ] Health check passes

**URLs to Test**:
- https://web4.ustfccca.org/iz/xcri/ (navigate to Team Five Rankings)
- https://web4.ustfccca.org/iz/xcri/api/docs (verify endpoints)
- https://web4.ustfccca.org/iz/xcri/api/health (verify healthy)

---

## Backward Compatibility Note

The original `/teams` endpoint still exists and works. If you encounter any issues during migration, the frontend can be rolled back to use `/teams` while debugging.

---

## Success Criteria

✅ Frontend uses `/team-five` API endpoints
✅ All team ranking pages work correctly
✅ All filters and search functional
✅ Team detail pages load properly
✅ API healthy with 4 workers running
✅ No console errors in browser
✅ Changes committed and pushed to GitHub

---

## Commit Message Template

```
[XCRI] Session 014 - Frontend migration to /team-five endpoint

- Update api.js to add team-five methods
- Update TeamTable component to use team-five endpoint
- Update [other components] to use team-five endpoint
- Build and deploy frontend
- Restart API workers with new code

Frontend now uses /team-five endpoint. Backend /teams endpoint
remains for backward compatibility.
```

---

## Related Documentation

- Session 013 wrap-up: `docs/sessions/session-013-wrap-up.md`
- Session 013b wrap-up: `docs/sessions/session-013b-wrap-up.md`
- API documentation: `api/routes/team_five.py`
- Main API: `api/main.py`

---

## Notes

- **IMPORTANT**: Do NOT use `rsync --delete` flag when deploying frontend
- The `/teams` endpoint will remain available for backward compatibility
- API workers MUST be restarted after backend file sync
- Frontend build time is typically < 1 second with Vite
- API restart takes ~5 seconds with 4 workers

---

**Estimated Duration**: 30-45 minutes
**Complexity**: Low (straightforward find-and-replace migration)
**Risk**: Low (original /teams endpoint still works)
