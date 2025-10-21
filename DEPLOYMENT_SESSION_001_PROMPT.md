# Deployment Session 001 - XCRI Production Deployment

**Session Type**: Deployment Window
**Date**: October 21, 2025 (or later)
**Duration**: 2-3 hours (estimated)
**Target**: https://web4.ustfccca.org/iz/xcri
**Status**: Ready to execute

---

## Context from PM Session 013

**Previous Session**: PM Session 013 completed webapp migration from izzypy_xcri to iz-apps-clean/xcri

**Migration Results**:
- ✅ Frontend migrated (React 19 + Vite 7)
- ✅ Backend migrated (FastAPI REST API)
- ✅ Configuration files created (.env, .htaccess, systemd service)
- ✅ Deployment scripts ready (deploy.sh)
- ✅ Git repository initialized (2 commits)
- ✅ Documentation complete (README.md, CLAUDE.md)

**Repository Status**:
- Location: /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
- Files: 70 files (11,755 lines of code)
- Size: 992 KB
- Commits: 2 (initial migration + CLAUDE.md)

---

## Session Objective

Deploy the XCRI Rankings web application to production server at web4.ustfccca.org/iz/xcri.

**Architecture**:
- Frontend: React SPA served by Apache
- Backend: FastAPI daemon on port 8001 (localhost only)
- Proxy: Apache reverse proxy to backend
- Service: User systemd (no sudo required)
- Database: MySQL web4ustfccca_iz (read-only access)

---

## Prerequisites - Verify Before Starting

### Local Environment

```bash
# Verify you're in the correct directory
pwd
# Should output: /Users/lewistv/code/ustfccca/iz-apps-clean/xcri

# Verify git repository
git log --oneline
# Should show 2 commits:
# - Add CLAUDE.md for future Claude sessions
# - Initial XCRI webapp migration from izzypy_xcri

# Verify directory structure
ls -la
# Should show: api/, frontend/, deployment/, .htaccess, README.md, CLAUDE.md
```

### Server Access

```bash
# Test SSH connection
ssh web4ustfccca@web4.ustfccca.org "echo 'SSH OK'; whoami; hostname; pwd"

# Expected output:
# SSH OK
# web4ustfccca
# 100-29-47-255.cprapid.com
# /home/web4ustfccca
```

### Database Access

```bash
# Test database connection from server
ssh web4ustfccca@web4.ustfccca.org \
  "mysql --user=web4ustfccca_public --password=39rDXrFP3e*f web4ustfccca_iz -e 'SELECT COUNT(*) FROM iz_rankings_xcri_athlete_rankings'"

# Expected: ~418,000 athletes
```

### Documentation Review

Before starting deployment, **READ THESE FILES**:
1. `README.md` - Deployment procedures and architecture
2. `CLAUDE.md` - Complete reference guide (535 lines)
3. `deployment/deploy.sh` - Automated deployment script

---

## Phase 1: Initial Server Setup (30 min)

### Task 1.1: Check if XCRI Already Exists on Server

```bash
# Check if directory exists
ssh web4ustfccca@web4.ustfccca.org "ls -la /home/web4ustfccca/iz/ | grep xcri"

# If xcri exists: STOP and review (might be from previous attempt)
# If xcri doesn't exist: Proceed with clone
```

**Decision Point**:
- If directory exists: Backup first, then proceed or clean
- If directory doesn't exist: Continue to clone

### Task 1.2: Clone Repository to Server

**NOTE**: You'll need to determine the git repository URL first. Options:

**Option A**: Push to GitHub/GitLab first, then clone on server
```bash
# Local machine - push to remote
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
git remote add origin <YOUR_GIT_URL>
git push -u origin main

# Server - clone
ssh web4ustfccca@web4.ustfccca.org
cd /home/web4ustfccca/iz
git clone <YOUR_GIT_URL> xcri
```

