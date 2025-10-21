# XCRI - Next Session Prompt (Session 002)

**Session Type**: Feature Activation and UX Improvements
**Priority**: High (feedback form setup) + Medium (UX enhancements)
**Status**: Application fully operational - enhancing user experience

---

## Quick Context

The XCRI Rankings application is **fully deployed and operational** at:
- **Frontend**: https://web4.ustfccca.org/iz/xcri/
- **API**: https://web4.ustfccca.org/iz/xcri/api/
- **Repository**: https://github.com/lewistv/iz-apps-xcri
- **Issues**: https://github.com/lewistv/iz-apps-xcri/issues

**Previous Session**: Repository setup, bug fixes, feature implementation
- ✅ Created independent GitHub repository
- ✅ Fixed routing bugs (#7)
- ✅ Implemented dynamic page titles (#9)
- ✅ Added USTFCCCA favicon
- ✅ Built feedback form system (#11) - **Needs activation**
- ✅ Created 10 GitHub issues for tracking

**Current State**: Production-ready with:
- ✅ All endpoints working (11 API endpoints)
- ✅ Frontend rendering correctly with fixed navigation
- ✅ Database connected (418K athletes, 36K teams)
- ✅ Feedback form deployed (needs GitHub token)
- ⏳ Manual uvicorn process (systemd fix deferred to Issue #6)

---

## Session Objectives

### Phase 1: Activate Feedback Form (15-20 minutes) - CRITICAL

**Status**: ✅ Deployed, ⏳ Needs GitHub token configuration

**Goal**: Enable user feedback submissions that create GitHub issues automatically

**Steps**:

1. **Create GitHub Personal Access Token** (User task)
   ```
   URL: https://github.com/settings/tokens
   Type: Classic token
   Scopes: repo (Full control of private repositories)
   Expiration: No expiration or 90 days
   Note: "XCRI Feedback Form"
   ```

2. **Install httpx on Server**
   ```bash
   ssh ustfccca-web4
   cd /home/web4ustfccca/public_html/iz/xcri/api
   source venv/bin/activate
   pip install httpx>=0.25.0
   ```

3. **Add Token to .env**
   ```bash
   cd /home/web4ustfccca/public_html/iz/xcri/api
   nano .env

   # Add at bottom:
   GITHUB_TOKEN=ghp_paste_your_token_here
   GITHUB_REPO=lewistv/iz-apps-xcri
   ```

4. **Restart API**
   ```bash
   cd /home/web4ustfccca/public_html/iz/xcri
   ./deployment/restart-api.sh
   ```

5. **Test Feedback System**
   ```bash
   # Check status
   curl https://web4.ustfccca.org/iz/xcri/api/feedback/status | jq

   # Should show: "configured": true
   ```

6. **Submit Test Feedback**
   - Visit: https://web4.ustfccca.org/iz/xcri/feedback
   - Fill out form with test data
   - Verify issue created: https://github.com/lewistv/iz-apps-xcri/issues

**Success Criteria**:
- [ ] GitHub token created and added to .env
- [ ] httpx installed in venv
- [ ] API restarted successfully
- [ ] `/feedback/status` shows "configured": true
- [ ] Test submission creates GitHub issue
- [ ] Issue has correct labels ("user-feedback", type)
- [ ] Confirmation shown with issue URL

**Documentation**: See `FEEDBACK_SETUP.md` for detailed instructions

---

### Phase 2: Implement Debouncing (Issue #8) - HIGH PRIORITY

**Problem**: When users quickly click through filters (division, gender, region, conference), the system gets overwhelmed with API requests.

**User Report**: "When quickly clicking around, the system may get overwhelmed. Could we set a sleep or something to make sure the user is done clicking around before getting lists of athletes or teams?"

**Goal**: Add debouncing to wait until user stops clicking before fetching data

**Implementation Approach**:

1. **Install debounce utility** (if not using custom hook)
   ```bash
   cd frontend
   npm install lodash.debounce
   # OR use custom useDebouncedCallback hook
   ```

2. **Debounce filter changes in App.jsx**
   ```javascript
   import { useCallback } from 'react';
   import debounce from 'lodash.debounce';

   // Debounce API calls (300ms delay)
   const debouncedFetch = useCallback(
     debounce(() => {
       if (isHistorical && selectedSnapshot) {
         fetchHistoricalData();
       } else if (!isHistorical) {
         fetchCurrentData();
       }
     }, 300),
     [isHistorical, selectedSnapshot, division, gender, region, conference]
   );

   // Update useEffect to use debounced version
   useEffect(() => {
     debouncedFetch();
   }, [division, gender, view, isHistorical, selectedSnapshot, region, conference]);
   ```

3. **Add loading indicator during debounce**
   - Show subtle "loading..." or spinner while waiting
   - Don't block UI, just indicate data is being refreshed

4. **Test rapid clicking**
   - Click through multiple filters quickly
   - Verify only final selection triggers API call
   - Ensure smooth user experience

**Files to Modify**:
- `frontend/src/App.jsx` - Add debouncing to filter handlers
- `frontend/package.json` - Add lodash.debounce if needed

**Success Criteria**:
- [ ] Rapid filter changes don't overwhelm API
- [ ] Only final filter selection triggers data fetch
- [ ] UI remains responsive during debounce
- [ ] Loading state shown during wait period
- [ ] No regression in normal filter usage

**Close Issue #8** when complete

---

### Phase 3: Add Loading States (Issue #1) - HIGH PRIORITY

**Problem**: Users don't see feedback while data is loading or when errors occur

**Goal**: Implement comprehensive loading states and error handling

**Implementation**:

1. **Loading Spinners** for data tables
   ```javascript
   {loading && (
     <div className="loading-overlay">
       <div className="spinner"></div>
       <p>Loading {view === 'athletes' ? 'athletes' : 'teams'}...</p>
     </div>
   )}
   ```

2. **Skeleton Screens** (optional, better UX)
   - Show placeholder table rows while loading
   - Gives immediate visual feedback

3. **Error Messages** with retry
   ```javascript
   {error && (
     <div className="error-container">
       <h3>Oops! Something went wrong</h3>
       <p>{error}</p>
       <button onClick={retry}>Try Again</button>
     </div>
   )}
   ```

4. **Empty States**
   ```javascript
   {!loading && !error && data.length === 0 && (
     <div className="empty-state">
       <p>No {view} found matching your criteria.</p>
       <p>Try adjusting your filters.</p>
     </div>
   )}
   ```

5. **Progressive Loading** for large datasets
   - Show "Loading X of Y results..." progress indicator

**Files to Update**:
- `frontend/src/components/AthleteTable.jsx`
- `frontend/src/components/TeamTable.jsx`
- `frontend/src/services/api.js` - Add retry logic
- `frontend/src/App.css` - Loading/error styles

**Success Criteria**:
- [ ] Loading spinner shows during data fetch
- [ ] Error messages are user-friendly (not console logs)
- [ ] Retry button works for failed requests
- [ ] Empty state handles no results gracefully
- [ ] Loading progress shown for large datasets

**Close Issue #1** when complete

---

## Secondary Tasks (Time Permitting)

### Phase 4: URL Persistence for Filters (Issue #2) - MEDIUM PRIORITY

**Goal**: Save filter state to URL so users can bookmark and share filtered views

**Implementation**:
```javascript
import { useSearchParams } from 'react-router-dom';

const [searchParams, setSearchParams] = useSearchParams();

// Read from URL on mount
useEffect(() => {
  const divisionParam = searchParams.get('division');
  const genderParam = searchParams.get('gender');
  if (divisionParam) setDivision(parseInt(divisionParam));
  if (genderParam) setGender(genderParam);
}, []);

// Update URL when filters change
const handleDivisionChange = (newDivision) => {
  setDivision(newDivision);
  setSearchParams({
    division: newDivision,
    gender: gender,
    region: region || '',
    conference: conference || ''
  });
};
```

**Example URLs**:
- `https://web4.ustfccca.org/iz/xcri/athletes?division=2030&gender=M&region=Northeast`
- `https://web4.ustfccca.org/iz/xcri/teams?division=2031&gender=F&conference=Big+12`

**Close Issue #2** when complete

---

### Phase 5: Search Improvements (Issue #4) - MEDIUM PRIORITY

**Goal**: Add debounced search with better feedback

**Implementation**:
1. Debounce search input (300ms)
2. Show "Searching..." indicator
3. Clear search button (X icon)
4. Preserve search in URL params

**Close Issue #4** when complete

---

## Issues Overview

**Total Open**: 9 issues
**This Session Target**: Close 2-3 issues

**Prioritized for This Session**:
1. ⏳ **#11**: Feedback form activation (already deployed, needs setup)
2. 🔥 **#8**: Debouncing (HIGH - user reported, affects performance)
3. 🔥 **#1**: Loading states (HIGH - affects UX significantly)
4. 📋 **#2**: URL persistence (MEDIUM - nice to have)
5. 📋 **#4**: Search improvements (MEDIUM - complements #8)

**Deferred to Later**:
- #3: Pagination improvements
- #5: Mobile responsiveness (needs device testing)
- #6: systemd service fix (infrastructure, not urgent)
- #10: Shared header (architectural change, larger task)

---

## Testing Checklist

**After Feedback Activation**:
- [ ] Visit /iz/xcri/feedback
- [ ] Submit test bug report
- [ ] Verify GitHub issue created
- [ ] Check email notification received
- [ ] Test rate limiting (try 4 submissions in one hour)
- [ ] Verify "configured": true in /feedback/status

**After Debouncing**:
- [ ] Rapidly click Division selector 5 times
- [ ] Verify only final selection triggers API call
- [ ] Check loading state appears briefly
- [ ] No console errors
- [ ] Performance improved (fewer API calls)

**After Loading States**:
- [ ] Clear browser cache
- [ ] Reload page and verify loading spinner
- [ ] Simulate slow network (DevTools throttling)
- [ ] Verify error state with network offline
- [ ] Test retry button functionality
- [ ] Check empty state with filters that return no results

---

## Development Workflow

### 1. Activate Feedback (No Code Changes)
```bash
# On server
ssh ustfccca-web4
cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate
pip install httpx>=0.25.0
nano .env  # Add GITHUB_TOKEN
cd ..
./deployment/restart-api.sh
```

### 2. Local Development (for Issues #8, #1, etc.)
```bash
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri/frontend
npm run dev  # Test at http://localhost:5173
```

### 3. Build and Deploy
```bash
# Frontend
cd frontend
npm run build

# Deploy
rsync -av --exclude='venv/' --exclude='.git/' --exclude='node_modules/' \
  /Users/lewistv/code/ustfccca/iz-apps-clean/xcri/frontend/dist/ \
  ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

# If backend changes
rsync -av --exclude='venv/' --exclude='.git/' --exclude='__pycache__/' \
  /Users/lewistv/code/ustfccca/iz-apps-clean/xcri/api/ \
  ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/

ssh ustfccca-web4 "/home/web4ustfccca/public_html/iz/xcri/deployment/restart-api.sh"
```

### 4. Git Workflow
```bash
git add .
git commit -m "[XCRI] Description of changes (Issue #X)"
git push origin main
```

---

## Important Notes

### Production Status
- Application is **fully operational**
- No critical bugs blocking users
- All enhancements are **improvements**, not fixes
- Take incremental approach (one feature at a time)
- Test thoroughly before deploying

### User Feedback Priority
Based on actual user testing:
1. **Debouncing** (#8) - Directly requested by user
2. **Loading states** (#1) - Improves perceived performance
3. **URL persistence** (#2) - Allows bookmarking
4. **Search** (#4) - Complements debouncing

### Code Quality
- Keep commits focused and well-documented
- Close GitHub issues when features are deployed
- Update documentation as needed
- Add comments for complex logic (especially debouncing)

---

## Success Criteria for Session

**Minimum Success**:
- [x] Feedback form activated and tested
- [ ] Issue #8 (Debouncing) implemented and deployed

**Good Success**:
- [x] Feedback form activated
- [ ] Issue #8 implemented
- [ ] Issue #1 (Loading states) implemented

**Excellent Success**:
- [x] Feedback form activated
- [ ] Issue #8 implemented
- [ ] Issue #1 implemented
- [ ] Issue #2 (URL persistence) implemented

**Close at least 2 issues** this session (not counting feedback activation)

---

## Files to Review

**Existing Code**:
- `frontend/src/App.jsx` - Main component with filter logic
- `frontend/src/components/AthleteTable.jsx` - Athlete table
- `frontend/src/components/TeamTable.jsx` - Team table
- `frontend/src/services/api.js` - API client

**New Files Needed**:
- None (all work is modifying existing files)

**Documentation**:
- `FEEDBACK_SETUP.md` - Feedback form setup guide
- `SESSION_REPORT_2025-10-21.md` - Previous session report
- This file - Current session prompt

---

## Quick Start Command

**To start the session**, paste this:

```markdown
I'm continuing work on the XCRI Rankings application. The application is operational at https://web4.ustfccca.org/iz/xcri/.

Read NEXT_SESSION_PROMPT_002.md and start with:

Phase 1: Activate Feedback Form (Priority: CRITICAL)
- Help me create GitHub Personal Access Token
- Walk through server setup (httpx, .env, restart)
- Test feedback submission

Then move to:
Phase 2: Implement Debouncing (Issue #8, HIGH PRIORITY)
- User reported: "system gets overwhelmed when quickly clicking around"
- Add debouncing to filter changes in App.jsx

Current status:
- Application: ✅ Working perfectly
- Feedback form: ✅ Deployed, ⏳ Needs token setup
- Issues open: 9 (targeting 2-3 closures this session)
```

---

## Reference Documents

- **SESSION_REPORT_2025-10-21.md** - Summary of previous session
- **NEXT_SESSION_PROMPT_002.md** - This file (current session plan)
- **FEEDBACK_SETUP.md** - Detailed feedback form setup instructions
- **MANUAL_STARTUP.md** - API manual startup guide (Option C)
- **CLAUDE.md** - Project overview and architecture
- **README.md** - General project information

---

**Session Status**: Ready to start
**Application Status**: ✅ Operational
**Priority 1**: Activate feedback form (15-20 min setup)
**Priority 2**: Implement debouncing (user-reported issue)
**Target**: Close 2-3 GitHub issues
**Risk Level**: Low (all enhancements, no critical bugs)

**Let's make XCRI even better!** 🚀
