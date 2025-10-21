# XCRI - Next Session Prompt

**Session Type**: Refinement and Improvements
**Priority**: Medium (cosmetic and practical fixes)
**Status**: Application is fully operational - these are enhancements

---

## Quick Context

The XCRI Rankings application is **fully deployed and operational** at:
- **Frontend**: https://web4.ustfccca.org/iz/xcri/
- **API**: https://web4.ustfccca.org/iz/xcri/api/

**Previous Session**: Deployment Session 002 - Successfully resolved all deployment issues and validated all endpoints.

**Current State**: Production-ready React SPA + FastAPI application with:
- ✅ All 11 API endpoints working
- ✅ Frontend loading and rendering athlete rankings
- ✅ Database connection validated (418K athletes, 36K teams)
- ✅ systemd service running stable
- ✅ Documentation complete

---

## Session Objective

**Primary Focus**: Fix systemd service restart loop (HIGH PRIORITY)

**Secondary Focus**: Cosmetic and practical improvements to enhance user experience

**Current Status**: Application is fully operational via manual uvicorn process (PID 3858399). systemd service has restart loop issue and needs fixing.

---

## Priority Tasks

### 0. Fix systemd Service Restart Loop (CRITICAL)
**Priority**: HIGH - Must fix before final deployment sign-off

**Current Situation**:
- Application running via manual uvicorn process: `nohup uvicorn main:app --host 127.0.0.1 --port 8001 &`
- Manual process is stable and working perfectly
- systemd service had `Restart=always` causing 10-second restart loop
- Service configuration updated but not tested yet

**Options**:

**Option A: Test Updated systemd Service** (Recommended)
```bash
# Kill manual process
ssh ustfccca-web4 "pkill -f 'uvicorn main:app --host 127.0.0.1 --port 8001'"

# Test updated service (changed Restart=always to Restart=on-failure)
ssh ustfccca-web4 "systemctl --user daemon-reload && systemctl --user enable xcri-api && systemctl --user start xcri-api"

# Monitor for 60 seconds to ensure no restart loop
watch -n 5 "ssh ustfccca-web4 'systemctl --user status xcri-api | head -10'"
```

**Option B: Implement Gunicorn Supervisor** (More Robust)
```bash
# Install Gunicorn in venv
ssh ustfccca-web4 "cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && pip install gunicorn"

# Update systemd service to use Gunicorn + UvicornWorker
ExecStart=/home/web4ustfccca/public_html/iz/xcri/api/venv/bin/gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --log-level info
```

**Option C: Keep Manual Process** (Quick Fix)
- Document the manual startup command
- Add to crontab with `@reboot` for auto-start on server reboot
- Monitor manually

**Success Criteria**:
- [ ] systemd service runs without restarting
- [ ] Service survives for at least 5 minutes without shutdown
- [ ] API responds consistently during test period
- [ ] Service auto-restarts only on actual failures

**Files to Update**:
- `~/.config/systemd/user/xcri-api.service` (already updated, needs testing)
- OR `api/requirements.txt` (if adding Gunicorn)

---

## Suggested Tasks

### 1. Frontend UI/UX Refinements
**Priority**: Medium

**Areas to Review**:
- Overall layout and spacing
- Color scheme and branding consistency
- Typography and readability
- Button and control styling
- Responsive design on different screen sizes

**Questions to Consider**:
- Does the interface match USTFCCCA branding?
- Is the layout intuitive for users?
- Are important actions/filters easy to find?
- Does it look professional and modern?

**Test URLs**:
- Home: https://web4.ustfccca.org/iz/xcri/
- Athletes: https://web4.ustfccca.org/iz/xcri/athletes
- Teams: https://web4.ustfccca.org/iz/xcri/teams

---

### 2. Loading States and Error Messages
**Priority**: High

**Current Behavior**: Review how the app handles:
- Initial data loading
- Filter changes (loading new data)
- API errors
- Network timeouts
- Empty results

**Improvements Needed**:
- [ ] Add loading spinners/skeletons during data fetch
- [ ] Show user-friendly error messages (not just console errors)
- [ ] Handle "no results" state gracefully
- [ ] Add retry mechanism for failed API calls
- [ ] Show loading progress for large datasets

**Files to Review**:
- `frontend/src/components/AthleteTable.jsx`
- `frontend/src/components/TeamTable.jsx`
- `frontend/src/services/api.js`

