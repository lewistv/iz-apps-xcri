# XCRI API Async Migration & Performance Upgrade Plan

**Created**: October 23, 2025
**Priority**: HIGH - **Experiencing production slowdowns at peak traffic**
**Implementation**: Scheduled for late-night maintenance window

---

## Traffic Analysis

### Current Load (Yesterday's Stats)
- **Unique Visitors**: 18,000
- **Pages per Visitor**: 10 average
- **Total Page Loads**: **180,000**
- **Time on Site**: 3+ minutes average
- **Issues Observed**: Slow response times and timeouts during peak traffic

###calculated Backend Load Estimate
**Assumptions**:
- Each page load = 3-5 API requests (athlete list, metadata, filters)
- Average: 4 API requests per page
- Total API requests/day: **180,000 × 4 = 720,000 requests**
- Peak traffic (8am-10pm, 14 hours): ~51,400 requests/hour
- **Peak concurrent users**: ~100-200 simultaneously

**Current Bottleneck**:
- Single worker = handles 1 request at a time
- No connection pooling = 10-50ms overhead per request
- Result: Requests queue up → timeouts → bad user experience

---

## Database Connection Budget Analysis

### MySQL Server Configuration
**Unable to query directly** (access denied without password in SSH session), but we can make safe assumptions:

**Standard MariaDB/MySQL Limits**:
- Default `max_connections`: **151** (typical)
- Safe operating zone: Use ≤ 100 connections (leave 51 for overhead)
- Conservative assumption for planning: **100 available connections**

### Current IZ Apps Connection Usage

**Apps Deployed** (from `/home/web4ustfccca/public_html/iz/`):
1. **season-resume** - Flask CGI app
2. **xc-scoreboard** - Flask CGI app
3. **xcri** - FastAPI (current - uvicorn)

**Shared Database Pool Configuration** (from `shared/database.py:84`):
- Pool size per app: **2 connections** (standard mode)
- Pool size per app: **3 connections** (admin mode)
- Optimized for CGI: "6 apps × 2 connections = 12 connections max"

**Estimated Current Usage**:
- season-resume: 2 connections
- xc-scoreboard: 2 connections
- xcri (current, no pooling): 0-10 transient connections
- **Total**: ~4-14 connections baseline

###Proposed XCRI Configuration

**Multi-Worker Setup** (4 workers recommended):
- Workers: 4
- Pool per worker: 10 connections
- Total XCRI connections: **40 connections**

**Total Server Load**:
- Other apps: ~4 connections
- XCRI: 40 connections
- **Total**: ~44 connections
- **Headroom**: 56 connections available (under 100 limit)
- **Safety margin**: Excellent ✅

---

## Architecture Comparison

### Current Architecture (Synchronous)
```
User Request → Apache → Reverse Proxy → Uvicorn (1 worker)
                                           ↓
                                    PyMySQL (no pooling)
                                           ↓
                                    MySQL Connection (new each time)
                                           ↓
                                    Query → Close Connection
```

**Problems**:
- ❌ One request at a time (blocking)
- ❌ Connection overhead every request (10-50ms)
- ❌ Python GIL limits single-threaded performance
- ❌ No connection reuse
- ❌ Queued requests timeout under load

### Proposed Architecture (Async)
```
User Request → Apache → Reverse Proxy → Uvicorn (4 workers)
                                           ↓
                                    aiomysql Pool (10 connections each)
                                           ↓
                                    Reused MySQL Connection
                                           ↓
                                    Async Query → Connection returns to pool
```

**Benefits**:
- ✅ 4 requests simultaneously (4x throughput)
- ✅ Non-blocking async I/O (better concurrency)
- ✅ Connection reuse (eliminate overhead)
- ✅ 40 pooled connections ready (no wait)
- ✅ Better CPU utilization across cores

---

## Implementation Plan

### Phase 1: Preparation (This Session - No Downtime)

#### 1.1: Update Dependencies
**Add to `api/requirements.txt`**:
```txt
aiomysql==0.2.0
cryptography==41.0.7  # Required by aiomysql
```

#### 1.2: Create Async Database Module
**New file**: `api/database_async.py`
- Implement aiomysql connection pool
- Add lifecycle management (startup/shutdown)
- Provide async context managers
- Keep existing `database.py` for backward compatibility during migration