**Option B**: Copy files via rsync (if no git remote)
```bash
# From local machine
rsync -avz --exclude='node_modules' --exclude='venv' --exclude='.git' \
  /Users/lewistv/code/ustfccca/iz-apps-clean/xcri/ \
  web4ustfccca@web4.ustfccca.org:/home/web4ustfccca/iz/xcri/

# Then init git on server
ssh web4ustfccca@web4.ustfccca.org
cd /home/web4ustfccca/iz/xcri
git init
git add .
git commit -m "Initial deployment"
```

### Task 1.3: Verify Files on Server

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/iz/xcri

# Verify directory structure
ls -la
# Should see: api/, frontend/, deployment/, .htaccess, README.md

# Verify critical files
test -f .htaccess && echo "✓ .htaccess present"
test -f deployment/xcri-api.service && echo "✓ systemd service present"
test -f deployment/deploy.sh && echo "✓ deploy script present"
```

### Task 1.4: Create .env File on Server

**IMPORTANT**: The .env file is NOT in git (security), must be created manually:

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/iz/xcri/api

cat > .env << 'EOF'
# XCRI API Production Configuration
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=web4ustfccca_iz
DATABASE_USER=web4ustfccca_public
DATABASE_PASSWORD=39rDXrFP3e*f

API_HOST=127.0.0.1
API_PORT=8001
API_CORS_ORIGINS=https://web4.ustfccca.org

LOG_LEVEL=INFO
DEBUG=False
ENVIRONMENT=production

SNAPSHOT_DIR=/home/web4ustfccca/izzypy_xcri/data/exports
EOF

# Set secure permissions
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- (600 permissions)
```

---

## Phase 2: Backend Setup (30 min)

### Task 2.1: Create Python Virtual Environment

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/iz/xcri/api

# Check Python version
python3.9 --version
# Should be 3.9.16 or similar

# Create venv
python3.9 -m venv venv

# Verify venv created
ls -la venv/
# Should see: bin/, lib/, etc.

# Activate venv
source venv/bin/activate

# Verify Python in venv
which python
# Should show: /home/web4ustfccca/iz/xcri/api/venv/bin/python

python --version
# Should show: Python 3.9.x
```

### Task 2.2: Install Python Dependencies

```bash
# Still in venv
cd /home/web4ustfccca/iz/xcri/api
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|pymysql)"

# Expected packages:
# fastapi        (latest)
# uvicorn        (latest)
# sqlalchemy     (latest)
# pymysql        (latest)
# pydantic       (latest)
```

### Task 2.3: Test Backend Manually

```bash
# Still in venv
cd /home/web4ustfccca/iz/xcri/api
source venv/bin/activate

# Test import
python -c "from main import app; print('Import successful')"

# Expected: "Import successful"

# Test database connection
python -c "from database import get_db; print('Database connection OK')"

# If errors occur: Check .env file, database credentials
```

### Task 2.4: Test API Startup (Manual)

```bash
# Terminal 1 - Start API manually for testing
cd /home/web4ustfccca/iz/xcri/api
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8001

# Expected output:
# INFO:     Started server process
# INFO:     Uvicorn running on http://127.0.0.1:8001

# Terminal 2 - Test health endpoint
curl -s http://127.0.0.1:8001/health | python3 -m json.tool

# Expected:
# {
#   "status": "healthy",
#   "database": "connected",
#   ...
# }

# Terminal 2 - Test athletes endpoint
curl -s "http://127.0.0.1:8001/athletes/?division=2030&gender=M&limit=3" | python3 -m json.tool

# Should return 3 D1 Men athletes

# Terminal 1 - Stop with Ctrl+C
```

---

## Phase 3: Install Systemd Service (15 min)

### Task 3.1: Create Logs Directory

```bash
ssh web4ustfccca@web4.ustfccca.org

mkdir -p /home/web4ustfccca/iz/xcri/logs

# Verify
ls -la /home/web4ustfccca/iz/xcri/
# Should see: logs/ directory
```

### Task 3.2: Install User Systemd Service

```bash
ssh web4ustfccca@web4.ustfccca.org

# Create user systemd directory
mkdir -p ~/.config/systemd/user

# Copy service file
cp /home/web4ustfccca/iz/xcri/deployment/xcri-api.service \
   ~/.config/systemd/user/

