# XCRI Subagent Specifications

This document contains specifications for specialized subagents that can be deployed if needed to automate high-frequency, high-risk operations with guaranteed correct procedures.

**Status**: Not yet implemented - Specifications only
**Created**: October 29, 2025 (Session 020)
**Context**: Created after Session 020 catastrophic deployment failures to document correct procedures for potential automation

---

## Design Principles

All XCRI subagents follow these principles:

1. **Single Responsibility Principle (SRP)**: Each agent has one clear purpose
2. **Explicit Input/Output Contracts**: Clear parameters in, clear results out
3. **Safety First**: Built-in verification steps and rollback capabilities
4. **Human Approval Required**: No destructive operations without confirmation
5. **Comprehensive Logging**: Every step logged for debugging
6. **Fail-Safe Defaults**: If unsure, stop and ask

---

## Subagent 1: XCRI API Restart Agent

### Purpose

Safely restart the XCRI FastAPI application on production server with proper bytecode cache clearing and process verification.

### Responsibility

Restart the XCRI API uvicorn service following the exact procedure documented in CLAUDE.md CRITICAL RULE #4.

### When to Use

- After deploying backend code changes (Python files in api/)
- After changing .env configuration
- When API is serving old code despite correct files on server
- When API process appears hung or unresponsive

### When NOT to Use

- For frontend-only changes (no restart needed)
- If API is working correctly and no code changes were deployed
- During active user sessions (coordinate with user first)

### Input Parameters

```python
{
  "reason": str,                    # Why restart is needed (e.g., "deployed code changes")
  "verify_file": Optional[str],     # Path to verify on server before restart (e.g., "api/services/team_knockout_service.py")
  "verify_pattern": Optional[str],  # Pattern to grep for verification (e.g., "%%Y")
  "maintenance_mode": bool = False  # Whether to enable maintenance mode first
}
```

### Step-by-Step Procedure

#### Phase 1: Pre-Restart Verification

1. **Verify server connectivity**
   ```bash
   ssh ustfccca-web4 'echo "Connected"'
   ```
   - Expected: "Connected"
   - If fails: Stop and report connection error

2. **Count current processes**
   ```bash
   ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l'
   ```
   - Expected: 5 (or 0 if not running)
   - Log count for comparison after restart

3. **Verify deployed file (if verify_file provided)**
   ```bash
   ssh ustfccca-web4 'grep -c "PATTERN" /home/web4ustfccca/public_html/iz/xcri/api/PATH'
   ```
   - Expected: Pattern found
   - If fails: Stop and report "deployed file missing or incorrect"

4. **Enable maintenance mode (if requested)**
   ```bash
   ssh ustfccca-web4 'touch /home/web4ustfccca/public_html/iz/xcri/.maintenance'
   ```

#### Phase 2: Process Termination

5. **Kill all Python processes**
   ```bash
   ssh ustfccca-web4 'killall -9 python3.9 2>/dev/null'
   ```
   - Note: Returns non-zero if no processes found (acceptable)

6. **Wait for cleanup**
   ```bash
   sleep 3
   ```

7. **Verify processes terminated**
   ```bash
   ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l'
   ```
   - Expected: 0
   - If >0: Report "zombie processes detected" with PIDs

#### Phase 3: Cache Clearing

8. **Clear bytecode cache (.pyc files)**
   ```bash
   ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && find . -name "*.pyc" -delete 2>/dev/null'
   ```

9. **Clear __pycache__ directories**
   ```bash
   ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null'
   ```

#### Phase 4: API Startup

10. **Start uvicorn with 4 workers**
    ```bash
    ssh ustfccca-web4 'cd /home/web4ustfccca/public_html/iz/xcri/api && source venv/bin/activate && nohup uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4 >> ../logs/api-live.log 2>&1 &'
    ```

11. **Wait for worker initialization**
    ```bash
    sleep 10
    ```
    - Critical: Workers need 6-10 seconds to initialize