#### 1.3: Create Maintenance Mode Page
**New file**: `frontend/public/maintenance.html`
- Custom maintenance page
- "Runners around trees" animation/image
- "Check back in 30 minutes" message
- Styled to match USTFCCCA branding

#### 1.4: Test in Development
- Install dependencies locally
- Test async database module
- Convert 1-2 endpoints as proof of concept
- Verify connection pooling works
- Check memory usage

### Phase 2: Migration (Maintenance Window - ~30 minutes downtime)

**Scheduled**: Late night / early morning (low traffic)

#### 2.1: Pre-Migration Checklist (5 minutes)
- [ ] Backup current working API code
- [ ] Test maintenance page displays correctly
- [ ] Verify rollback procedure ready
- [ ] Have monitoring dashboard open

#### 2.2: Enable Maintenance Mode (1 minute)
```bash
# Apache redirect all /iz/xcri/ traffic to maintenance page
# Modify .htaccess or use separate maintenance.htaccess
```

#### 2.3: Deploy Code Changes (10 minutes)
```bash
# On local machine
cd /Users/lewistv/code/ustfccca/iz-apps-clean/xcri
git add .
git commit -m "[XCRI] Async migration with connection pooling and multi-worker support"
git push origin main

# On server
ssh ustfccca-web4
cd /home/web4ustfccca/public_html/iz/xcri
git pull origin main

# Install new dependencies
cd api
source venv/bin/activate
pip install -r requirements.txt
```

#### 2.4: Stop Current API (1 minute)
```bash
# Find and kill current process
ps aux | grep "[u]vicorn main:app"
kill <PID>

# Verify stopped
ps aux | grep uvicorn
```

#### 2.5: Start New Multi-Worker API (2 minutes)
```bash
cd /home/web4ustfccca/public_html/iz/xcri/api
source venv/bin/activate

# Start with 4 workers and connection pooling
nohup uvicorn main:app \
  --host 127.0.0.1 \
  --port 8001 \
  --workers 4 \
  >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &

echo "Started PID: $!"
```

#### 2.6: Verify Startup (5 minutes)
```bash
# Check logs for all 4 workers starting
tail -f /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log

# Look for:
# - "Started server process [PID]" (4 times)
# - "Connection pool initialized" (4 times)
# - "Application startup complete" (4 times)

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:8001/metadata/latest/date
curl "http://localhost:8001/athletes/?division=2030&gender=M&limit=5"
```

#### 2.7: Disable Maintenance Mode (1 minute)
```bash
# Restore normal .htaccess
# Remove maintenance redirect
```

#### 2.8: Monitor Production (5 minutes)
- Test public URLs in browser
- Check API response times
- Monitor error logs
- Verify athlete/team pages load correctly
- Check connection pool usage in logs

### Phase 3: Rollback (If Needed - 5 minutes)

**If something goes wrong**:

```bash
# 1. Enable maintenance mode
# 2. Stop new API
ps aux | grep uvicorn | awk '{print $2}' | xargs kill

# 3. Revert code
cd /home/web4ustfccca/public_html/iz/xcri
git reset --hard HEAD~1

# 4. Start old API (single worker, sync)
cd api
source venv/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port 8001 \
  >> /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log 2>&1 &

# 5. Disable maintenance mode
# 6. Investigate issue
```

---

## Code Changes Required

### 1. Database Module (New: `api/database_async.py`)

