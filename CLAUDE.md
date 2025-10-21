# CLAUDE.md

This file provides guidance to Claude Code when working with the XCRI Rankings web application.

## Project Overview

**XCRI Rankings** - Display-only web application for USTFCCCA Cross Country Running Index rankings.

**Purpose**: Provide public web interface for viewing XCRI rankings, historical snapshots, and component scores.

**Important**: This is a **display-only application**. All ranking calculations and database updates are performed in the parent `izzypy_xcri` repository.

---

## Current Status (October 21, 2025)

**Migration Status**: ✅ COMPLETE - Migrated from izzypy_xcri/webapp
**Repository**: ✅ Independent repository at https://github.com/lewistv/iz-apps-xcri
**Deployment Status**: ✅ **DEPLOYED AND OPERATIONAL**

**Production URL**: https://web4.ustfccca.org/iz/xcri/
**API URL**: https://web4.ustfccca.org/iz/xcri/api/
**GitHub Issues**: https://github.com/lewistv/iz-apps-xcri/issues

**Completion Rate**: 82% (14 of 17 issues closed)

**Recent Session (004)**: Branding and integration complete
- ✅ Issue #16: Athletic.net branding in breadcrumb
- ✅ Issue #15: Season resume integration for teams
- ✅ Issue #10: Shared USTFCCCA header integration
- ✅ Breadcrumb updated to "USTFCCCA InfoZone > XCRI"
- ✅ Page title added: "🏆 XCRI: Cross Country Rating Index"

**Next Session**: Cosmetic and practical fixes (Issues #1, #3, #17)

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
- **Server**: Uvicorn ASGI (2 workers)
- **Port**: 8001 (localhost only)
- **Endpoints**: 15 REST endpoints
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
- **Process Management**: Manual uvicorn + crontab (Option C - see MANUAL_STARTUP.md)
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

```bash
# Check service status
systemctl --user status xcri-api

# View logs (follow mode)
journalctl --user -u xcri-api -f

# View last 100 lines
journalctl --user -u xcri-api -n 100

# Restart service
systemctl --user restart xcri-api

# Stop service
systemctl --user stop xcri-api

# Start service
systemctl --user start xcri-api

# View API error logs
tail -f /home/web4ustfccca/iz/xcri/logs/api-error.log

# View API access logs
tail -f /home/web4ustfccca/iz/xcri/logs/api-access.log
```

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

**Next Session**: Remaining issues or user feedback review

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

**Last Updated**: October 21, 2025
**Migration Status**: Complete and deployed
**Deployment Status**: ✅ Operational
**Next Step**: Cosmetic and practical fixes
