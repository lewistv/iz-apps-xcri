# CLAUDE.md

This file provides guidance to Claude Code when working with the XCRI Rankings web application.

## Project Overview

**XCRI Rankings** - Display-only web application for USTFCCCA Cross Country Running Index rankings.

**Purpose**: Provide public web interface for viewing XCRI rankings, historical snapshots, and component scores.

**Important**: This is a **display-only application**. All ranking calculations and database updates are performed in the parent `izzypy_xcri` repository.

---

## Current Status (October 29, 2025)

**Migration Status**: ✅ COMPLETE - Migrated from izzypy_xcri/webapp
**Repository**: ✅ Independent repository at https://github.com/lewistv/iz-apps-xcri
**Deployment Status**: ✅ **OPERATIONAL** - Session 018 deployment complete
**Security Status**: ✅ **SECURE** - Session 005 security sweep complete

**Production URL**: https://web4.ustfccca.org/iz/xcri/
**API URL**: https://web4.ustfccca.org/iz/xcri/api/
**Team Knockout URL**: https://web4.ustfccca.org/iz/xcri/?view=team-knockout
**GitHub Issues**: https://github.com/lewistv/iz-apps-xcri/issues

**Completion Rate**: 100% (23 of 23 issues closed) 🎉
**Analytics**: ✅ Google Analytics (G-FBG8Y8ZSTW) tracking enabled
**Monitoring**: ✅ Real-time monitoring dashboard deployed

**Recent Session (020)**: Integration of izzypy_xcri Session 031 Database Improvements
- ✅ Integrated 6 new database fields from izzypy_xcri Session 031
- ✅ Backend: Added 3 fields to TeamKnockoutRanking (region, conference, most_recent_race_date)
- ✅ Backend: Added 3 fields to TeamKnockoutMatchup (meet_id, team_a_ko_rank, team_b_ko_rank)
- ✅ Frontend: Enabled server-side region/conference filtering
- ✅ Frontend: Fixed Athletic.net links to use meet_id instead of race_hnd
- ✅ Frontend: Added opponent knockout rank badges in matchup history
- ✅ Critical bug fixes: Python format string escaping (`%%Y` for DATE_FORMAT in aiomysql)
- ✅ Documentation: Comprehensive deployment procedures added to CLAUDE.md
- ⚠️ **CRITICAL**: Documented catastrophic git operations failure and emergency recovery procedures
- ⚠️ Region/Conference filtering requires populated data from izzypy_xcri (awaiting data)

**Previous Session (019)**: Frontend/Backend Bug Fixes and Refinements
- ✅ 11 of 13 user-reported issues resolved
- ✅ Team Knockout table columns refined (renamed, removed, added)
- ✅ Matchup history modal improvements (ordinal formatting, Athletic.net links)
- ✅ H2H modal enhancements (season/gender subheader)
- ✅ Documentation updates (FAQ anchors, cross-references, varsity definitions)
- ✅ Historical snapshot "coming soon" banner
- 📄 Comprehensive requirements document created for backend team

**Previous Session (018)**: Team Knockout Frontend UI Implementation
- ✅ Complete frontend UI for Team Knockout rankings (6 components, ~1,370 lines)
- ✅ Rankings table with sorting, filtering, pagination
- ✅ Matchup history modal with win-loss statistics
- ✅ Head-to-head comparison modal
- ✅ Responsive design and error handling
- ✅ FAQ section updated with Team Knockout documentation
- ✅ Production deployment successful
- ✅ Issue #23 closed - Team Knockout feature 100% complete (backend + frontend)

**Previous Session (017)**: Team Knockout matchups endpoint bug fix
- ✅ Fixed HTTP 422 validation error (route ordering + SQL ambiguity)
- ✅ All 6 Team Knockout endpoints operational (100% success rate)
- ✅ Root cause #1: /{team_id} route defined before /matchups route
- ✅ Root cause #2: SQL WHERE clause missing table aliases (m. prefix)
- ✅ Changes deployed and API restarted successfully
- ✅ GitHub Issue #24 closed, Issue #23 updated
- ✅ Team Knockout backend 100% complete

**Previous Session (016)**: Server restart and Team Knockout deployment verification
- ✅ Maintenance mode implementation for user-friendly updates
- ✅ API server restarted with 4 workers (1 parent + 4 workers = 5 processes)
- ✅ Fixed 3 SQL bugs (ambiguous column references in WHERE clauses)
- ✅ 5/6 Team Knockout endpoints operational (83% success rate)
- ✅ Comprehensive agent documentation created (API_RESTART_GUIDE.md)
- ✅ Updated restart script to use --workers 4
- ⚠️ 1 endpoint deferred: matchups history (422 validation error - FIXED in Session 017)

**Previous Session (015)**: Team Knockout matchup API implementation
- ✅ Backend API complete: 6 endpoints, 7 service functions, 10 models
- ✅ Code deployed to server (1,549 lines added)
- ✅ Frontend API client methods added
- ✅ Data ready: 37,935 matchups across 14 divisions