```python
"""
XCRI Rankings API - Async Database Connection Management with Pooling
"""

import logging
import aiomysql
from contextlib import asynccontextmanager
from typing import Optional

logger = logging.getLogger(__name__)

# Global connection pool (initialized at app startup)
pool: Optional[aiomysql.Pool] = None


async def create_pool(config: dict, pool_size: int = 10):
    """
    Create async MySQL connection pool at application startup.

    Args:
        config: Database configuration from settings
        pool_size: Number of connections in pool (default: 10 per worker)
    """
    global pool
    try:
        pool = await aiomysql.create_pool(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            db=config['database'],
            minsize=5,              # Keep 5 connections ready
            maxsize=pool_size,      # Maximum 10 connections per worker
            autocommit=True,
            charset='utf8mb4',
            connect_timeout=5,
            pool_recycle=3600,      # Recycle connections after 1 hour
        )
        logger.info(f"✓ Async connection pool initialized (size: {pool_size})")
    except Exception as e:
        logger.error(f"✗ Failed to create connection pool: {e}")
        raise


async def close_pool():
    """Close connection pool at application shutdown."""
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        logger.info("✓ Connection pool closed")


@asynccontextmanager
async def get_db():
    """
    Async context manager for database connections from pool.

    Usage:
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM table")
                results = await cursor.fetchall()
    """
    if not pool:
        raise RuntimeError("Connection pool not initialized. Call create_pool() first.")

    async with pool.acquire() as conn:
        yield conn


@asynccontextmanager
async def get_db_cursor():
    """
    Async context manager for database cursor (simplified).

    Usage:
        async with get_db_cursor() as cursor:
            await cursor.execute("SELECT * FROM table")
            results = await cursor.fetchall()
    """
    async with get_db() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield cursor


async def test_connection() -> bool:
    """Test database connection from pool."""
    try:
        async with get_db_cursor() as cursor:
            await cursor.execute("SELECT 1")
            await cursor.fetchone()
        logger.info("✓ Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection test failed: {e}")
        return False
```

### 2. Main Application (Update: `api/main.py`)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with connection pool management."""
    # Startup
    logger.info("=" * 60)
    logger.info("XCRI Rankings API - Starting Up (Async Mode)")
    logger.info("=" * 60)

    try:
        # Create async connection pool
        from database_async import create_pool
        config = {
            'host': settings.database_host,
            'port': settings.database_port,
            'user': settings.database_user,
            'password': settings.database_password,
            'database': settings.database_name,
        }
        await create_pool(config, pool_size=10)
        logger.info("✓ Async database connection pool initialized")

    except Exception as e:
        logger.error(f"✗ Startup failed: {e}")
        raise

    logger.info("✓ XCRI Rankings API - Ready")
    yield

    # Shutdown
    logger.info("XCRI Rankings API - Shutting Down")
    from database_async import close_pool
    await close_pool()
```

### 3. Service Layer (Example: `api/services/athlete_service.py`)

**Before (Sync)**:
```python
def get_athletes_list(...):
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results
```

**After (Async)**:
```python
async def get_athletes_list(...):
    async with get_db_cursor() as cursor:
        await cursor.execute(query, params)
        results = await cursor.fetchall()
    return results
```

### 4. Route Handlers (Example: `api/routes/athletes.py`)

**Before (Sync)**:
```python
@router.get("/athletes/")
def list_athletes(...):
    results = athlete_service.get_athletes_list(...)
    return results
```

**After (Async)**:
```python
@router.get("/athletes/")
async def list_athletes(...):
    results = await athlete_service.get_athletes_list(...)
    return results