# Verify copy
ls -la ~/.config/systemd/user/xcri-api.service

# Reload systemd
systemctl --user daemon-reload

# Enable service (auto-start)
systemctl --user enable xcri-api

# Start service
systemctl --user start xcri-api

# Wait a few seconds
sleep 5

# Check status
systemctl --user status xcri-api

# Expected output:
# ● xcri-api.service - XCRI Rankings API Service
#    Loaded: loaded
#    Active: active (running)
```

### Task 3.3: Verify API Service

```bash
# Check if process is running
ps aux | grep uvicorn | grep xcri

# Check if port 8001 is listening
netstat -tuln | grep 8001
# Expected: tcp  0  0  127.0.0.1:8001  0.0.0.0:*  LISTEN

# Test health endpoint
curl -s http://127.0.0.1:8001/health

# Expected: {"status":"healthy",...}

# Check logs
journalctl --user -u xcri-api -n 50

# Or check log files
tail -30 /home/web4ustfccca/iz/xcri/logs/api-access.log
tail -30 /home/web4ustfccca/iz/xcri/logs/api-error.log
```

**If service won't start**: Check logs with `journalctl --user -u xcri-api -n 100`

---

## Phase 4: Frontend Setup (20 min)

### Task 4.1: Install Node Modules

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/iz/xcri/frontend

# Install dependencies
npm install

# This may take 2-5 minutes
# Expected: node_modules/ directory created with ~15 packages
```

### Task 4.2: Build Frontend for Production

```bash
cd /home/web4ustfccca/iz/xcri/frontend

# Build production bundle
npm run build

# Expected output:
# vite v7.x.x building for production...
# dist/index.html                   X.XX kB
# dist/assets/index-XXXXX.css       XX.XX kB
# dist/assets/index-XXXXX.js        XXX.XX kB
# ✓ built in XXXms

# Verify build
ls -la dist/

# Should see:
# index.html
# assets/index-XXXXX.css
# assets/index-XXXXX.js
# vite.svg
```

### Task 4.3: Copy Build to Web Root

**IMPORTANT**: Apache serves from `/home/web4ustfccca/iz/xcri/`, not from `frontend/dist/`

```bash
cd /home/web4ustfccca/iz/xcri

# Copy frontend build files to xcri root
cp -r frontend/dist/* .

# Verify files in root
ls -la
# Should now see in root:
# index.html (from frontend build)
# assets/ (from frontend build)
# .htaccess (already there)
# api/, frontend/, deployment/ (original dirs)

# Verify index.html
head -5 index.html
# Should show React app HTML
```

---

## Phase 5: Apache Configuration (10 min)

### Task 5.1: Verify .htaccess

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/iz/xcri

# Verify .htaccess exists
cat .htaccess

# Should contain:
# - RewriteEngine On
# - API proxy rules (to port 8001)
# - SPA routing rules
# - Security headers
```

### Task 5.2: Test Apache Configuration

```bash
# From local machine - test if Apache serves the site
curl -I https://web4.ustfccca.org/iz/xcri

# Expected:
# HTTP/1.1 200 OK
# (or 404 if .htaccess not processed yet - this is OK, will fix)

# Test if API proxy works
curl -s https://web4.ustfccca.org/iz/xcri/api/health

# Expected:
# {"status":"healthy",...}

# If 404 or 502: Check Apache error logs
ssh web4ustfccca@web4.ustfccca.org "tail -50 ~/logs/error_log | grep xcri"
```

**If API proxy doesn't work**:
- Verify mod_proxy is enabled: Contact server admin
- Check if .htaccess is processed: Check Apache config
- Verify backend service running: `systemctl --user status xcri-api`

---

## Phase 6: Integration Testing (30 min)

### Test Suite 1: API Endpoints (15 min)

```bash
# From local machine (or server)

# 1. Health check
curl -s https://web4.ustfccca.org/iz/xcri/api/health | python3 -m json.tool

# 2. Athletes endpoint - D1 Men
curl -s "https://web4.ustfccca.org/iz/xcri/api/athletes/?division=2030&gender=M&limit=5" | python3 -m json.tool