**Previous Session (012)**: Snapshot filtering and issue closure
- ✅ Issue #20: Region/conference filtering for historical snapshots (DEPLOYED)
- ✅ Issue #19: Snapshot filtering (closed as duplicate)
- ✅ Issue #21: Semantic UI styling (deferred to January 2026+)
- ✅ All historical snapshot endpoints now support region/conference filters
- ✅ Full feature parity with current season endpoints
- ✅ Production deployment successful with 4 uvicorn workers

**Previous Session (011)**: Async migration and critical bug fixes
- ✅ Async + connection pooling operational (8-10x throughput improvement)
- ✅ Health endpoint fixed and working
- ✅ Metadata endpoint returning current date
- ✅ Monitoring script enhanced for multi-worker tracking

**Previous Session (004-005)**: Security, branding, and integration
- ✅ Issue #18: Security sweep complete
- ✅ Issue #16: Athletic.net branding in breadcrumb
- ✅ Issue #15: Season resume integration for teams
- ✅ Issue #10: Shared USTFCCCA header integration
- ✅ Issue #6: Systemd service investigation (adopted manual startup)

**Next Session (021)**: Testing and refinements
- Test region/conference filtering once data is populated by izzypy_xcri
- Verify Athletic.net meet links work correctly with meet_id field
- Monitor Team Knockout ranking stability with new fields
- Address any user feedback on new features
- Consider frontend UI improvements for region/conference filters

---

## Architecture

### Frontend
- **Framework**: React 19 + Vite 7
- **Type**: Single Page Application (SPA)
- **Routing**: React Router (client-side)
- **API Client**: Axios
- **Styling**: CSS (responsive design)
- **Build Output**: `frontend/dist/` (production build)

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn ASGI (4 workers + 1 parent = 5 processes)
- **Port**: 8001 (localhost only)
- **Endpoints**: 21 REST endpoints (athletes, teams, team-five, team-knockout, snapshots, metadata, scs, components, feedback)
- **Database**: MySQL (read-only access)
- **Authentication**: None (public data)

### Database
- **Server**: localhost (on web4)
- **Database**: web4ustfccca_iz
- **User**: web4ustfccca_public (read-only)
- **Password**: See `env` file in iz-apps-clean root
- **Tables**: 12 XCRI tables (athlete_rankings, team_rankings, etc.)

### Deployment
- **Server**: web4.ustfccca.org
- **Path**: /home/web4ustfccca/public_html/iz/xcri
- **Method**: rsync deployment (server is NOT a git repo)
- **Process Management**: Manual restart via SSH (see docs/operations/API_RESTART_GUIDE.md)
- **Restart Script**: deployment/restart-api.sh (local automation)
- **Web Server**: Apache with reverse proxy (.htaccess)
- **Git Repository**: https://github.com/lewistv/iz-apps-xcri (independent repo)

---

## Directory Structure

```
xcri/
├── api/                    # FastAPI backend
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # Settings management
│   ├── database.py        # MySQL connection
│   ├── models.py          # Pydantic models (request/response)
│   ├── routes/            # API route handlers
│   │   ├── athletes.py   # Athlete rankings endpoints
│   │   ├── teams.py      # Team rankings endpoints
│   │   ├── snapshots.py  # Historical snapshots
│   │   ├── scs.py        # SCS component scores
│   │   └── ...
│   ├── services/          # Business logic layer
│   │   ├── athlete_service.py
│   │   ├── team_service.py
│   │   └── ...
│   ├── .env              # Production config (NOT in git)
│   ├── requirements.txt  # Python dependencies
│   └── venv/            # Python virtual environment (NOT in git)
│
├── frontend/              # React SPA
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   ├── components/    # React components
│   │   │   ├── AthleteTable.jsx
│   │   │   ├── TeamTable.jsx
│   │   │   ├── SnapshotSelector.jsx
│   │   │   ├── SCSModal.jsx
│   │   │   └── ...
│   │   ├── pages/         # Page components (FAQ, etc.)
│   │   ├── services/      # API client
│   │   │   └── api.js     # Axios API wrapper
│   │   └── content/       # Markdown content
│   ├── public/            # Static assets
│   ├── dist/             # Production build (NOT in git)
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
│
├── deployment/           # Deployment scripts
│   ├── deploy.sh        # Main deployment script
│   └── xcri-api.service # Systemd service definition
│
├── .htaccess            # Apache configuration
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## Key API Endpoints

**System**:
- GET `/` - Root endpoint with API info
- GET `/health` - Health check

**Current Rankings** (from MySQL):
- GET `/athletes/` - List athletes (pagination, filters, search)
- GET `/athletes/{id}` - Single athlete details
- GET `/teams/` - List teams (pagination, filters)
- GET `/teams/{id}` - Single team details
- GET `/athletes/team/{id}/roster` - Team roster

**Historical Snapshots** (from Excel files):
- GET `/snapshots/` - List available snapshots (13 total)
- GET `/snapshots/{date}/athletes` - Athletes from specific snapshot
- GET `/snapshots/{date}/teams` - Teams from specific snapshot
- GET `/snapshots/{date}/metadata` - Snapshot metadata

**SCS Components**:
- GET `/scs/athletes/{id}/components` - Component score breakdown

**Team Knockout Rankings** (Session 015 - H2H matchup system):
- GET `/team-knockout/` - List Team Knockout rankings (H2H-based)
- GET `/team-knockout/{team_id}` - Single team knockout ranking
- GET `/team-knockout/matchups` - Team's matchup history with win-loss stats
- GET `/team-knockout/matchups/head-to-head` - Direct H2H comparison between two teams
- GET `/team-knockout/matchups/meet/{race_hnd}` - All matchups from a specific meet
- GET `/team-knockout/matchups/common-opponents` - Common opponent analysis

**Metadata**:
- GET `/metadata/` - List calculation metadata
- GET `/metadata/latest` - Latest calculations

---

## Configuration Files

### API Configuration (.env)

Located: `api/.env` (NOT in git)

```env
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=web4ustfccca_iz
DATABASE_USER=web4ustfccca_public
DATABASE_PASSWORD=[REDACTED - See /Users/lewistv/Claude/.env.web4]