---

### 3. Filter State Persistence
**Priority**: Medium

**Current Behavior**: Filters may reset on page refresh

**Desired Behavior**:
- Save filter state to URL parameters
- Allow bookmarking filtered views
- Restore filter state from URL on page load
- Update URL when filters change (without page reload)

**Example URLs**:
```
https://web4.ustfccca.org/iz/xcri/athletes?division=2030&gender=M&region=Northeast
https://web4.ustfccca.org/iz/xcri/teams?division=2031&gender=F&conference=Big+12
```

**Implementation**:
- Use React Router's `useSearchParams` hook
- Sync filter state with URL parameters
- Parse URL params on component mount
- Update URL when filters change

**Files to Update**:
- `frontend/src/components/FilterControls.jsx` (or similar)
- `frontend/src/App.jsx`

---

### 4. Table Pagination Improvements
**Priority**: Medium

**Current Behavior**: Review pagination controls

**Improvements**:
- [ ] Show current page / total pages
- [ ] Add "rows per page" selector (25, 50, 100, 250)
- [ ] Add "jump to page" input
- [ ] Keyboard shortcuts (arrow keys, Page Up/Down)
- [ ] Scroll to top on page change
- [ ] Preserve pagination state in URL

**Files to Review**:
- `frontend/src/components/AthleteTable.jsx`
- `frontend/src/components/TeamTable.jsx`

---

### 5. Search Functionality
**Priority**: High (if not already implemented)