# 3. Teams endpoint
curl -s "https://web4.ustfccca.org/iz/xcri/api/teams/?division=2030&gender=M&limit=5" | python3 -m json.tool

# 4. Snapshots list
curl -s "https://web4.ustfccca.org/iz/xcri/api/snapshots/" | python3 -m json.tool

# 5. Specific snapshot
curl -s "https://web4.ustfccca.org/iz/xcri/api/snapshots/2024-11-25/athletes?division=2030&gender=M&limit=5" | python3 -m json.tool

# 6. SCS components
curl -s "https://web4.ustfccca.org/iz/xcri/api/scs/athletes/19019918/components?season_year=2024&division=2030&gender=M" | python3 -m json.tool

# 7. API docs (open in browser)
open https://web4.ustfccca.org/iz/xcri/api/docs
```

**All tests should return JSON data without errors**

### Test Suite 2: Frontend Application (15 min)

Open in browser: https://web4.ustfccca.org/iz/xcri

**Manual Testing Checklist**:
- [ ] Page loads without errors
- [ ] Division selector shows all 7 divisions
- [ ] Gender selector shows Men/Women
- [ ] Default view shows D1 Men athletes
- [ ] Rankings table displays with data
- [ ] Search bar works (type "Smith")
- [ ] Pagination works (navigate pages)
- [ ] Snapshot selector shows current + historical
- [ ] Switching snapshots loads different data
- [ ] Region filter works
- [ ] Conference filter works
- [ ] SCS icon appears next to athlete names
- [ ] Clicking SCS opens modal with component scores
- [ ] Team name links work (team profile page)
- [ ] Athletic.net links work (external link)
- [ ] Footer links work (FAQ, How It Works, Glossary)
- [ ] Breadcrumb navigation works
- [ ] No errors in browser console (F12)

**Cross-Browser Testing**:
- [ ] Chrome/Edge: All features work
- [ ] Safari: All features work
- [ ] Firefox: All features work

**Mobile Testing**:
- [ ] Responsive design works on mobile
- [ ] Tables scroll/display correctly
- [ ] Buttons are clickable on small screens

---

## Phase 7: Performance Validation (15 min)

### API Performance

```bash
# Test API response time (10 requests)
for i in {1..10}; do
  time curl -s "https://web4.ustfccca.org/iz/xcri/api/athletes/?division=2030&gender=M&limit=25" > /dev/null
done

# Average should be <100ms for current rankings
# Average should be <300ms for snapshots
```

### Frontend Performance

Open browser DevTools → Network tab:
- [ ] Page load (DOMContentLoaded): <1s
- [ ] Page load (Full): <2s
- [ ] API requests: <100ms
- [ ] Static assets cached (304 on reload)

### Database Query Performance

```bash
ssh web4ustfccca@web4.ustfccca.org

# Check API logs for slow queries
grep -i "slow" /home/web4ustfccca/iz/xcri/logs/api-error.log

# No slow queries should appear for typical operations
```

---

## Phase 8: Final Verification (10 min)

### Service Health

```bash
ssh web4ustfccca@web4.ustfccca.org

# Service status
systemctl --user status xcri-api

# Should show: active (running)

# Recent logs (no errors)
journalctl --user -u xcri-api -n 50

# Check error log (should be minimal)
wc -l /home/web4ustfccca/iz/xcri/logs/api-error.log

# Check access log (should show requests)
tail -20 /home/web4ustfccca/iz/xcri/logs/api-access.log
```

### Production Checklist

- [ ] Frontend accessible: https://web4.ustfccca.org/iz/xcri
- [ ] API responding: https://web4.ustfccca.org/iz/xcri/api/health
- [ ] API docs accessible: https://web4.ustfccca.org/iz/xcri/api/docs
- [ ] All 15 API endpoints working
- [ ] All 14 division/gender combinations loading
- [ ] All 13 snapshots accessible
- [ ] Search functionality working
- [ ] Geographic filters working
- [ ] SCS modal working
- [ ] Navigation working
- [ ] Performance targets met (<100ms API, <2s page load)
- [ ] No critical errors in logs
- [ ] Service auto-restarts (test with `systemctl --user restart xcri-api`)

---

## Phase 9: Documentation (10 min)

### Create Deployment Record

```bash
# On local machine
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri

