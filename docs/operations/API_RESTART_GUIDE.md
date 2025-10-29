# XCRI API Restart Guide for Automated Agents

**Last Updated**: October 29, 2025 (Session 016)
**Target Audience**: Automated agents performing server maintenance
**Server**: web4.ustfccca.org
**Application**: XCRI Rankings API (FastAPI + Uvicorn)

---

## Table of Contents

1. [Overview](#overview)
2. [Process Architecture](#process-architecture)
3. [When to Restart](#when-to-restart)
4. [Pre-Restart Checklist](#pre-restart-checklist)
5. [Restart Procedure](#restart-procedure)
6. [Verification Steps](#verification-steps)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)
9. [Common Pitfalls](#common-pitfalls)

---

## Overview

The XCRI API runs on **Uvicorn ASGI server** with **4 worker processes** for production. This creates 5 total Python processes:
- 1 parent process (Uvicorn master)
- 4 worker processes (handling requests)

**Critical Facts**:
- All 5 processes MUST be killed during restart
- Python bytecode cache (.pyc files) MUST be cleared
- Workers take 6-8 seconds to fully start
- Maintenance mode should be enabled before restart
- Production uses unified log file (api-live.log)

---

## Process Architecture

### Current Production Configuration

```bash
# Production command
uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4

# Process tree structure
web4ustfccca 123456  # Parent process (Uvicorn master)
  ├─ web4ustfccca 123457  # Worker 1
  ├─ web4ustfccca 123458  # Worker 2
  ├─ web4ustfccca 123459  # Worker 3
  └─ web4ustfccca 123460  # Worker 4
```

### File Locations

```
/home/web4ustfccca/public_html/iz/xcri/
├── api/                          # Backend application
│   ├── main.py                   # FastAPI entry point
│   ├── venv/                     # Python virtual environment
│   └── [service files]
├── logs/
│   └── api-live.log              # Production log file (UNIFIED)
├── .htaccess                     # Apache configuration
└── frontend/dist/                # React build
```

---

## When to Restart

### Scenarios Requiring Restart

1. **Backend code deployment**:
   - New service files (e.g., team_knockout_service.py)
   - Updated route handlers
   - Modified models.py or main.py
   - Database connection changes

2. **Configuration changes**:
   - .env file modifications
   - Database credentials updated
   - API settings changed

3. **Performance issues**:
   - Memory leaks suspected
   - Hanging worker processes
   - Slow response times

4. **After fixing bugs**:
   - SQL query fixes in service layer
   - Pydantic model updates
   - Import errors resolved

### Scenarios NOT Requiring Restart

- Frontend-only changes (React components)
- Static file updates
- .htaccess modifications (Apache reloads automatically)
- Documentation updates

---

## Pre-Restart Checklist

### Step 1: Verify Deployment Status

```bash
# Check what files were recently deployed
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  ls -lht services/*.py routes/*.py models.py main.py | head -10'

# Note timestamps - files uploaded AFTER current processes started need restart
```

### Step 2: Check Current Process Status

```bash
# Find when current processes started
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9" | head -5'

# Example output:
# web4ust+ 123456 ... 13:39 /path/to/python3.9  # Parent started at 13:39
# web4ust+ 123457 ... 13:39 /path/to/python3.9  # Workers also at 13:39
```

**Compare timestamps**:
- If service files were uploaded AFTER process start time → RESTART REQUIRED
- If process start time is AFTER file upload time → Processes have new code

### Step 3: Test Current Functionality

```bash
# Test health endpoint
curl -s https://web4.ustfccca.org/iz/xcri/api/health

# Test specific endpoint that may need updating
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1"
```

If endpoints return 404 for newly deployed routes → RESTART REQUIRED

### Step 4: Backup Current Configuration

```bash
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri && \
  cp .htaccess .htaccess.backup-$(date +%Y%m%d-%H%M%S)'
```

---

## Restart Procedure

### Phase 1: Enable Maintenance Mode

**Purpose**: Inform users that updates are in progress

```bash
# Edit .htaccess to add maintenance redirect at TOP of file
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri && \
  cat > .htaccess.maintenance << "EOF"
# ==========================================
# MAINTENANCE MODE - [Date/Session]
# Remove this block after restart complete
# ==========================================
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/iz/xcri/maintenance\.html$
RewriteCond %{REQUEST_URI} !^/iz/xcri/.*\.(css|js|png|jpg|jpeg|gif|ico|svg)$
RewriteRule ^.*$ /iz/xcri/maintenance.html [R=503,L]
ErrorDocument 503 /iz/xcri/maintenance.html
Header set Retry-After "600"
# END MAINTENANCE MODE
# ==========================================

EOF
  cat .htaccess.maintenance .htaccess > .htaccess.new && \
  mv .htaccess.new .htaccess'
```

**Verify**:
```bash
curl -I https://web4.ustfccca.org/iz/xcri/ | grep "HTTP"
# Should return: HTTP/1.1 503 Service Temporarily Unavailable
```

### Phase 2: Kill All Processes

**Critical**: Must kill ALL 5 processes (1 parent + 4 workers)

```bash
# Method 1: Pattern matching (PREFERRED)
ssh ustfccca-web4 'ps aux | grep "web4ust.*python3.9" | grep -v grep | awk "{print \$2}" | xargs kill -9 2>/dev/null'

# Wait for processes to fully terminate
sleep 3

# Verify all processes killed
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9" | wc -l'
# Should return: 0 (or close to 0)
```

**Why kill -9?**
- SIGTERM may leave zombie workers
- SIGKILL ensures immediate termination
- Production requirement for clean restart

**Common Issues**:
- If `ps aux | grep python` still shows processes → Repeat kill command
- Check for orphaned nohup processes → Kill by pattern: `pkill -9 -f "uvicorn main:app"`

### Phase 3: Clear Python Bytecode Cache

**Why**: Old .pyc files can cache outdated code, causing import errors

```bash
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete 2>/dev/null && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null'
```

**What this clears**:
- `*.pyc` files (compiled Python bytecode)
- `__pycache__` directories (Python 3 cache folders)

**Verification**:
```bash
ssh ustfccca-web4 'find /home/web4ustfccca/public_html/iz/xcri/api -name "*.pyc" | wc -l'
# Should return: 0
```

### Phase 4: Start Uvicorn with 4 Workers

```bash
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &'
```

**Important flags**:
- `--host 127.0.0.1`: Localhost only (Apache reverse proxy handles external)
- `--port 8001`: Production port
- `--workers 4`: Creates 1 parent + 4 workers = 5 processes
- `>> api-live.log 2>&1`: Unified logging (stdout + stderr to same file)
- `&`: Background process

**Wait for startup**:
```bash
sleep 6  # Workers need 6-8 seconds to fully initialize
```

---

## Verification Steps

### Step 1: Process Count Verification

```bash
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9" | wc -l'
# Expected: 5 (1 parent + 4 workers)
```

**If count is wrong**:
- Less than 5 → Workers failed to start (check logs)
- More than 5 → Old processes not killed (repeat Phase 2)

### Step 2: Health Endpoint Test

```bash
# Test localhost (direct to uvicorn)
ssh ustfccca-web4 'curl -s http://127.0.0.1:8001/health | python3 -m json.tool'

# Expected response:
# {
#     "status": "healthy",
#     "api_version": "2.0.0",
#     "database_connected": true,
#     ...
# }
```

**If health check fails**:
1. Check logs: `ssh ustfccca-web4 'tail -50 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log'`
2. Look for import errors, database connection failures, or missing environment variables
3. Verify .env file exists and is readable

### Step 3: Swagger UI Verification

```bash
ssh ustfccca-web4 'curl -s http://127.0.0.1:8001/docs | head -20'
# Should return HTML with "<title>XCRI Rankings API" or similar
```

### Step 4: Test New/Updated Endpoints

**Example: Team Knockout endpoints**

```bash
# Test 1: List endpoint
ssh ustfccca-web4 'curl -s "http://127.0.0.1:8001/team-knockout/?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=1" | python3 -m json.tool'

# Test 2: Single team
ssh ustfccca-web4 'curl -s "http://127.0.0.1:8001/team-knockout/714" | python3 -m json.tool'

# Test 3: Head-to-head matchup
ssh ustfccca-web4 'curl -s "http://127.0.0.1:8001/team-knockout/matchups/head-to-head?team_a_id=714&team_b_id=1699&season_year=2025" | python3 -m json.tool'
```

**Success criteria**:
- HTTP 200 OK for valid requests
- Valid JSON response structure
- No SQL errors or 500 Internal Server Errors
- Correct data returned (check team names, rankings match expectations)

### Step 5: Disable Maintenance Mode

**Only after ALL verification passes**

```bash
# Remove maintenance mode block from .htaccess (lines 2-12 typically)
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri && \
  sed -i "2,12d" .htaccess'

# Verify removal
ssh ustfccca-web4 'head -20 /home/web4ustfccca/public_html/iz/xcri/.htaccess'
# Should NOT contain maintenance mode redirect
```

### Step 6: Public URL Verification

```bash
# Test frontend
curl -I https://web4.ustfccca.org/iz/xcri/
# Should return: HTTP/1.1 200 OK

# Test API through public URL
curl -s https://web4.ustfccca.org/iz/xcri/api/health | python3 -m json.tool

# Test updated endpoints
curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1"
```

---

## Troubleshooting

### Issue 1: Import Errors After Restart

**Symptom**: Logs show `ImportError: cannot import name 'X' from 'models'`

**Cause**: Python bytecode cache not cleared, or new files not deployed

**Fix**:
```bash
# 1. Kill processes again
ssh ustfccca-web4 'ps aux | grep "web4ust.*python3.9" | grep -v grep | awk "{print \$2}" | xargs kill -9'

# 2. Aggressively clear cache
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null'

# 3. Verify deployed file
ssh ustfccca-web4 'grep -n "TeamKnockoutListResponse" /home/web4ustfccca/public_html/iz/xcri/api/models.py'
# Should find the class definition

# 4. Restart again
```

### Issue 2: 404 Errors for New Endpoints

**Symptom**: New routes return 404 Not Found

**Cause**: Workers loaded old code before file deployment, or router not registered

**Fix**:
```bash
# 1. Check router registration in main.py
ssh ustfccca-web4 'grep "team_knockout" /home/web4ustfccca/public_html/iz/xcri/api/main.py'
# Should show: app.include_router(team_knockout.router)

# 2. Verify file exists
ssh ustfccca-web4 'ls -lh /home/web4ustfccca/public_html/iz/xcri/api/routes/team_knockout.py'

# 3. Check file modification time vs process start time
ssh ustfccca-web4 'stat -c "%y" /home/web4ustfccca/public_html/iz/xcri/api/routes/team_knockout.py && \
  ps aux | grep "[p]ython3.9" | head -1'

# If file is OLDER than process → Deploy file again
# If file is NEWER than process → Need to restart (workers have old code)
```

### Issue 3: SQL Errors (Ambiguous Columns)

**Symptom**: 500 errors with message like "Column 'season_year' in WHERE is ambiguous"

**Cause**: SQL query missing table aliases in WHERE clause

**Fix**:
```bash
# 1. Edit service file locally to add table aliases
# Example: Change "WHERE season_year = %s" to "WHERE m.season_year = %s"

# 2. Deploy fixed file
scp api/services/team_knockout_service.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/services/

# 3. Restart API (follow full restart procedure)
```

### Issue 4: Only 1-2 Processes Running (Not 5)

**Symptom**: `ps aux | grep python | wc -l` returns less than 5

**Cause**: Startup error in one or more workers, or `--workers` flag missing

**Fix**:
```bash
# 1. Check logs for worker startup errors
ssh ustfccca-web4 'tail -100 /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log'

# Look for:
# - Import errors
# - Database connection failures
# - Missing .env variables

# 2. Verify uvicorn command includes --workers 4
ssh ustfccca-web4 'ps aux | grep "[u]vicorn main:app"'
# Should show: --workers 4

# 3. If --workers missing, kill and restart with correct command
```

### Issue 5: Health Endpoint Returns "Database Connection Failed"

**Symptom**: Health check shows `"database_connected": false`

**Cause**: Database credentials incorrect, or network issue

**Fix**:
```bash
# 1. Test database connection manually
ssh ustfccca-web4 'mysql --host=localhost --user=web4ustfccca_public \
  --password=[REDACTED] web4ustfccca_iz -e "SELECT 1"'

# 2. Verify .env file
ssh ustfccca-web4 'cat /home/web4ustfccca/public_html/iz/xcri/api/.env | grep DATABASE'

# 3. Check file permissions (should be 600)
ssh ustfccca-web4 'ls -la /home/web4ustfccca/public_html/iz/xcri/api/.env'
```

---

## Rollback Procedures

### When to Rollback

- New code causes 500 errors on critical endpoints
- Database queries failing due to SQL bugs
- Import errors preventing API startup
- Performance degradation after deployment

### Rollback Steps

#### Option 1: Restore Previous File Version

```bash
# 1. Check git history on server
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && git log --oneline -5'

# 2. Checkout previous commit (if server is git repo)
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && git checkout HEAD~1 services/team_knockout_service.py'

# 3. Restart API
```

#### Option 2: Redeploy from Local Backup

```bash
# 1. Use local git to find working version
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
git log --oneline api/services/team_knockout_service.py

# 2. Checkout previous commit locally
git checkout [commit-hash] api/services/team_knockout_service.py

# 3. Deploy to server
scp api/services/team_knockout_service.py ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/api/services/

# 4. Restart API
```

#### Option 3: Comment Out New Router (Emergency)

```bash
# If new endpoints are broken, disable them quickly:
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  sed -i "s/app.include_router(team_knockout.router)/# app.include_router(team_knockout.router)/" main.py'

# Restart API - new endpoints will 404 but rest of API works
```

---

## Common Pitfalls

### Pitfall 1: Forgetting to Kill All 5 Processes

**Problem**: Using `pkill -f "uvicorn main:app"` without `-9` flag leaves zombie workers

**Solution**: Always use pattern matching with `kill -9`:
```bash
ps aux | grep "web4ust.*python3.9" | grep -v grep | awk '{print $2}' | xargs kill -9
```

### Pitfall 2: Not Clearing Bytecode Cache

**Problem**: `.pyc` files cache old code, causing import errors even after deployment

**Solution**: ALWAYS run:
```bash
find . -name "*.pyc" -delete && find . -type d -name __pycache__ -exec rm -rf {} +
```

### Pitfall 3: Testing Too Soon After Restart

**Problem**: Testing health endpoint before workers finish starting (leads to false negatives)

**Solution**: Wait at least 6 seconds:
```bash
nohup uvicorn ... &
sleep 6  # WAIT for workers to initialize
curl http://127.0.0.1:8001/health
```

### Pitfall 4: Using Separate Log Files

**Problem**: Old scripts used `api-access.log` and `api-error.log` separately

**Solution**: Production uses unified logging:
```bash
>> api-live.log 2>&1  # Redirect both stdout and stderr to same file
```

### Pitfall 5: Forgetting Maintenance Mode

**Problem**: Restarting during high-traffic period without warning users

**Solution**: Always enable maintenance mode first, disable only after full verification

### Pitfall 6: Not Verifying Process Count

**Problem**: Assuming API is running if health check passes, but only 1 worker started

**Solution**: Check process count:
```bash
ps aux | grep "[p]ython3.9" | wc -l  # Should be 5
```

### Pitfall 7: Testing Only Localhost

**Problem**: API works on localhost but fails through public URL (Apache proxy issues)

**Solution**: Test both:
```bash
curl http://127.0.0.1:8001/health  # Localhost
curl https://web4.ustfccca.org/iz/xcri/api/health  # Public URL
```

---

## Quick Reference: Full Restart Command Sequence

```bash
# 1. Enable maintenance mode
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri && \
  cp .htaccess .htaccess.backup && \
  cat > .htaccess.maintenance << "EOF"
# MAINTENANCE MODE
RewriteEngine On
RewriteCond %{REQUEST_URI} !^/iz/xcri/maintenance\.html$
RewriteCond %{REQUEST_URI} !^/iz/xcri/.*\.(css|js|png|jpg|jpeg|gif|ico|svg)$
RewriteRule ^.*$ /iz/xcri/maintenance.html [R=503,L]
ErrorDocument 503 /iz/xcri/maintenance.html
Header set Retry-After "600"
# END MAINTENANCE MODE
EOF
  cat .htaccess.maintenance .htaccess > .htaccess.new && mv .htaccess.new .htaccess'

# 2. Kill all processes
ssh ustfccca-web4 'ps aux | grep "web4ust.*python3.9" | grep -v grep | awk "{print \$2}" | xargs kill -9 2>/dev/null'
sleep 3

# 3. Clear bytecode cache
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  find . -name "*.pyc" -delete 2>/dev/null && \
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null'

# 4. Start with 4 workers
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && \
  source venv/bin/activate && \
  nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 \
    >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &'
sleep 6

# 5. Verify (expect 5 processes)
ssh ustfccca-web4 'ps aux | grep "[p]ython3.9" | wc -l'

# 6. Test health
ssh ustfccca-web4 'curl -s http://127.0.0.1:8001/health | python3 -m json.tool | head -5'

# 7. Disable maintenance mode (after verification)
ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri && sed -i "2,12d" .htaccess'

# 8. Test public URL
curl -s https://web4.ustfccca.org/iz/xcri/api/health | python3 -m json.tool
```

---

## Session 016 Learnings (October 29, 2025)

### Key Discoveries

1. **Timing is critical**: Files deployed at 13:41 were not loaded by workers started at 13:39
2. **5-process architecture**: Always verify exactly 5 Python processes (1 parent + 4 workers)
3. **SQL ambiguous columns**: WHERE clauses in joins MUST use table aliases (e.g., `m.season_year`)
4. **Bytecode caching**: Must clear `.pyc` files after every code deployment
5. **Unified logging**: Production uses `api-live.log` (not separate access/error files)

### Bugs Fixed During Restart

1. **Head-to-head matchup SQL**: Added `m.` prefix to WHERE clause columns to resolve ambiguous references
2. **Common opponents ORDER BY**: Changed from alias reference to full SUM expression with parameters
3. **Meet matchups query**: Added table alias to all WHERE clause columns

### Endpoint Status After Fixes

- ✅ `/team-knockout/` (list) - HTTP 200
- ✅ `/team-knockout/{id}` (single team) - HTTP 200
- ⚠️ `/team-knockout/matchups` - HTTP 422 (Pydantic validation issue - deferred to Session 017)
- ✅ `/team-knockout/matchups/head-to-head` - HTTP 200
- ✅ `/team-knockout/matchups/meet/{race_hnd}` - SQL fixed (404 = no data for test race)
- ✅ `/team-knockout/matchups/common-opponents` - HTTP 200

**Success Rate**: 5/6 endpoints operational (83%)

---

## Additional Resources

- **Local restart script**: `/deployment/restart-api.sh`
- **Production logs**: `/home/web4ustfccca/public_html/iz/xcri/logs/api-live.log`
- **CLAUDE.md**: Project-level documentation with architecture details
- **Session 016 prompt**: `/docs/sessions/session-016-prompt.md`

---

**Document Version**: 1.0
**Created**: October 29, 2025
**Author**: Session 016 (Automated Agent Documentation Initiative)