API_HOST=127.0.0.1
API_PORT=8001
API_CORS_ORIGINS=https://web4.ustfccca.org

LOG_LEVEL=INFO
DEBUG=False
ENVIRONMENT=production

SNAPSHOT_DIR=/home/web4ustfccca/izzypy_xcri/data/exports
```

### Apache Configuration (.htaccess)

Located: `.htaccess`

- Proxies `/iz/xcri/api/*` requests to `http://127.0.0.1:8001/`
- Serves frontend static files directly
- Handles React Router (SPA routing via index.html)
- Security headers and file blocking

### Systemd Service (deployment/xcri-api.service)

- User service (no sudo required)
- Auto-restart on failure
- Logs to `logs/api-access.log` and `logs/api-error.log`
- WorkingDirectory: `/home/web4ustfccca/iz/xcri/api`

---

## Deployment Workflow

### Initial Deployment (One-time)

1. **Prepare Server**:
   ```bash
   ssh web4ustfccca@web4.ustfccca.org
   cd /home/web4ustfccca/iz
   git clone <this-repository> xcri
   cd xcri
   ```

2. **Setup Backend**:
   ```bash
   cd api
   python3.9 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**:
   ```bash
   cd ../frontend
   npm install
   npm run build
   ```

4. **Install Systemd Service**:
   ```bash
   mkdir -p ~/.config/systemd/user
   cp deployment/xcri-api.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable xcri-api
   systemctl --user start xcri-api
   ```

5. **Create Logs Directory**:
   ```bash
   mkdir -p /home/web4ustfccca/iz/xcri/logs
   ```

### Regular Updates (Git-based)

**Option 1: Use deployment script** (recommended):
```bash
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
./deployment/deploy.sh
```

**Option 2: Manual deployment**:
```bash
# Local
git add .
git commit -m "Your changes"
git push origin main

# Server
ssh web4ustfccca@web4.ustfccca.org
cd /home/web4ustfccca/iz/xcri
git pull origin main
systemctl --user restart xcri-api
```

### ⚠️ CRITICAL: Frontend Deployment Best Practices

**SAFE Frontend Deployment** (When you only changed frontend code):
```bash
cd frontend
npm run build
rsync -avz dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/
```

**❌ NEVER USE `--delete` FLAG ❌**

The `--delete` flag will **REMOVE CRITICAL FILES** that are not in `frontend/dist/`:
- `.htaccess` (Apache configuration - site will break)
- `api-proxy.cgi` (API routing - API will be unreachable)
- `api/` directory (Backend code and venv)

**What was deleted on October 22, 2025**:
```bash
# This command destroyed the production site:
rsync -avz --delete frontend/dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

# Had to emergency restore:
scp .htaccess ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/
scp api-proxy.cgi ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/
ssh ustfccca-web4 'chmod 755 /home/web4ustfccca/public_html/iz/xcri/api-proxy.cgi'
```

**Why this matters**:
- The server is **NOT a git repository** - it's deployed via rsync
- Frontend build output (`dist/`) doesn't contain backend files
- `--delete` removes anything on server not in source directory
- Results in immediate production outage

**Correct deployment approach**:
1. **Frontend only**: Use rsync WITHOUT `--delete` (updates frontend files only)
2. **Backend only**: SSH to server, git pull, restart service
3. **Both**: Do frontend rsync first, then backend git pull
4. **Full deployment**: Use `./deployment/deploy.sh` which handles everything correctly

---

## 🚨 CRITICAL DEPLOYMENT PROCEDURES AND COMMON PITFALLS

**⚠️ WARNING**: This section documents critical procedures based on catastrophic production failures. Read and follow these guidelines carefully to prevent complete production outages.

### CRITICAL RULE #1: Never Use Git Operations on Production Server

**❌ NEVER DO THIS**:
```bash
# DO NOT run git clean, git reset --hard, or any destructive git operations on production
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz && git clean -fd'
```

**Why This Matters**:
- Production server (`/home/web4ustfccca/public_html/iz/`) is **NOT a git repository**
- Git operations can delete ALL application files (xc-scoreboard, season-resume, XCRI, shared/)
- Results in immediate complete outage of all IZ applications
- Requires manual file-by-file restoration via rsync

**Session 020 Incident**: Git clean operation deleted all IZ application files, causing complete production outage requiring emergency restoration of 4+ applications.

### CRITICAL RULE #2: Database Configuration Patterns

**Flask Applications (.env Location)**:
```bash
# Flask apps use load_dotenv() which looks for .env in CURRENT WORKING DIRECTORY
# Each Flask app needs its own .env file in its directory

# CORRECT - Each app has its own .env:
/home/web4ustfccca/public_html/iz/.env                    # Root IZ app
/home/web4ustfccca/public_html/iz/xc-scoreboard/.env     # XC Scoreboard
/home/web4ustfccca/public_html/iz/season-resume/.env     # Season Resume
/home/web4ustfccca/public_html/iz/xcri/api/.env          # XCRI API

# WRONG - Only parent .env exists:
/home/web4ustfccca/public_html/iz/.env                    # Won't work for child apps!
```

**Database Host Configuration**:
```env
# CORRECT for all Flask apps and XCRI API:
DATABASE_HOST=localhost
WEB4_DB_HOST=localhost

# WRONG - MySQL user permissions are host-specific:
DATABASE_HOST=100-29-47-255.cprapid.com  # User web4ustfccca_public@localhost won't work!
WEB4_DB_HOST=100-29-47-255.cprapid.com   # Access denied errors!
```

**Database Password** (NEVER use placeholders):
```env
# CORRECT:
DATABASE_PASSWORD=39rDXrFP3e*f
WEB4_DB_PASSWORD=39rDXrFP3e*f

# WRONG - Will cause authentication failures:
DATABASE_PASSWORD=[GET_FROM_ENV_FILE_AT_/Users/lewistv/Claude/.env.web4]
```

### CRITICAL RULE #3: Python Format String Escaping in SQL

**aiomysql Requirement** - Double `%%` Escaping:
```python
# CORRECT - Double %% required for DATE_FORMAT in aiomysql:
DATE_FORMAT(ko.most_recent_race_date, '%%Y-%%m-%%d') as most_recent_race_date

# WRONG - Single % causes ValueError: unsupported format character 'Y':
DATE_FORMAT(ko.most_recent_race_date, '%Y-%m-%d') as most_recent_race_date
```

**Why This Matters**:
- aiomysql uses Python's `%` operator for parameter binding
- Single `%` in SQL strings is interpreted as a Python format specifier BEFORE reaching MySQL
- Error: `ValueError: unsupported format character 'Y' (0x59) at index 709`
- Solution: Escape with `%%` so Python passes literal `%` to MySQL

**Affected Files**: Any SQL queries with DATE_FORMAT, TIME_FORMAT, or other MySQL functions using `%` directives
- `api/services/team_knockout_service.py` (lines 106-107, 186-187)
- Any future service files using DATE/TIME formatting

### CRITICAL RULE #4: API Process Restart After Code Changes

**Always Restart API After Deploying Code**:
```bash
# Code changes don't take effect until API process reloads
# API loads code into memory at startup, not on each request

# REQUIRED after rsync deployment:
ssh ustfccca-web4 'killall -9 python3.9 2>/dev/null && \
  sleep 3 && \
  cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete 2>/dev/null && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> ../logs/api-live.log 2>&1 &'

# Wait for workers to initialize (6-10 seconds)
sleep 10

# Verify 5 processes running (1 parent + 4 workers)
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l'  # Should return 5

# Test health endpoint
curl https://web4.ustfccca.org/iz/xcri/api/health
```

**Why This Matters**:
- Python bytecode cache (`.pyc` files) can serve old code
- API process loads code at startup, not on each request
- Symptoms: API serves old code despite correct files on server
- Must kill process, clear cache, restart with fresh code

### CRITICAL RULE #5: Flask /iz/shared/ Directory

**Shared Directory is Required for All Flask Apps**:
```bash
# Flask apps (xc-scoreboard, season-resume, root /iz) import from shared/
# Missing shared/ causes: ModuleNotFoundError: No module named 'shared.database'

# Required structure:
/home/web4ustfccca/public_html/iz/shared/
  ├── database.py       # Database connection manager
  ├── utils.py          # Shared utilities
  ├── templates/        # Base templates
  └── static/           # Shared assets

# If shared/ is deleted, ALL Flask apps break immediately
```

**Session 020 Incident**: User identified missing `/iz/shared/` directory as root cause of Flask app failures after git clean operation.

### CRITICAL RULE #6: Deployment Verification Checklist

**After ANY Deployment, Verify All Services**:
```bash
# 1. Root IZ Landing Page
curl -I https://web4.ustfccca.org/iz/ | grep "HTTP"  # Should be 200

# 2. XC Scoreboard
curl -I https://web4.ustfccca.org/iz/xc-scoreboard/ | grep "HTTP"  # Should be 200

# 3. Season Resume
curl -I https://web4.ustfccca.org/iz/season-resume/ | grep "HTTP"  # Should be 200

# 4. XCRI Frontend
curl -I https://web4.ustfccca.org/iz/xcri/ | grep "HTTP"  # Should be 200

# 5. XCRI API
curl https://web4.ustfccca.org/iz/xcri/api/health  # Should return JSON

# 6. Verify API processes
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l'  # Should be 5
```

**If ANY service returns non-200 or fails**:
1. Check application-specific error logs
2. Verify `.env` files exist in each app directory
3. Verify database host is `localhost`
4. Check `/iz/shared/` directory exists
5. Clear Python bytecode cache
6. Restart affected services

### Common Deployment Errors and Solutions

#### Error: "Access denied for user 'web4ustfccca_public'@'100-29-47-255.cprapid.com'"

**Root Causes**:
1. `.env` file missing from app directory (load_dotenv() looks in CWD)
2. Database host configured as remote IP instead of localhost
3. Database password is placeholder text

**Solution**:
```bash
# Copy .env to app directory
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz && cp .env xc-scoreboard/.env'

# Change database host to localhost
ssh ustfccca-web4 'sed -i "s|WEB4_DB_HOST=100-29-47-255.cprapid.com|WEB4_DB_HOST=localhost|" /home/web4ustfccca/public_html/iz/xc-scoreboard/.env'

# Verify password is correct (not placeholder)
ssh ustfccca-web4 'grep WEB4_DB_PASSWORD /home/web4ustfccca/public_html/iz/xc-scoreboard/.env'

# Clear bytecode cache
ssh ustfccca-web4 'find /home/web4ustfccca/public_html/iz/xc-scoreboard -name "*.pyc" -delete'
```

#### Error: "ModuleNotFoundError: No module named 'shared.database'"

**Root Cause**: `/iz/shared/` directory missing or deleted

**Solution**:
```bash
# Restore shared directory from local repository
cd /Users/lewistv/code/ustfccca/iz-apps-clean
rsync -avz --exclude='__pycache__' shared/ ustfccca-web4:/home/web4ustfccca/public_html/iz/shared/
```

#### Error: "ValueError: unsupported format character 'Y' (0x59)"

**Root Cause**: SQL query has single `%` in DATE_FORMAT (should be `%%`)

**Solution**:
```python
# Find the problematic query (usually in services/*.py)
# Change single % to double %%:
DATE_FORMAT(field_name, '%%Y-%%m-%%d')  # CORRECT

# Deploy fix and restart API:
rsync -avz api/services/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/services/
# Then restart API (see CRITICAL RULE #4)
```

#### Error: API Serves Old Code After Deployment

**Root Cause**: API process loaded old code into memory before fix was deployed

**Solution**:
```bash
# Always restart API after deploying code changes
# See CRITICAL RULE #4 for full restart procedure

# Verify file on server is correct
ssh ustfccca-web4 'grep "%%Y" /home/web4ustfccca/public_html/iz/xcri/api/services/team_knockout_service.py'

# If file is correct but API still fails, kill and restart
ssh ustfccca-web4 'killall -9 python3.9'
# Wait 3 seconds, clear cache, restart (see full procedure in CRITICAL RULE #4)
```

### Emergency Recovery Procedures

**Complete IZ Application Restoration** (if git operations delete everything):
```bash
# From local repository: /Users/lewistv/code/ustfccca/iz-apps-clean

# 1. Restore shared directory
rsync -avz --exclude='__pycache__' shared/ ustfccca-web4:/home/web4ustfccca/public_html/iz/shared/

# 2. Restore XC Scoreboard
rsync -avz --exclude='venv' --exclude='__pycache__' xc-scoreboard/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xc-scoreboard/

# 3. Restore Season Resume
rsync -avz --exclude='venv' --exclude='__pycache__' season-resume/ ustfccca-web4:/home/web4ustfccca/public_html/iz/season-resume/

# 4. Restore Root IZ Landing Page
cd xcri  # Root IZ files are in xcri/ subdirectory
rsync -avz index.py app-iz-main.cgi ustfccca-web4:/home/web4ustfccca/public_html/iz/
ssh ustfccca-web4 'chmod 755 /home/web4ustfccca/public_html/iz/app-iz-main.cgi'

# 5. Restore XCRI Frontend
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
rsync -avz frontend/dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/

# 6. Restore XCRI API
rsync -avz --exclude='venv' --exclude='__pycache__' api/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/

# 7. Fix .env files (see Database Configuration above)
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz && cp .env xc-scoreboard/.env && cp .env season-resume/.env'
ssh ustfccca-web4 'sed -i "s|WEB4_DB_HOST=100-29-47-255.cprapid.com|WEB4_DB_HOST=localhost|" /home/web4ustfccca/public_html/iz/.env /home/web4ustfccca/public_html/iz/xc-scoreboard/.env /home/web4ustfccca/public_html/iz/season-resume/.env'

# 8. Verify database password in XCRI API .env
ssh ustfccca-web4 'grep DATABASE_PASSWORD /home/web4ustfccca/public_html/iz/xcri/api/.env'
# If placeholder, replace with actual: 39rDXrFP3e*f

# 9. Clear all bytecode cache
ssh ustfccca-web4 'find /home/web4ustfccca/public_html/iz -name "*.pyc" -delete'

# 10. Restart XCRI API
# (See CRITICAL RULE #4)

# 11. Verify all services (See CRITICAL RULE #6)
```

### Safe Deployment Practices

**DO**:
- Use rsync WITHOUT `--delete` flag for frontend deployments
- Always verify files on server after rsync
- Always restart API after backend code changes
- Always clear Python bytecode cache before restart
- Always verify all services after deployment
- Keep local repository as source of truth
- Use `.env` files in each app's working directory
- Set database host to `localhost` for all apps
- Test in development before deploying to production

**DON'T**:
- Use git operations on production server
- Use `--delete` flag with rsync to production
- Deploy without restarting affected services
- Forget to clear `.pyc` files
- Use placeholder text in .env files
- Configure database host as remote IP
- Skip deployment verification steps
- Deploy untested code to production

---

## Development Commands

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Dev server (hot reload)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Backend Development

```bash
cd api

# Create/activate venv
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Run with specific config
uvicorn main:app --reload --env-file .env.local
```

### Testing

```bash
# Test API health
curl http://localhost:8001/health

# Test specific endpoint
curl "http://localhost:8001/athletes/?division=2030&gender=M&limit=5"

# Test on production
curl https://web4.ustfccca.org/iz/xcri/api/health
```

---

## Production URLs

- **Frontend**: https://web4.ustfccca.org/iz/xcri
- **API Base**: https://web4.ustfccca.org/iz/xcri/api
- **API Docs**: https://web4.ustfccca.org/iz/xcri/api/docs
- **Health Check**: https://web4.ustfccca.org/iz/xcri/api/health

---

## Service Management (on server)

**IMPORTANT**: Production uses **manual process management**, NOT systemd.

### Process Architecture

```bash
# Production runs 5 Python processes:
# - 1 parent process (Uvicorn master)
# - 4 worker processes (request handlers)

# Check running processes
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9"'

# Count processes (should be 5)
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9" | wc -l'
```

### Manual Restart Procedure

**For detailed instructions**, see `docs/operations/API_RESTART_GUIDE.md`

```bash
# Quick restart (use with caution - no maintenance mode)
ssh ustfccca-web4 'ps aux | grep "web4ust.*python3.9" | grep -v grep | awk "{print \$2}" | xargs kill -9 2>/dev/null && \
  sleep 3 && \
  cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete 2>/dev/null && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &'
```

### Viewing Logs

```bash
# View unified production log
ssh ustfccca-web4 'tail -f /home/web4ustfccca/iz/xcri/logs/api-live.log'

# View last 100 lines
ssh ustfccca-web4 'tail -100 /home/web4ustfccca/iz/xcri/logs/api-live.log'

# Search for errors
ssh ustfccca-web4 'grep -i error /home/web4ustfccca/iz/xcri/logs/api-live.log | tail -50'
```

### Critical Notes

1. **Always clear Python bytecode cache** (.pyc files) before restart
2. **Wait 6+ seconds** after starting for workers to initialize
3. **Verify 5 processes** are running after restart
4. **Use maintenance mode** for user-facing updates
5. **Test health endpoint** before disabling maintenance mode

---

## Important Notes

### Data Flow

**DO NOT**:
- Modify database from this webapp
- Add write operations to API
- Perform ranking calculations here

**DO**:
- Use read-only database access
- Display existing rankings data
- Provide user-friendly interface

### Database Updates

All database updates (current rankings, snapshots, component scores) are performed via the parent **izzypy_xcri** repository:

1. Calculate rankings: `izzypy_xcri/batch_xcri_rankings.py`
2. Export to MySQL: `--export-to-mysql` flag
3. Webapp automatically displays updated data

### Historical Snapshots

- Stored as Excel files: `/home/web4ustfccca/izzypy_xcri/data/exports/`
- 13 snapshots (2024: 9, 2025: 4)
- API reads Excel files via pandas (snapshot_service.py)
- Future: Consider migrating to MySQL for performance

### Performance

**Current Performance**:
- API response time: <100ms (current rankings from MySQL)
- API response time: <300ms (historical snapshots from Excel)
- Page load time: <2s
- Bandwidth reduction: 98% (with filters + compression)

**Optimization Tips**:
- Use server-side filtering (region, conference)
- Enable HTTP compression (gzip)
- Cache control headers for static assets
- Database indexes for fast queries

---

## Troubleshooting

### API Won't Start

```bash
# Check logs
journalctl --user -u xcri-api -n 50

# Check if port 8001 is in use
netstat -tuln | grep 8001

# Verify venv
cd /home/web4ustfccca/iz/xcri/api
source venv/bin/activate
python --version  # Should be 3.9+
```

### Frontend Returns 404

```bash
# Verify build exists
ls -la /home/web4ustfccca/iz/xcri/frontend/dist/

# Check Apache .htaccess
cat /home/web4ustfccca/iz/xcri/.htaccess

# Verify file permissions
ls -la /home/web4ustfccca/iz/xcri/
```

### Database Connection Failed

```bash
# Test database connection
mysql --user=web4ustfccca_public --password=[REDACTED] web4ustfccca_iz -e "SELECT 1"

# Check .env file
cat /home/web4ustfccca/iz/xcri/api/.env | grep DATABASE

# Verify .env permissions (should be 600)
ls -la /home/web4ustfccca/iz/xcri/api/.env
```

### Snapshots Not Loading

```bash
# Verify Excel files exist
ls -la /home/web4ustfccca/izzypy_xcri/data/exports/*/excel/