# Create deployment log
cat > DEPLOYMENT_LOG.md << EOF
# XCRI Production Deployment Log

## Deployment Date
$(date)

## Deployment Status
✅ SUCCESS

## Production URLs
- Frontend: https://web4.ustfccca.org/iz/xcri
- API: https://web4.ustfccca.org/iz/xcri/api
- API Docs: https://web4.ustfccca.org/iz/xcri/api/docs
- Health: https://web4.ustfccca.org/iz/xcri/api/health

## Service Status
- Backend: systemd service xcri-api (active)
- Frontend: Apache serving static files
- Database: MySQL web4ustfccca_iz (read-only)

## Testing Results
- API Endpoints: All 15 working
- Frontend Features: All tested
- Performance: Within targets
- Cross-browser: Verified
- Mobile: Verified

## Deployed By
Claude Code - Deployment Session 001

## Issues Encountered
[Document any issues here]

## Notes
[Any additional notes]
EOF

# Commit deployment log
git add DEPLOYMENT_LOG.md
git commit -m "Deployment: Successful production deployment $(date '+%Y-%m-%d')"
git push origin main
```

### Update Server with Git

```bash
ssh web4ustfccca@web4.ustfccca.org

cd /home/web4ustfccca/iz/xcri

# Pull latest (with deployment log)
git pull origin main
```

---

## Success Criteria

**Must Complete** ✅:
- [ ] Backend API deployed and running
- [ ] Frontend deployed and serving
- [ ] Systemd service active and enabled
- [ ] All 15 API endpoints responding correctly
- [ ] All 14 division/gender combinations loading
- [ ] All 13 snapshots accessible
- [ ] Search functionality working
- [ ] Geographic filters working (region, conference)
- [ ] SCS modal working
- [ ] Performance within targets (<100ms API, <2s page load)
- [ ] Zero critical errors in logs
- [ ] Service auto-restarts on failure
- [ ] Deployment documented

**Should Complete** 📋:
- [ ] Cross-browser testing complete
- [ ] Mobile responsive testing complete
- [ ] All documentation updated
- [ ] Git repository updated

---

## Rollback Plan (If Needed)

If critical issues occur:

```bash
ssh web4ustfccca@web4.ustfccca.org

# Stop service
systemctl --user stop xcri-api

# Rename current deployment
cd /home/web4ustfccca/iz
mv xcri xcri_failed_$(date +%Y%m%d_%H%M%S)

# Restore from backup (if you made one)
# OR remove and start over
rm -rf xcri

# Service will auto-stop when directory removed
```

---

## Troubleshooting Guide

### API Won't Start

```bash
# Check logs
journalctl --user -u xcri-api -n 100

# Common issues:
# 1. Port 8001 in use: netstat -tuln | grep 8001
# 2. Database connection failed: Check .env file
# 3. Python import errors: Check venv and dependencies
# 4. File permissions: .env should be 600
```

### Frontend Shows 404

```bash
# Verify files in web root
ls -la /home/web4ustfccca/iz/xcri/index.html

# Verify .htaccess
cat /home/web4ustfccca/iz/xcri/.htaccess

# Check Apache logs
tail -50 ~/logs/error_log | grep xcri
```

### API Proxy Not Working (502 Bad Gateway)

```bash
# Verify backend running
systemctl --user status xcri-api

# Verify port 8001 listening
netstat -tuln | grep 8001

# Test direct connection
curl http://127.0.0.1:8001/health

# If direct works but proxy doesn't:
# - mod_proxy may not be enabled
# - .htaccess may not be processed
# - Contact server admin
```

### Database Connection Failed

```bash
# Test database credentials
mysql --user=web4ustfccca_public --password=39rDXrFP3e*f web4ustfccca_iz -e "SELECT 1"