#### Phase 5: Post-Restart Verification

12. **Count new processes**
    ```bash
    ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l'
    ```
    - Expected: 5 (1 parent + 4 workers)
    - If !=5: Report "incorrect process count: N"

13. **Test health endpoint**
    ```bash
    curl -s "https://web4.ustfccca.org/iz/xcri/api/health" | python3 -m json.tool
    ```
    - Expected: Valid JSON with status: "healthy"
    - Check response time (<2 seconds)
    - If fails: Report "health check failed" with error

14. **Test specific endpoint (if provided)**
    ```bash
    curl -s "https://web4.ustfccca.org/iz/xcri/api/ENDPOINT" | python3 -m json.tool | head -20
    ```
    - Expected: Valid JSON response
    - If error: Report specific API error

15. **Disable maintenance mode (if enabled)**
    ```bash
    ssh ustfccca-web4 'rm -f /home/web4ustfccca/public_html/iz/xcri/.maintenance'
    ```

### Output Format

```json
{
  "success": true,
  "restart_reason": "deployed code changes",
  "timestamp": "2025-10-29T15:30:00Z",
  "pre_restart": {
    "processes_before": 5,
    "file_verified": true
  },
  "post_restart": {
    "processes_after": 5,
    "health_check": "passed",
    "response_time_ms": 156
  },
  "warnings": [],
  "errors": []
}
```

### Error Handling

| Error | Action |
|-------|--------|
| SSH connection failed | Stop immediately, report connection error |
| File verification failed | Stop, report file missing or incorrect |
| Processes won't terminate | Report PIDs, suggest manual intervention |
| API won't start | Check logs, report startup error |
| Wrong process count | Report count, suggest investigating logs |
| Health check fails | Attempt one retry after 5 seconds, then report failure |

### Safety Checks

- ✅ Never run git operations on production server
- ✅ Never delete application files (only .pyc cache)
- ✅ Always verify file on server matches expectation before restart
- ✅ Always count processes before and after
- ✅ Always test health endpoint before declaring success
- ✅ Maintenance mode optional but recommended for user-facing updates

### Related Documentation

- CLAUDE.md: CRITICAL RULE #4 - API Process Restart After Code Changes
- docs/operations/API_RESTART_GUIDE.md: Detailed manual procedures

---

## Subagent 2: XCRI Frontend Deploy Agent

### Purpose

Safely deploy XCRI frontend React application to production server without destroying backend files.

### Responsibility

Build and deploy frontend code following the exact procedure documented in CLAUDE.md with explicit prohibitions against destructive flags.

### When to Use

- After making changes to frontend React code (src/)
- After updating frontend dependencies (package.json)
- When frontend displays old code despite changes

### When NOT to Use

- For backend-only changes (API code)
- If frontend is working correctly and no changes were made

### Input Parameters

```python
{
  "build_first": bool = True,       # Whether to run npm build before deploy
  "verify_build": bool = True,      # Whether to verify dist/ exists before deploy
  "dry_run": bool = False           # If true, show what would be deployed without deploying
}
```

### Step-by-Step Procedure

#### Phase 1: Local Build

1. **Verify we're in correct directory**
   ```bash
   pwd  # Should be /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
   ```
   - Expected: Ends with "iz-apps-clean/xcri"
   - If wrong: Stop and report incorrect directory

2. **Change to frontend directory**
   ```bash
   cd frontend
   ```

3. **Verify package.json exists**
   ```bash
   ls package.json
   ```
   - Expected: File exists
   - If missing: Stop and report "not in frontend directory"

4. **Run npm build (if build_first=true)**
   ```bash
   npm run build
   ```
   - Expected: Exit code 0, dist/ directory created
   - If fails: Stop and report build error with log

5. **Verify dist/ directory exists**
   ```bash
   ls -la dist/
   ```
   - Expected: Directory exists with index.html, assets/, etc.
   - If missing: Stop and report "build failed - no dist/"