```

**Files to Convert** (all services and routes):
- `services/athlete_service.py`
- `services/team_service.py`
- `services/snapshot_service.py`
- `services/metadata_service.py`
- `services/scs_service.py`
- `services/resume_service.py`
- `routes/athletes.py`
- `routes/teams.py`
- `routes/snapshots.py`
- `routes/metadata.py`
- `routes/scs.py`
- `routes/feedback.py`

---

## Performance Expectations

### Before Optimization
- **Throughput**: 1 request at a time (blocking)
- **Response Time**: 100-200ms (cached) + queue wait time
- **Connection Overhead**: 10-50ms per request
- **Peak Capacity**: ~10-20 concurrent users before slowdown
- **Database Connections**: 0-10 transient (created/destroyed each request)

### After Optimization
- **Throughput**: 4 requests simultaneously (4x improvement)
- **Response Time**: 50-100ms (no connection overhead + async)
- **Connection Overhead**: 0ms (pooled connections ready)
- **Peak Capacity**: 100-200 concurrent users (10x improvement)
- **Database Connections**: 40 pooled (4 workers × 10 connections)

### Expected Improvements
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Concurrent Capacity | 10-20 users | 100-200 users | **10x** |
| Throughput (req/sec) | ~5-10 | ~40-80 | **8x** |
| Response Time (avg) | 150ms + queue | 75ms | **50% faster** |
| Connection Overhead | 10-50ms | 0ms | **100% eliminated** |
| Timeout Errors | Frequent | Rare | **90% reduction** |

---

## Monitoring & Validation

### Metrics to Watch (First 24 Hours)

**1. API Response Times**:
```bash
# Check logs for timing
grep "INFO.*GET" /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | tail -100
```

**2. Worker Health**:
```bash
# All 4 workers running?
ps aux | grep "[u]vicorn main:app" | wc -l  # Should show 5 (1 master + 4 workers)
```

**3. Connection Pool Usage**:
```bash
# Check logs for pool stats
grep "pool" /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log
```

**4. Error Rate**:
```bash
# Any 500 errors?
grep "ERROR" /home/web4ustfccca/public_html/iz/xcri/logs/api-live.log | tail -20
```

**5. Memory Usage**:
```bash
# Monitor per-worker memory
ps aux | grep uvicorn | awk '{print $6}'  # RSS memory in KB
```

### Success Criteria

**Must Have** (Go/No-Go):
- ✅ All 4 workers start successfully
- ✅ Health endpoint returns 200
- ✅ Connection pools initialize (4 pools × 10 connections)
- ✅ No startup errors in logs
- ✅ Frontend loads athlete/team data correctly
- ✅ API response times < 200ms

**Nice to Have** (Monitor over time):
- ✅ Response times 50% faster
- ✅ No timeout errors during peak traffic
- ✅ Connection pool stable (no exhaustion)
- ✅ Memory usage < 150MB per worker

---

## Risk Assessment

### Low Risk ✅
- Connection pooling (proven pattern)
- Async/await in FastAPI (officially supported)
- 4 workers (conservative, plenty of headroom)
- Maintenance window (low traffic)

### Moderate Risk ⚠️
- First async migration for this app (test thoroughly)
- Multiple file changes (services + routes)
- New dependency (aiomysql)

### Mitigation Strategies
1. **Test Locally First**: Full local testing before deployment
2. **Maintenance Window**: Deploy during low-traffic period
3. **Rollback Ready**: Single git command to revert
4. **Monitoring**: Watch logs closely for first hour
5. **Gradual Load**: Natural traffic ramp-up (not instant)

### Rollback Triggers
**Revert immediately if**:
- Workers fail to start
- Connection pool errors
- 500 error rate > 5%
- Memory usage > 200MB per worker
- Response times slower than before

---

## Timeline

### This Session (Preparation - 2-3 hours)
- [x] Analysis and planning complete
- [ ] Create `database_async.py` module
- [ ] Update `requirements.txt`
- [ ] Create maintenance page HTML
- [ ] Convert 2-3 services to async (proof of concept)
- [ ] Test locally
- [ ] Commit code (DO NOT DEPLOY)

### Scheduled Maintenance Window (30-45 minutes)
**Recommended Time**: 2:00 AM - 3:00 AM ET (lowest traffic)

- [ ] Enable maintenance mode
- [ ] Deploy code
- [ ] Install dependencies
- [ ] Restart API with 4 workers
- [ ] Verify functionality
- [ ] Disable maintenance mode
- [ ] Monitor for 1 hour

### Day After (Monitoring)
- [ ] Review 24-hour metrics
- [ ] Check error logs
- [ ] Analyze response times
- [ ] Document lessons learned
- [ ] Update CLAUDE.md with new architecture

---

## Next Steps

**User Decision Point**:

1. **Proceed with Preparation** (This Session):
   - I'll implement all code changes
   - Create maintenance page
   - Test locally
   - Commit to git (not deployed)
   - Ready for maintenance window

2. **Schedule Maintenance Window**:
   - Choose date/time (late night recommended)
   - Announce to stakeholders if needed
   - Execute deployment plan

3. **Defer to Future Session**:
   - Document plan only
   - Implement when traffic justifies
   - Monitor current performance

**My Recommendation**: Option 1 (Proceed with Preparation)
- Your traffic (180K page loads/day) justifies this NOW
- Peak slowdowns = poor user experience
- Code will be ready, just need to pick deployment time
- Low risk with high reward

**What would you like to do?**

---

**End of Plan**