# Check .env file
cat /home/web4ustfccca/iz/xcri/api/.env | grep DATABASE

# Verify .env permissions
ls -la /home/web4ustfccca/iz/xcri/api/.env
# Should be: -rw------- (600)
```

### Snapshots Not Loading

```bash
# Check if snapshot files exist
ls -la /home/web4ustfccca/izzypy_xcri/data/exports/

# Verify SNAPSHOT_DIR in .env
cat /home/web4ustfccca/iz/xcri/api/.env | grep SNAPSHOT_DIR

# Check API logs
tail -50 /home/web4ustfccca/iz/xcri/logs/api-error.log
```

---

## Post-Deployment Tasks

**Immediate** (Day 1):
- [ ] Monitor logs for first 24 hours
- [ ] Check service status regularly
- [ ] Collect user feedback
- [ ] Document any issues

**Week 1**:
- [ ] Monitor weekly
- [ ] Review performance metrics
- [ ] Test weekly data updates (when izzypy_xcri exports new data)
- [ ] Verify service survives server reboots

**Ongoing**:
- [ ] Weekly monitoring
- [ ] Monthly log review
- [ ] Quarterly security review
- [ ] Update dependencies as needed

---

## Expected Timeline

**Optimistic** (2 hours):
- Phase 1: Server setup (20 min)
- Phase 2: Backend setup (20 min)
- Phase 3: Systemd service (10 min)
- Phase 4: Frontend build (15 min)
- Phase 5: Apache config (5 min)
- Phase 6: Testing (20 min)
- Phase 7: Performance (10 min)
- Phase 8: Verification (10 min)
- Phase 9: Documentation (10 min)

**Realistic** (3 hours):
- Add 50% buffer for troubleshooting
- Thorough testing
- Complete documentation

**If Issues Occur** (4+ hours):
- Debugging database connections
- Apache configuration issues
- Service startup problems
- May require multiple attempts

---

## Resources

**Documentation**:
- README.md (this directory)
- CLAUDE.md (comprehensive guide)
- izzypy_xcri/PM_SESSION_013_COMPLETE.md (migration summary)

**Scripts**:
- deployment/deploy.sh (automated deployment - for future updates)
- deployment/xcri-api.service (systemd service)

**Configuration**:
- .htaccess (Apache config)
- api/.env (database credentials - CREATE MANUALLY)
- frontend/vite.config.js (build config)

**Related Apps** (for reference):
- /home/web4ustfccca/iz/xc-scoreboard
- /home/web4ustfccca/iz/season-resume

---

## Important Notes

**Database**:
- This app uses READ-ONLY access
- All data updates done via izzypy_xcri repository
- Never add write operations to this webapp

**Service Management**:
- User systemd (no sudo needed)
- Service runs as web4ustfccca user
- Auto-restarts on failure

**Git Workflow**:
- Match pattern of xc-scoreboard and season-resume
- Commit locally, push, then pull on server
- Use deployment/deploy.sh for regular updates

**Security**:
- .env file never committed to git
- API listens on localhost only (127.0.0.1)
- Apache proxies external requests
- Read-only database user enforced

---

## Communication Plan

**Before Deployment**:
- Notify stakeholders of deployment window
- No expected downtime (new deployment)

**During Deployment**:
- Test incrementally (backend first, then frontend)
- Document any issues immediately

**After Deployment**:
- Announce go-live URL
- Share API documentation link
- Collect initial feedback

---

## Ready to Deploy?

**Pre-flight Checklist**:
- [ ] Read README.md
- [ ] Read CLAUDE.md
- [ ] SSH access verified
- [ ] Database access verified
- [ ] In correct directory (iz-apps-clean/xcri)
- [ ] Git repository status confirmed

**If all checked**: Proceed with Phase 1

**If any unchecked**: Review prerequisites first

---

**Session**: Deployment Session 001
**Status**: READY TO EXECUTE
**Target**: web4.ustfccca.org/iz/xcri
**Next**: Begin Phase 1 (Server Setup)

🚀 **Good luck with the deployment!**
