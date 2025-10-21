#!/bin/bash
# Create GitHub Issues for XCRI Frontend Improvements
# Based on NEXT_SESSION_PROMPT.md suggestions
#
# Usage: ./create-issues.sh [repository]
# Example: ./create-issues.sh ustfccca/xcri
# Example: ./create-issues.sh ustfccca/iz-apps-clean

set -e

REPO=${1:-}

if [ -z "$REPO" ]; then
    echo "Usage: ./create-issues.sh <repository>"
    echo "Example: ./create-issues.sh ustfccca/xcri"
    exit 1
fi

echo "Creating GitHub Issues for $REPO..."
echo ""

# Issue 1: Loading States
echo "Creating Issue 1: Loading States and Error Messages..."
gh issue create --repo "$REPO" \
    --title "[XCRI] Add loading states and error messages" \
    --label "enhancement,ui" \
    --body "## Description
Implement comprehensive loading states and error handling for better user experience.

## Tasks
- [ ] Add loading spinners/skeletons during data fetch
- [ ] Show user-friendly error messages (not just console errors)
- [ ] Handle \"no results\" state gracefully
- [ ] Add retry mechanism for failed API calls
- [ ] Show loading progress for large datasets

## Files to Update
- \`frontend/src/components/AthleteTable.jsx\`
- \`frontend/src/components/TeamTable.jsx\`
- \`frontend/src/services/api.js\`

## Priority
High

## Reference
NEXT_SESSION_PROMPT.md - Task #2"

echo "✓ Created loading states issue"
echo ""

# Issue 2: Filter State Persistence
echo "Creating Issue 2: Filter State Persistence..."
gh issue create --repo "$REPO" \
    --title "[XCRI] Persist filter state in URL parameters" \
    --label "enhancement,ux" \
    --body "## Description
Save filter state to URL parameters to allow bookmarking and sharing filtered views.

## Tasks
- [ ] Use React Router's \`useSearchParams\` hook
- [ ] Sync filter state with URL parameters
- [ ] Parse URL params on component mount
- [ ] Update URL when filters change (without page reload)

## Example URLs
\`\`\`
https://web4.ustfccca.org/iz/xcri/athletes?division=2030&gender=M&region=Northeast
https://web4.ustfccca.org/iz/xcri/teams?division=2031&gender=F&conference=Big+12
\`\`\`

## Files to Update
- \`frontend/src/components/FilterControls.jsx\` (or similar)
- \`frontend/src/App.jsx\`

## Priority
Medium

## Reference
NEXT_SESSION_PROMPT.md - Task #3"

echo "✓ Created filter persistence issue"
echo ""

# Issue 3: Pagination Improvements
echo "Creating Issue 3: Pagination Improvements..."
gh issue create --repo "$REPO" \
    --title "[XCRI] Enhance table pagination controls" \
    --label "enhancement,ui" \
    --body "## Description
Improve pagination functionality with more user-friendly controls.

## Tasks
- [ ] Show current page / total pages
- [ ] Add \"rows per page\" selector (25, 50, 100, 250)
- [ ] Add \"jump to page\" input
- [ ] Keyboard shortcuts (arrow keys, Page Up/Down)
- [ ] Scroll to top on page change
- [ ] Preserve pagination state in URL

## Files to Update
- \`frontend/src/components/AthleteTable.jsx\`
- \`frontend/src/components/TeamTable.jsx\`

## Priority
Medium

## Reference
NEXT_SESSION_PROMPT.md - Task #4"

echo "✓ Created pagination issue"
echo ""

# Issue 4: Search Improvements
echo "Creating Issue 4: Search Functionality Improvements..."
gh issue create --repo "$REPO" \
    --title "[XCRI] Improve search functionality" \
    --label "enhancement,ux" \
    --body "## Description
Enhance search experience with debouncing and better feedback.

## Tasks
- [ ] Implement debounced search (300ms delay after typing stops)
- [ ] Show \"searching...\" indicator during search
- [ ] Add clear search button
- [ ] Preserve search term in URL params
- [ ] Highlight search terms in results (optional)

## Implementation Options
- Client-side search for already-loaded data (fast)
- Server-side search via API (more accurate)

## API Endpoint
\`/athletes/?search=<query>\` (already exists)

## Priority
High

## Reference
NEXT_SESSION_PROMPT.md - Task #5"

echo "✓ Created search improvements issue"
echo ""

# Issue 5: Mobile Responsiveness
echo "Creating Issue 5: Mobile Responsiveness..."
gh issue create --repo "$REPO" \
    --title "[XCRI] Improve mobile responsiveness" \
    --label "enhancement,mobile,ui" \
    --body "## Description
Ensure application works well on mobile devices and tablets.

## Test On
- Mobile phone (320px - 480px)
- Tablet (768px - 1024px)
- Desktop (1280px+)

## Tasks
- [ ] Tables scroll horizontally or stack columns on mobile
- [ ] Filters accessible on mobile (dropdown/drawer)
- [ ] Buttons are touch-friendly (44px minimum)
- [ ] Text readable without zooming
- [ ] Navigation works on small screens

## Testing Tools
- Chrome DevTools (Device Mode)
- Real device testing

## Priority
Medium

## Reference
NEXT_SESSION_PROMPT.md - Task #6"

echo "✓ Created mobile responsiveness issue"
echo ""

# Issue 6: systemd Service Fix
echo "Creating Issue 6: Fix systemd Service Restart Loop..."
gh issue create --repo "$REPO" \
    --title "[XCRI] Fix systemd service restart loop" \
    --label "bug,deployment,infrastructure" \
    --body "## Description
The xcri-api systemd service has a restart loop issue. Currently running via manual uvicorn process as workaround (Option C).

## Current Status
- ✅ Application working via manual process (PID 3858399)
- ⚠️ systemd service has restart loop
- ✅ Crontab auto-start implemented (Option C)

## Options to Resolve

### Option A: Test Updated systemd Service
- Service updated from \`Restart=always\` to \`Restart=on-failure\`
- Needs testing to verify fix

### Option B: Implement Gunicorn Supervisor
- More robust production setup
- Add Gunicorn to requirements.txt
- Use UvicornWorker for ASGI support

### Option C: Keep Manual Process ✅ (Current)
- Documented in MANUAL_STARTUP.md
- Crontab @reboot auto-start
- Works but not ideal for production

## Files
- \`~/.config/systemd/user/xcri-api.service\`
- \`deployment/xcri-api.service\`
- \`MANUAL_STARTUP.md\`

## Priority
High (infrastructure improvement)

## Reference
NEXT_SESSION_PROMPT.md - Task #0
MANUAL_STARTUP.md"

echo "✓ Created systemd service issue"
echo ""

echo "=== All Issues Created Successfully ==="
echo ""
echo "View issues: gh issue list --repo $REPO"
echo "Or visit: https://github.com/$REPO/issues"