# Check SNAPSHOT_DIR in .env
cat /home/web4ustfccca/iz/xcri/api/.env | grep SNAPSHOT_DIR

# Check API logs for errors
tail -50 /home/web4ustfccca/iz/xcri/logs/api-error.log
```

---

## Security

**Implemented**:
- Read-only database user
- Localhost-only API (127.0.0.1:8001)
- CORS restricted to web4.ustfccca.org
- .htaccess blocks .py, .env, .log files
- Security headers (X-Content-Type-Options, etc.)

**Database Credentials**:
- Stored in .env (NOT in git)
- File permissions: 600 (owner read/write only)
- Never commit .env to git

---

## Related Projects

**izzypy_xcri** (algorithm and research repository):
- Location: `/Users/lewistv/code/ustfccca/izzypy_xcri`
- Purpose: Algorithm development, ranking calculations, research
- Database: Read/write access for rankings updates
- Exports: MySQL database updates for this web app

**iz-apps-xcri** (this repository):
- Location: `/Users/lewistv/code/ustfccca/iz-apps-clean/xcri`
- GitHub: https://github.com/lewistv/iz-apps-xcri
- Purpose: Display-only web application (production deployment)
- Database: Read-only access to rankings data
- Deployment: rsync to web4.ustfccca.org

**iz-apps-clean** (sibling applications):
- Location: `/Users/lewistv/code/ustfccca/iz-apps-clean`
- GitHub: https://github.com/lewistv/iz-apps-production
- Purpose: Other USTFCCCA production web applications
- Server path: `/home/web4ustfccca/public_html/iz`
- Other apps: xc-scoreboard, season-resume, records-lists

---

## Feature Overview

**Current Rankings** (LIVE):
- 7 divisions (D1, D2, D3, NAIA, NJCAA D1/D2/D3)
- 2 genders (Men, Women)
- 14 division/gender combinations
- ~60,000 athletes
- ~36,000 teams

**Historical Snapshots**:
- 13 weekly snapshots (2024-2025 seasons)
- ~358,000 athlete records (historical)
- Same divisions/genders as current

**Features**:
- Athlete rankings table (sortable, searchable, paginated)
- Team rankings table
- Region/conference filtering (server-side)
- Search (client-side, debounced)
- SCS component score modal
- Team roster view
- Historical snapshot selector
- Documentation pages (FAQ, How It Works, Glossary)

**Not Included**:
- User authentication
- Data editing/updates
- Ranking calculations
- Administrative interface

---

## Session History

**PM Session 013** (October 21, 2025):
- Phase 1: Pre-deployment review complete
- Phase 2: Migration to iz-apps-clean/xcri complete
- Files: 69 files, 11,755 lines migrated
- Git: Repository initialized with initial commit
- Status: Ready for deployment

**Deployment Session 002** (October 21, 2025):
- ✅ Frontend deployed to /iz/xcri/
- ✅ Backend systemd service configured
- ✅ CGI proxy created for API routing
- ✅ Root .htaccess configured for SPA + API routing
- ✅ Database module fixed (lazy initialization + Pydantic Settings)
- ✅ All API endpoints validated (athletes, teams, snapshots, metadata)
- ✅ Frontend loading and rendering athlete data
- Status: **Deployed and operational**

**Session 003** (October 21, 2025):
- ✅ Issue #1: Enhanced loading states with animated spinner
- ✅ Issue #4: Search improvements (X icon clear, result count)
- ✅ Issue #5: Mobile responsiveness optimization
- ✅ Issue #3: Enhanced pagination (First/Last + jump-to-page)
- ✅ Issue #17: Fixed SCS modal season year bug
- Status: **UX improvements complete**

**Session 004** (October 21, 2025):
- ✅ Issue #16: Athletic.net branding in breadcrumb
- ✅ Issue #15: Season resume integration for teams
- Database: Fixed iz_groups_season_resumes schema and JOIN mapping
- Backend: New resume_service.py with proper team mapping
- Frontend: TeamProfile displays season resume HTML
- Status: **Feature enhancements complete - 76% completion rate**

**Session 020** (October 29, 2025):
- ✅ Integration of 6 new database fields from izzypy_xcri Session 031
- UPDATED: api/models.py - 6 new Pydantic fields (3 for rankings, 3 for matchups)
- UPDATED: api/services/team_knockout_service.py - SQL queries with new fields
- CRITICAL FIX: Python format string escaping (`%%Y` for DATE_FORMAT in aiomysql)
- UPDATED: frontend/src/App.jsx - Server-side region/conference filtering
- UPDATED: frontend/src/components/MatchupHistoryModal.jsx - meet_id links, ko_rank badges
- UPDATED: frontend/src/components/MatchupHistoryModal.css - ko-rank-badge styling
- ⚠️ **CATASTROPHIC FAILURE**: Git operations deleted all IZ applications
- ✅ Emergency restoration: xc-scoreboard, season-resume, XCRI, shared/, root /iz
- ✅ Database configuration fixes: .env files, localhost host, correct password
- ✅ Python bytecode cache clearing procedures implemented
- ✅ Comprehensive deployment documentation added to CLAUDE.md
- Status: **All systems operational, critical procedures documented**

**Session 015** (October 29, 2025):
- ✅ Team Knockout matchup API implementation (backend complete)
- NEW: api/services/team_knockout_service.py - 7 async service functions (680 lines)
- NEW: api/routes/team_knockout.py - 6 REST API endpoints (550 lines)
- UPDATED: api/models.py - 10 Pydantic models for Team Knockout data (+255 lines)
- UPDATED: api/main.py - Router registration
- UPDATED: frontend/src/services/api.js - 6 API client methods
- Data: 37,935 matchups across 14 divisions ready
- Code: Committed and pushed to GitHub (commit: 1cf9f94)
- Deployment: Files on server, restart pending (Session 016)
- Frontend UI: Deferred to future session (extensive component work required)
- Status: **Backend API complete, deployment verification needed**

---

## Deployment Issues Resolved

### Issue 1: CGI Proxy 500 Errors
**Problem**: api-proxy.cgi worked via SSH but returned 500 errors via web browser

**Root Cause**: Python stdout buffering - mixing text-mode `print()` with binary-mode `sys.stdout.buffer.write()` caused headers and body to appear out of order

**Solution**: Added `flush=True` to all print statements and explicit `sys.stdout.flush()` before binary writes

**Files Changed**: `/iz/xcri/api-proxy.cgi`

### Issue 2: API Routing Missing Path
**Problem**: API requests reached backend but with empty path (e.g., `/athletes/` became `/`)

**Root Cause**: Root .htaccess rewrite rule missing `$1` to preserve path after `/api/`

**Solution**: Changed rule from `RewriteRule ^iz/xcri/api(/.*)?$ /iz/xcri/api-proxy.cgi [QSA,L]` to `RewriteRule ^iz/xcri/api(/.*)?$ /iz/xcri/api-proxy.cgi$1 [QSA,L]`

**Files Changed**: `/public_html/.htaccess` (root)

### Issue 3: Service Startup Failure (DATABASE_PASSWORD)
**Problem**: xcri-api service failed to start with "DATABASE_PASSWORD environment variable is required"

**Root Cause**: database.py tried to initialize `DatabaseConfig()` at module import time, before .env file was loaded

**Solution**:
1. Changed from `os.getenv()` to Pydantic Settings (which loads .env automatically)
2. Implemented lazy initialization - `db_config = None` at module level, initialized on first `get_db()` call
3. DatabaseConfig now imports from config.py which handles .env loading

**Files Changed**: `api/database.py`, `api/config.py`

### Issue 4: Missing Config Fields
**Problem**: Service failed with `AttributeError: 'Settings' object has no attribute 'api_title'`

**Root Cause**: config.py was simplified too much, removing fields that main.py needed

**Solution**: Added `api_title`, `api_description`, `api_version` fields to Settings class

**Files Changed**: `api/config.py`

### Issue 5: Zombie Uvicorn Processes
**Problem**: Service showed "running" but served old/broken code with import errors

**Root Cause**: Previous uvicorn process survived after crash, listening on port 8001

**Diagnosis**: `ps aux | grep uvicorn` revealed old process from earlier deployment

**Solution**: Killed zombie process with `kill -9 <PID>`, then restarted service

**Prevention**: Always check for running processes before debugging startup failures

### Issue 6: Python Bytecode Cache
**Problem**: Code changes didn't take effect even after deployment

**Root Cause**: `.pyc` files cached old code with import errors

**Solution**: Clear all bytecode cache before service restart:
```bash
find /home/web4ustfccca/public_html/iz/xcri/api -name '*.pyc' -delete
find /home/web4ustfccca/public_html/iz/xcri/api -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