6. **Count files in dist/**
   ```bash
   find dist/ -type f | wc -l
   ```
   - Expected: >10 files (index.html + assets)
   - Log count for verification

#### Phase 2: Dry Run (if requested)

7. **Show what would be deployed (if dry_run=true)**
   ```bash
   rsync -avzn dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/
   ```
   - Show file list to user
   - Ask for confirmation before proceeding

#### Phase 3: Deployment

8. **Deploy frontend files (WITHOUT --delete flag)**
   ```bash
   rsync -avz dist/ ustfccca-web4:/home/web4ustfccca/public_html/iz/xcri/
   ```
   - ⚠️ CRITICAL: NEVER use --delete flag
   - --delete would remove .htaccess, api-proxy.cgi, api/ directory

9. **Verify deployment succeeded**
   - Check rsync exit code
   - Expected: Exit code 0
   - If non-zero: Stop and report deployment error

#### Phase 4: Post-Deploy Verification

10. **Verify critical backend files still exist**
    ```bash
    ssh ustfccca-web4 'ls -la /home/web4ustfccca/public_html/iz/xcri/.htaccess /home/web4ustfccca/public_html/iz/xcri/api-proxy.cgi'
    ```
    - Expected: Both files exist
    - If missing: **CRITICAL ERROR** - backend files deleted!

11. **Verify frontend deployed**
    ```bash
    ssh ustfccca-web4 'ls -la /home/web4ustfccca/public_html/iz/xcri/index.html /home/web4ustfccca/public_html/iz/xcri/assets/'
    ```
    - Expected: Files exist with recent timestamps
    - If old timestamps: Deployment may have failed

12. **Test frontend loads**
    ```bash
    curl -I https://web4.ustfccca.org/iz/xcri/
    ```
    - Expected: HTTP 200 with text/html content type
    - If 404/500: Report frontend loading error

13. **Test API still accessible**
    ```bash
    curl -s https://web4.ustfccca.org/iz/xcri/api/health
    ```
    - Expected: Valid JSON health response
    - If fails: **CRITICAL** - API routing broken

### Output Format

```json
{
  "success": true,
  "build_time_seconds": 8.3,
  "files_deployed": 47,
  "deployment_time_seconds": 2.1,
  "verification": {
    "backend_files_intact": true,
    "frontend_loads": true,
    "api_accessible": true
  },
  "warnings": [],
  "errors": []
}
```

### Error Handling

| Error | Action |
|-------|--------|
| Not in correct directory | Stop, show current directory |
| npm build fails | Stop, show build error log |
| dist/ missing | Stop, report build failure |
| Backend files deleted | **CRITICAL** - Emergency restore procedure |
| Frontend won't load | Check .htaccess, check file permissions |
| API inaccessible | Check api-proxy.cgi exists and is executable |

### Safety Checks

- ✅ NEVER use --delete flag with rsync
- ✅ Always verify dist/ exists before deploying
- ✅ Always verify backend files (.htaccess, api-proxy.cgi, api/) still exist after deploy
- ✅ Always test both frontend and API after deployment
- ✅ Build locally, not on production server
- ✅ Dry run available for verification before actual deploy

### Related Documentation

- CLAUDE.md: "⚠️ CRITICAL: Frontend Deployment Best Practices"
- CLAUDE.md: Emergency Recovery Procedures (if backend files deleted)

---

## Subagent 3: IZ Applications Verification Agent

### Purpose

Verify all IZ applications (XCRI, xc-scoreboard, season-resume, root /iz) are operational after any deployment or maintenance.

### Responsibility

Execute comprehensive health checks on all IZ applications following CLAUDE.md CRITICAL RULE #6 verification checklist.

### When to Use

- After ANY deployment to /iz or subdirectories
- After database configuration changes
- After server maintenance or restarts
- When troubleshooting production issues
- As part of deployment pipeline verification

### When NOT to Use

- During development (local testing only)
- If only planning changes (not yet deployed)

### Input Parameters

```python
{
  "verbose": bool = True,           # Whether to show detailed output
  "include_detailed_tests": bool = False,  # Whether to test specific endpoints beyond health checks
  "fail_fast": bool = False         # Whether to stop on first failure or check all
}
```

### Step-by-Step Procedure

#### Phase 1: XCRI Application

1. **Test XCRI Frontend**
   ```bash
   curl -I https://web4.ustfccca.org/iz/xcri/
   ```
   - Expected: HTTP 200, text/html
   - If fails: Report frontend loading error

2. **Test XCRI API Health**
   ```bash
   curl -s "https://web4.ustfccca.org/iz/xcri/api/health"
   ```
   - Expected: Valid JSON with status: "healthy"
   - Parse database counts (athletes, teams, etc.)
   - If fails: Report API health check error

3. **Verify XCRI API Processes**
   ```bash
   ssh ustfccca-web4 'ps aux | grep "[p]ython3.9.*uvicorn" | wc -l'
   ```
   - Expected: 5 (1 parent + 4 workers)
   - If !=5: Report "XCRI API incorrect process count: N"

4. **Test XCRI Team Knockout endpoint (if detailed)**
   ```bash
   curl -s "https://web4.ustfccca.org/iz/xcri/api/team-knockout/?limit=1"
   ```
   - Expected: Valid JSON with 1 ranking
   - Verify new fields present (regl_group_name, conf_group_name, most_recent_race_date)

#### Phase 2: XC Scoreboard Application

5. **Test XC Scoreboard**
   ```bash
   curl -I https://web4.ustfccca.org/iz/xc-scoreboard/
   ```
   - Expected: HTTP 200, text/html
   - If fails: Report xc-scoreboard loading error

6. **Verify XC Scoreboard Database Connection (if detailed)**
   - Parse response for database error messages
   - Check for "Access denied" errors
   - If found: Report database configuration issue

#### Phase 3: Season Resume Application

7. **Test Season Resume**
   ```bash
   curl -I https://web4.ustfccca.org/iz/season-resume/
   ```
   - Expected: HTTP 200, text/html
   - If fails: Report season-resume loading error

8. **Verify Season Resume Database Connection (if detailed)**
   - Parse response for database error messages
   - Check for "No module named 'shared.database'" errors
   - If found: Report shared directory missing

#### Phase 4: Root IZ Landing Page

9. **Test Root IZ Page**
   ```bash
   curl -I https://web4.ustfccca.org/iz/
   ```
   - Expected: HTTP 200, text/html
   - If fails: Report root /iz loading error

#### Phase 5: Critical Files Check

10. **Verify Shared Directory Exists**
    ```bash
    ssh ustfccca-web4 'ls -la /home/web4ustfccca/public_html/iz/shared/'
    ```
    - Expected: Directory exists with database.py, utils.py
    - If missing: **CRITICAL** - shared directory deleted

11. **Verify .env Files Exist**
    ```bash
    ssh ustfccca-web4 'ls -la /home/web4ustfccca/public_html/iz/.env /home/web4ustfccca/public_html/iz/xc-scoreboard/.env /home/web4ustfccca/public_html/iz/season-resume/.env /home/web4ustfccca/public_html/iz/xcri/api/.env'
    ```
    - Expected: All 4 .env files exist
    - If missing: Report which .env files missing

12. **Verify Database Host Configuration (if detailed)**
    ```bash
    ssh ustfccca-web4 'grep "DB_HOST" /home/web4ustfccca/public_html/iz/.env /home/web4ustfccca/public_html/iz/xc-scoreboard/.env /home/web4ustfccca/public_html/iz/season-resume/.env /home/web4ustfccca/public_html/iz/xcri/api/.env'
    ```
    - Expected: All show "localhost" (not remote IP)
    - If remote IP: Report database configuration error

#### Phase 6: Response Time Testing (if detailed)

13. **Measure Response Times**
    - XCRI Frontend: `curl -w "%{time_total}" https://web4.ustfccca.org/iz/xcri/`
    - XCRI API Health: `curl -w "%{time_total}" https://web4.ustfccca.org/iz/xcri/api/health`
    - Expected: <2 seconds for frontend, <500ms for API
    - If slow: Report performance warning

### Output Format

```json
{
  "success": true,
  "timestamp": "2025-10-29T15:45:00Z",
  "results": {
    "xcri_frontend": {
      "status": "healthy",
      "http_code": 200,
      "response_time_ms": 1234
    },
    "xcri_api": {
      "status": "healthy",
      "http_code": 200,
      "processes": 5,
      "database_counts": {
        "athletes": 60000,
        "teams": 36000
      },
      "response_time_ms": 156
    },
    "xc_scoreboard": {
      "status": "healthy",
      "http_code": 200
    },
    "season_resume": {
      "status": "healthy",
      "http_code": 200
    },
    "root_iz": {
      "status": "healthy",
      "http_code": 200
    }
  },
  "critical_files": {
    "shared_directory": "exists",
    "env_files": "all_present",
    "database_config": "correct"
  },
  "warnings": [],
  "errors": [],
  "summary": "All 5 IZ applications operational"
}
```

### Error Handling

| Error | Severity | Action |
|-------|----------|--------|
| Any application returns non-200 | High | Report which app and HTTP code |
| XCRI API wrong process count | Medium | Report process count, suggest restart |
| Shared directory missing | **CRITICAL** | Emergency restore required |
| .env files missing | High | Report missing files, restoration needed |
| Database host is remote IP | High | Report configuration error, needs localhost |
| Response times >5 seconds | Medium | Performance warning |

### Success Criteria

All of the following must be true:
- ✅ All 5 applications return HTTP 200
- ✅ XCRI API health check returns valid JSON
- ✅ XCRI API has 5 processes running
- ✅ Shared directory exists with required files
- ✅ All .env files exist in correct locations
- ✅ No "Access denied" database errors

### Safety Checks

- ✅ Read-only operations only (no deployments or restarts)
- ✅ Can be run at any time without risk
- ✅ Comprehensive checking prevents false positives
- ✅ Clear output distinguishes warnings vs errors

### Related Documentation

- CLAUDE.md: CRITICAL RULE #6 - Deployment Verification Checklist
- CLAUDE.md: Emergency Recovery Procedures

---

## Deployment Priority

If implementing these subagents:

1. **Priority 1: API Restart Agent** (highest value)
   - Most frequent operation (multiple times per session)
   - Most error-prone (multi-step with timing requirements)
   - Highest impact if done incorrectly (API down)

2. **Priority 2: Verification Agent** (high value)
   - Should be run after EVERY deployment
   - Catches errors before users encounter them
   - Low risk (read-only operations)

3. **Priority 3: Frontend Deploy Agent** (medium value)
   - Less frequent than API restarts
   - Documentation may be sufficient
   - Main value is enforcing no --delete flag

---

## Implementation Notes

### Tools Required
- Bash (for SSH and curl commands)
- Read/Write (for reading CLAUDE.md, writing logs)
- Grep (for verifying patterns in deployed files)

### Estimated Complexity
- API Restart Agent: **Medium** (15-20 steps, timing critical)
- Frontend Deploy Agent: **Low-Medium** (13 steps, mostly straightforward)
- Verification Agent: **Medium** (13+ tests, comprehensive checking)

### Testing Strategy
- Test on development setup first
- Verify each phase independently
- Test error conditions (missing files, wrong ports, etc.)
- Dry-run mode for all destructive operations

---

**Last Updated**: October 29, 2025 (Session 020)
**Status**: Specifications complete, awaiting implementation decision