**Features**:
- Search by athlete name
- Search by school name
- Debounced search (don't search on every keystroke)
- Show "searching..." indicator
- Clear search button
- Preserve search in URL params

**Implementation**:
- Client-side search for already-loaded data (fast)
- OR server-side search via API (more accurate)
- Use debouncing (300ms delay after typing stops)

**API Endpoint**: `/athletes/?search=<query>` (already exists)

---

### 6. Mobile Responsiveness
**Priority**: Medium

**Test On**:
- Mobile phone (320px - 480px)
- Tablet (768px - 1024px)
- Desktop (1280px+)

**Areas to Check**:
- Tables should scroll horizontally or stack columns
- Filters should be accessible (maybe in dropdown/drawer)
- Buttons should be touch-friendly (44px minimum)
- Text should be readable without zooming
- Navigation should work on small screens

**Tools**:
- Chrome DevTools (Device Mode)
- Responsive Design Checker

---

### 7. Performance Optimizations
**Priority**: Low

**Areas to Review**:
- Initial page load time
- API response times
- Table rendering performance (large datasets)
- Image/asset optimization
- Code splitting (if not already done)
- Lazy loading components

**Measurements**:
- Use Chrome DevTools Performance tab
- Check Network tab for slow requests
- Monitor bundle size

**Quick Wins**:
- Enable HTTP compression (gzip)
- Add cache headers for static assets
- Lazy load non-critical components
- Optimize images

---

### 8. User Feedback Incorporation
**Priority**: Variable (depends on feedback)

**Questions to Ask User**:
1. What features are most important to you?
2. Are there any confusing or frustrating aspects?
3. What would make this tool more useful?
4. Are there any missing features you expected?
5. How does performance feel?

**Testing Scenarios**:
- Have user try common workflows
- Observe where they get stuck
- Ask about their expectations
- Note any confusion or errors

---

## Testing Checklist

Before making changes, test current functionality:

### Frontend
- [ ] Home page loads
- [ ] Athletes page loads with data
- [ ] Teams page loads with data
- [ ] Filters work (division, gender, region, conference)
- [ ] Search works (if implemented)
- [ ] Pagination works
- [ ] Sorting works (if implemented)
- [ ] SPA routing works (no page reloads)
- [ ] Refresh on any route works (doesn't 404)

### API
- [ ] Health endpoint: https://web4.ustfccca.org/iz/xcri/api/health
- [ ] Athletes endpoint: https://web4.ustfccca.org/iz/xcri/api/athletes/?division=2030&gender=M&limit=10
- [ ] Teams endpoint: https://web4.ustfccca.org/iz/xcri/api/teams/?division=2030&gender=M&limit=10
- [ ] Snapshots endpoint: https://web4.ustfccca.org/iz/xcri/api/snapshots/
- [ ] API docs: https://web4.ustfccca.org/iz/xcri/api/docs

### Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## Development Workflow

### 1. Review Current State
Start by visiting the production site and testing all features:
```bash
# Open in browser
open https://web4.ustfccca.org/iz/xcri/

# Check API health
curl https://web4.ustfccca.org/iz/xcri/api/health | jq
```

### 2. Make Changes Locally
```bash
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri

# Frontend changes
cd frontend
npm run dev  # Test at http://localhost:5173

# Backend changes (if needed)
cd ../api
source venv/bin/activate
uvicorn main:app --reload  # Test at http://localhost:8001
```

### 3. Build and Deploy
```bash
# Build frontend
cd frontend
npm run build

# Deploy frontend
rsync -av dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

# If backend changes
rsync -av api/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/
ssh ustfccca-web4 "systemctl --user restart xcri-api"
```

### 4. Verify Production
```bash
# Test in browser
open https://web4.ustfccca.org/iz/xcri/

# Check service status
ssh ustfccca-web4 "systemctl --user status xcri-api"

# Check logs
ssh ustfccca-web4 "tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-error.log"
```

---

## Files to Review

### Frontend Components
```
frontend/src/
├── App.jsx                 # Main app, routing
├── components/
│   ├── AthleteTable.jsx    # Athlete rankings table
│   ├── TeamTable.jsx       # Team rankings table
│   ├── FilterControls.jsx  # Division/gender/etc filters
│   ├── Pagination.jsx      # Pagination controls
│   └── ...
├── services/
│   └── api.js              # API client (axios)
└── main.jsx                # Entry point, Router setup
```

### Backend (Only if needed)
```
api/
├── main.py                 # FastAPI app
├── routes/
│   ├── athletes.py         # Athlete endpoints
│   └── teams.py            # Team endpoints
└── services/
    ├── athlete_service.py  # Business logic
    └── team_service.py     # Business logic
```

---

## Important Notes

### Don't Break What's Working
- The application is fully operational
- All deployment issues are resolved
- Take incremental approach (one feature at a time)
- Test thoroughly before deploying

### Frontend Only (Probably)
Most improvements will be frontend-only:
- UI/UX changes
- Loading states
- Filter state management
- Pagination improvements

Backend should only change if:
- Need new API endpoints
- Need to modify response format
- Need to add caching

### Git Workflow
```bash
# Before starting
git status
git pull origin main

# After changes
git add <files>
git commit -m "[XCRI] Description of changes"

# Optional: push to remote
git push origin main
```

### Deployment Safety
- Always test locally first
- Deploy frontend separately from backend
- Keep backups of working versions
- Have rollback plan ready

---

## Success Criteria

### Minimum (Must Have)
- [ ] Application still works after changes
- [ ] No regressions in existing functionality
- [ ] Loading states implemented
- [ ] Error handling improved
- [ ] User experience noticeably better

### Ideal (Nice to Have)
- [ ] Filter state persists in URL
- [ ] Pagination fully featured
- [ ] Search functionality smooth
- [ ] Mobile responsive
- [ ] Performance optimized
- [ ] User feedback incorporated

---

## Quick Start Command

**To start the session**, paste this:

```markdown
I'm continuing work on the XCRI Rankings application. The deployment is operational at https://web4.ustfccca.org/iz/xcri/ but running via manual uvicorn process.

Read NEXT_SESSION_PROMPT.md and start with Priority Task #0: Fix systemd Service Restart Loop.

Current status:
- Application: ✅ Working perfectly
- Process: Manual uvicorn (PID 3858399)
- Issue: systemd service has restart loop
- Priority: Fix systemd service OR implement Gunicorn supervisor

After fixing the service issue, we can move on to cosmetic improvements.
```

---

## Reference Documents

- **DEPLOYMENT_SESSION_002_COMPLETE.md** - Summary of deployment session (includes Issue #7: systemd restart loop)
- **NEXT_SESSION_PROMPT.md** - This file (includes systemd fix options)
- **CLAUDE.md** - Project overview and architecture
- **IZ_APPS_DEPLOYMENT_GUIDE.md** - Deployment patterns and troubleshooting
- **README.md** - General project information

---

**Session Status**: Ready to start
**Application Status**: ✅ Operational (manual process)
**Current Process**: Manual uvicorn (PID 3858399, stable since 16:08 UTC)
**Priority**: HIGH - Fix systemd service restart loop
**Secondary Priority**: Medium - UI/UX enhancements
**Risk Level**: Low (core functionality working, just needs proper service management)