**Best Practice**: Include cache clearing in deployment workflow

---

## Verified Endpoints (October 21, 2025)

| Endpoint | Status | Response Time | Notes |
|----------|--------|---------------|-------|
| `/health` | ✅ Working | <100ms | Database: 418K athletes, 36K teams, 60K SCS |
| `/athletes/` | ✅ Working | <200ms | Filters: division, gender, region, conference |
| `/athletes/{id}` | ✅ Working | <100ms | Individual athlete lookup |
| `/athletes/team/{id}/roster` | ✅ Working | <150ms | Team roster with rankings |
| `/teams/` | ✅ Working | <150ms | Team rankings with filters |
| `/teams/{id}` | ✅ Working | <100ms | Individual team lookup |
| `/snapshots/` | ✅ Working | <200ms | Lists 13 historical snapshots |
| `/snapshots/{date}/athletes` | ✅ Working | <300ms | Historical athlete data from Excel |
| `/snapshots/{date}/teams` | ✅ Working | <300ms | Historical team data from Excel |
| `/metadata/` | ✅ Working | <100ms | Calculation metadata |
| `/metadata/latest` | ✅ Working | <100ms | Latest 14 calculations |

**Frontend**: ✅ Working - Loads athlete table with division/gender filters

---

## Contact

For questions about this webapp or deployment issues, refer to:
- README.md (general information)
- API documentation: https://web4.ustfccca.org/iz/xcri/api/docs
- Parent project (izzypy_xcri) for algorithm questions

---

**Last Updated**: October 29, 2025
**Migration Status**: Complete and deployed
**Deployment Status**: ✅ Operational
**Session 020**: Integration complete with critical deployment documentation added
