# XCRI Session 013 - Prompt

**Proposed Focus**: Update team ranking terminology from "Team Rankings" to "Team Five Rankings"

**Context**: Session 012 completed all open GitHub issues and deployed snapshot filtering functionality

**GitHub Issues**: All 21 issues closed - No open issues

---

## Session Context

Session 012 successfully closed all remaining GitHub issues:
- ✅ Issue #20: Region/conference filtering for historical snapshots (DEPLOYED)
- ✅ Issue #19: Snapshot filtering (closed as duplicate)
- ✅ Issue #21: Semantic UI styling (deferred to January 2026+ off-season)

**Production Status**: Stable and performing excellently
- All systems operational
- 4 uvicorn workers running smoothly
- Historical snapshot filtering working correctly
- No open issues or pending work items

---

## Session 013 Objective

### Update Team Ranking Terminology

**Current State**: The application currently uses the generic term "Team Rankings" throughout the UI and API

**Goal**: Rename to "Team Five Rankings" to make room for a new team-based ranking system that will be deployed soon

**Rationale**:
- Current team rankings use top 5 athletes per team
- New team ranking system (different methodology) is in development
- Need to differentiate between the two ranking systems
- "Team Five Rankings" clearly indicates the 5-athlete basis

---

## Implementation Scope

### Frontend Changes (React Components)

**Files to update**:
1. `frontend/src/App.jsx` - Main routing and navigation
2. `frontend/src/components/TeamTable.jsx` - Team rankings table component
3. `frontend/src/components/Header.jsx` - Navigation menu
4. `frontend/src/pages/*.jsx` - Any pages referencing team rankings
5. Page titles and metadata

**Changes needed**:
- Update navigation menu text: "Team Rankings" → "Team Five Rankings"
- Update page titles: "Team Rankings" → "Team Five Rankings"
- Update component headers and labels
- Update breadcrumb text
- Update any help text or descriptions mentioning team rankings

### Backend Changes (FastAPI)

**Files to update**:
1. `api/routes/teams.py` - Team endpoint route descriptions
2. `api/main.py` - API metadata and documentation
3. API endpoint docstrings and summaries

**Changes needed**:
- Update OpenAPI documentation strings
- Update endpoint summaries: "Team Rankings" → "Team Five Rankings"
- Update response descriptions
- Maintain backward compatibility (no URL changes)

### Documentation Updates

**Files to update**:
1. `frontend/src/content/faq.md` - FAQ references
2. `frontend/src/content/how-it-works.md` - Methodology descriptions
3. `frontend/src/content/glossary.md` - Terminology definitions
4. `README.md` - Project description

**Changes needed**:
- Update all references to "team rankings"
- Add clarification about "Team Five" methodology
- Explain that it's based on top 5 athletes per team
- Prepare for future "Team Seven Rankings" or other variants

---

## Implementation Steps

1. **Review Current Usage**
   - Search codebase for all instances of "team ranking", "team rankings", etc.
   - Identify all locations needing updates
   - Plan changes to maintain consistency

2. **Update Frontend Components**
   - Navigation menu and routing
   - Page titles and metadata
   - Component headers and labels
   - Help text and descriptions

3. **Update Backend API**
   - Endpoint documentation
   - OpenAPI metadata
   - Response descriptions
   - Keep URLs unchanged (no breaking changes)

4. **Update Documentation**
   - FAQ content
   - How It Works explanations
   - Glossary definitions
   - README and project docs

5. **Testing**
   - Verify all text changes display correctly
   - Check page titles and metadata
   - Test navigation and routing
   - Verify API documentation updates
   - Check responsive design (mobile/desktop)

6. **Deployment**
   - Build frontend
   - Deploy to production
   - Verify changes in production
   - Test all affected pages

---

## Expected Outcome

- Clear differentiation between ranking methodologies
- Consistent "Team Five Rankings" terminology throughout application
- Documentation updated to explain the 5-athlete basis
- UI prepared for future addition of other team ranking types
- No breaking changes to API URLs or functionality
- Professional, clear terminology for users

---

## Technical Notes

**Search patterns to use**:
```bash
# Case-insensitive search for team ranking references
grep -ri "team.ranking" frontend/src
grep -ri "team.ranking" api/

# Check for variations
grep -ri "team\s*rank" frontend/src
grep -ri "team\s*rank" api/
```

**Replacement patterns**:
- "Team Rankings" → "Team Five Rankings"
- "team rankings" → "team five rankings"
- "Team Ranking" → "Team Five Ranking"
- "team ranking" → "team five ranking"

**Exceptions** (do NOT change):
- API endpoint URLs (maintain backward compatibility)
- Database table names
- Internal variable names (unless necessary for clarity)
- File names (unless part of visible content)

---

## Starting Point for Session 013

```
Continue working on the XCRI Rankings application.

**Session Focus**: Update team ranking terminology to "Team Five Rankings"

**Context from Session 012**:
- All 21 GitHub issues successfully closed
- Snapshot filtering deployed and operational
- Production is stable and performing excellently
- No pending issues or work items

**Task for this session**:
Update terminology throughout the XCRI application to replace "Team Rankings" with "Team Five Rankings" to prepare for deployment of a new team-based ranking system.

**Objective**:
Make room for a new team ranking methodology by clarifying that current team rankings use the top 5 athletes per team. This differentiation will allow for future addition of other team ranking variants (e.g., Team Seven Rankings).

**Scope**:
1. Frontend: Navigation, page titles, component labels, help text
2. Backend: API documentation, endpoint descriptions, OpenAPI metadata
3. Documentation: FAQ, How It Works, Glossary, README
4. Maintain backward compatibility: No URL changes or breaking changes

**Implementation approach**:
- Search for all instances of "team ranking" variations
- Update UI text and labels consistently
- Update API documentation strings
- Update markdown content files
- Test changes locally
- Deploy to production and verify

Please start by searching the codebase for all references to "team ranking" and creating a plan for systematic updates.
```

---

**Session 012 Documentation**: `docs/sessions/session-012-october-26-2025.md`
**Current Status**: All issues closed, production stable, ready for terminology update
