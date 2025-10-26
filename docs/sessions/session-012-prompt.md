# XCRI Session 012 - Prompt

**Proposed Focus**: Snapshot Filters or Semantic UI Styling  
**Context**: Session 011 completed async migration and fixed critical bugs  
**GitHub Issues**: #20 (snapshot filters), #21 (Semantic UI styling)

---

## Session Context

Session 011 successfully deployed the async migration to production and fixed several critical bugs:
- ✅ Async + connection pooling operational (8-10x throughput improvement)
- ✅ Health endpoint fixed and working
- ✅ Metadata endpoint returning current date  
- ✅ Monitoring script enhanced for multi-worker tracking
- ✅ Maintenance page runners animation corrected

**Production Status**: Stable and performing excellently
- Response times: 0.09-0.11s
- System load: 0.10 (very healthy)
- 5 processes running (1 master + 1 tracker + 3 workers)

---

## Option A: Fix Snapshot Filters (Issue #20)

**Priority**: Medium  
**Type**: Bug + Enhancement  
**Complexity**: Low-Medium (2-3 hours)

### Problem
Historical snapshot endpoints don't accept region/conference filter parameters. Users can filter current season rankings by region/conference, but this functionality is missing for historical snapshots.

### Files to Modify
1. `api/routes/snapshots.py` - Add filter parameters to endpoint signatures
2. `api/services/snapshot_service.py` - Add filtering logic to snapshot queries

### Implementation Steps
1. Read existing snapshot endpoints to understand current implementation
2. Review current season filter implementation in `athlete_service.py` and `team_service.py`
3. Add `region` and `conference` parameters to snapshot endpoints
4. Implement WHERE clause filtering in snapshot SQL queries
5. Test with various filter combinations
6. Update API documentation

### Expected Outcome
- Snapshot endpoints accept `region` and `conference` query parameters
- Historical data can be filtered by region/conference like current season data
- Consistent filtering behavior across current and historical views

---

## Option B: Apply Semantic UI Styling (Issue #21)

**Priority**: Medium  
**Type**: Enhancement  
**Complexity**: Medium-High (4-6 hours)

### Problem
XCRI pages lack the polished, professional styling found in the xc-scoreboard application. Applying consistent Semantic UI CSS patterns would improve visual quality and maintain brand consistency across USTFCCCA applications.

### Files to Modify
- `frontend/src/components/TeamProfile.jsx` - Team profile page styling
- `frontend/src/pages/FAQ.jsx` - FAQ page styling
- `frontend/src/pages/HowItWorks.jsx` - How It Works page styling
- `frontend/src/pages/Glossary.jsx` - Glossary page styling
- `frontend/src/pages/Feedback.jsx` - Feedback page styling
- Possibly others based on current state

### Implementation Steps
1. Review Semantic UI patterns in `/docs/SEMANTIC-UI-STYLE-GUIDE.md`
2. Examine xc-scoreboard application for reference implementations
3. Apply card structure layouts to team profile pages
4. Update typography, spacing, and colors on documentation pages
5. Ensure responsive design works across all devices
6. Test with existing content to avoid layout breaks

### Expected Outcome
- Consistent visual appearance across XCRI and xc-scoreboard apps
- Professional, polished UI matching xc-scoreboard quality
- Better visual hierarchy and readability
- Maintained functionality with enhanced appearance

---

## Recommendation

**Option A (Snapshot Filters)** is recommended for Session 012 because:

1. **Lower Complexity**: Clear implementation path with existing patterns to follow
2. **User Impact**: Directly addresses a functional limitation
3. **Shorter Duration**: Can likely complete in one session
4. **Foundation for Future Work**: Completing functional features before cosmetic enhancements

Option B (Semantic UI Styling) can be tackled in Session 013 or later, potentially as a multi-session project given its broader scope.

---

## Starting Point for Session 012

```
Continue working on the XCRI Rankings application.

**Session Focus**: Fix historical snapshot filters (Issue #20)

**Context from Session 011**:
- Async migration successfully deployed to production
- API running with 8-10x throughput improvement
- All critical bugs fixed (health endpoint, metadata endpoint, monitoring)
- Production is stable and performing excellently

**Task for this session**:
Implement region and conference filtering for historical snapshot endpoints. Currently, users can filter current season rankings by region/conference, but this functionality is missing for historical snapshots.

**Files to work with**:
1. api/routes/snapshots.py - Snapshot route handlers
2. api/services/snapshot_service.py - Snapshot business logic
3. Reference: api/services/athlete_service.py and team_service.py for filter patterns

**Steps**:
1. Review current snapshot endpoint implementation
2. Examine current season filter implementation patterns
3. Add region and conference parameters to snapshot endpoints
4. Implement SQL WHERE clause filtering for snapshots
5. Test with various filter combinations
6. Deploy to production and verify

**GitHub Issue**: #20 - https://github.com/lewistv/iz-apps-xcri/issues/20

Please start by examining the current snapshot implementation and identifying where filters need to be added.
```

---

## Alternative Starting Point (Option B)

```
Continue working on the XCRI Rankings application.

**Session Focus**: Apply Semantic UI styling to team pages and documentation pages (Issue #21)

**Context from Session 011**:
- Async migration successfully deployed to production
- All critical functionality is working correctly
- Production is stable and performing excellently

**Task for this session**:
Apply consistent Semantic UI CSS styling from the xc-scoreboard application to XCRI team pages and documentation pages. Goal is to create visual consistency across USTFCCCA applications while maintaining current functionality.

**Reference Materials**:
1. /docs/SEMANTIC-UI-STYLE-GUIDE.md - Semantic UI patterns and examples
2. xc-scoreboard application - Reference implementation

**Files to enhance**:
1. frontend/src/components/TeamProfile.jsx
2. frontend/src/pages/FAQ.jsx  
3. frontend/src/pages/HowItWorks.jsx
4. frontend/src/pages/Glossary.jsx
5. frontend/src/pages/Feedback.jsx

**Steps**:
1. Review Semantic UI style guide and xc-scoreboard patterns
2. Start with TeamProfile component (most visible to users)
3. Apply card layouts, typography, and spacing enhancements
4. Test responsive design across devices
5. Move to documentation pages
6. Deploy and verify visual consistency

**GitHub Issue**: #21 - https://github.com/lewistv/iz-apps-xcri/issues/21

Please start by reviewing the style guide and examining the current TeamProfile component.
```

---

**Session 011 Documentation**: `docs/sessions/session-011-october-24-2025.md`
