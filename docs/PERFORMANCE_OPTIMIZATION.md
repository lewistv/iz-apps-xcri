# XCRI API Performance Optimization Plan

**Created**: October 23, 2025
**Status**: Analysis Complete - Implementation Pending
**Priority**: High (Most resource-intensive app on server)

---

## Current Architecture Analysis

### Database Connection Model
**Current Implementation**: **Per-Request Connection Pattern**
- **Method**: PyMySQL with context managers (`get_db()`, `get_db_cursor()`)
- **Connection Lifecycle**: Open → Query → Close (every request)
- **Connection Pooling**: ❌ **NONE**
- **Async Support**: ❌ **Synchronous only**

**Key Code** (database.py:62-89):
```python
@contextmanager
def get_db():
    conn = None
    try:
        conn = pymysql.connect(**db_config.to_dict())  # NEW CONNECTION EVERY TIME
        yield conn
    finally:
        if conn:
            conn.close()  # CLOSED AFTER EVERY REQUEST
```

### API Server Configuration
**Current Setup**: **Single Uvicorn Worker**
- **Workers**: 1 (blocking synchronous operations)
- **Concurrency**: Limited by Python GIL (Global Interpreter Lock)
- **Port**: 8001 (localhost only, proxied via Apache)
- **Command**: `uvicorn main:app --host 127.0.0.1 --port 8001`

### Resource Usage
**Current Metrics**:
- **Memory**: 92 MB (PID 698808)
- **CPU**: 2.5% baseline
- **Uptime**: 19+ hours (since Oct 22)
- **Database Records**: 418K athletes, 36K teams, 60K SCS components

---

## Identified Bottlenecks

### 🔴 CRITICAL: No Connection Pooling
**Impact**: **HIGH**
- Every API request creates a new database connection
- Connection establishment overhead: ~10-50ms per request
- Under load: Connection creation becomes dominant cost
- Risk: Exhausting MySQL max_connections limit

**Example Scenario**:
- 100 concurrent users browsing rankings
- Each page load = 3-5 API requests
- Total: 300-500 simultaneous connection attempts
- Current: Creates/destroys 300-500 connections
- With pooling: Reuses 10-20 connections

### 🟡 MODERATE: Single Worker Process
**Impact**: MODERATE
- Only one request processed at a time (blocking)
- Python GIL prevents true parallelism in single process
- CPU cores underutilized (only 2.5% usage)
- Response time degrades under concurrent load

### 🟢 LOW: Frontend Caching Already Optimized
**Session 007 Achievement**: ✅ **99% reduction in metadata queries**
- sessionStorage caching active
- Only 1% of page loads hit database for dates
- Excellent optimization already in place

---

## Optimization Strategy

### Phase 1: Connection Pooling (HIGH PRIORITY)

#### Option A: aiomysql with FastAPI AsyncIO (RECOMMENDED)
**Benefits**:
- Native async/await support in FastAPI
- Connection pooling built-in
- Non-blocking I/O (better concurrency)
- Future-proof architecture

**Implementation**:
```python
# New database_async.py
import aiomysql
from contextlib import asynccontextmanager

# Global connection pool (created at startup)
pool = None

async def create_pool():
    global pool
    pool = await aiomysql.create_pool(
        host=settings.database_host,
        port=settings.database_port,
        user=settings.database_user,
        password=settings.database_password,
        db=settings.database_name,
        minsize=5,      # Minimum 5 connections ready
        maxsize=20,     # Maximum 20 connections
        autocommit=True,
        charset='utf8mb4'
    )

@asynccontextmanager
async def get_db():
    async with pool.acquire() as conn:
        yield conn
```

**Migration Effort**: MODERATE
- Convert all endpoints to `async def`
- Change `with get_db()` to `async with get_db()`
- Update all `cursor.execute()` to `await cursor.execute()`
- Keep existing database.py for backward compatibility during migration

**Performance Gain**: **30-50% improvement** under concurrent load

#### Option B: PyMySQL with Manual Pooling (SIMPLER)
**Benefits**:
- No async migration needed
- Simpler implementation
- Still provides connection reuse

**Implementation**:
```python
from queue import Queue
from threading import Lock

class ConnectionPool:
    def __init__(self, size=10):
        self.pool = Queue(maxsize=size)
        self.lock = Lock()
        for _ in range(size):
            conn = pymysql.connect(**config)
            self.pool.put(conn)

    @contextmanager
    def get_connection(self):
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)
```

**Migration Effort**: LOW
- Minimal code changes
- Drop-in replacement for current `get_db()`

**Performance Gain**: **20-30% improvement** under concurrent load

**RECOMMENDATION**: Start with Option B for quick wins, migrate to Option A for long-term scalability.

---

### Phase 2: Multi-Worker Deployment (MODERATE PRIORITY)

#### Current vs. Proposed
**Current**:
```bash
uvicorn main:app --host 127.0.0.1 --port 8001
```

**Proposed**:
```bash
# Option 1: Uvicorn with workers (simpler)
uvicorn main:app --host 127.0.0.1 --port 8001 --workers 4

# Option 2: Gunicorn with Uvicorn workers (production-grade)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8001
```

**Benefits**:
- 4 worker processes = handle 4 requests simultaneously
- Better CPU utilization across cores
- Automatic worker restart on failure
- Scales with available CPU cores

**Considerations**:
- Each worker needs own connection pool (4 workers × 10 connections = 40 total)
- Memory usage increases (4 × 92MB = ~368MB)
- Requires testing to find optimal worker count

**Performance Gain**: **200-400% throughput** improvement

---

### Phase 3: Application-Level Caching (LOW PRIORITY)

#### Hot Path Caching
**Candidates for caching**:
- Division/gender metadata (rarely changes)
- Conference/region lists (static)
- Popular team/athlete lookups (cache top 100)
- Snapshot metadata (immutable once created)

**Implementation Options**:

**Option 1: In-Memory (functools.lru_cache)**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_division_metadata():
    # Cached for lifetime of worker process
    pass
```

**Option 2: Redis (Shared Cache)**
```python
import redis
cache = redis.Redis(host='localhost', port=6379)

async def get_athlete(athlete_id):
    cached = cache.get(f"athlete:{athlete_id}")
    if cached:
        return json.loads(cached)
    # Query database
    cache.setex(f"athlete:{athlete_id}", 3600, json.dumps(result))
```

**Benefits**:
- Reduces database queries for hot paths
- Shared cache across workers (with Redis)
- TTL-based expiration

**Considerations**:
- Cache invalidation complexity
- Additional infrastructure (Redis server)
- Memory overhead

**Performance Gain**: **10-20% improvement** for cached queries

---

## Implementation Roadmap

### Immediate (This Session)
1. ✅ Analyze current architecture
2. ✅ Document bottlenecks
3. ⏳ Implement PyMySQL connection pooling (Option B)
4. ⏳ Test with connection pool
5. ⏳ Deploy and monitor

**Expected Impact**: 20-30% improvement, no async migration required

### Short-Term (Next Session)
1. Add multi-worker support (2-4 workers)
2. Tune connection pool size per worker
3. Load testing with concurrent users
4. Monitor database connection usage

**Expected Impact**: 200-400% throughput improvement

### Long-Term (Future)
1. Migrate to aiomysql async (Phase 1 Option A)
2. Implement Redis caching for hot paths
3. Add query performance monitoring
4. Database indexing optimization

**Expected Impact**: 50-100% additional improvement

---

## Database Connection Budget

### MySQL Server Limits
**Need to verify**:
- `max_connections` setting (typical: 151-500)
- Current `Threads_connected` count
- `Max_used_connections` peak

**Commands to check**:
```sql
SHOW VARIABLES LIKE 'max_connections';
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';
```

### Recommended Pool Sizing

**Single Worker Setup**:
- Pool size: 10-20 connections
- Safe for any MySQL configuration

**Multi-Worker Setup (4 workers)**:
- Pool per worker: 5-10 connections
- Total: 20-40 connections
- Reserve: ~50 connections for other apps
- Required: `max_connections` ≥ 100

**Formula**:
```
Total Connections = (Workers × Pool_Size) + Overhead
Overhead = Other apps + MySQL admin + Buffer

Example:
4 workers × 10 pool = 40
+ 20 (other apps) + 5 (admin) + 10 (buffer) = 75 connections
```

---

## Risk Assessment

### Low Risk
- ✅ Connection pooling (PyMySQL option)
- ✅ LRU caching for static data
- ✅ Adding 2-4 workers

### Moderate Risk
- ⚠️ Async migration (requires thorough testing)
- ⚠️ Redis integration (new infrastructure)

### High Risk
- 🔴 Excessive workers (could exhaust DB connections)
- 🔴 No connection limits (DoS risk)

---

## Monitoring Requirements

### Metrics to Track
1. **Response Time**: P50, P95, P99 latency
2. **Database Connections**: Active, peak, pool usage
3. **API Throughput**: Requests/second
4. **Error Rates**: 500 errors, timeouts
5. **Resource Usage**: Memory, CPU per worker

### Tools
- **Application**: FastAPI middleware for timing
- **Database**: MySQL slow query log
- **System**: `htop`, `ps aux | grep uvicorn`
- **Logs**: API access logs with timing

---

## Success Metrics

### Phase 1 Goals (Connection Pooling)
- ✅ Response time improvement: 20-30%
- ✅ Connection overhead reduction: 80%
- ✅ Zero connection exhaustion errors
- ✅ Memory usage stable

### Phase 2 Goals (Multi-Worker)
- ✅ Throughput increase: 3-4x
- ✅ Concurrent request handling: 4+ simultaneous
- ✅ CPU utilization: 10-15% baseline
- ✅ Worker process stability

### Phase 3 Goals (Caching)
- ✅ Cache hit rate: 60%+ for hot paths
- ✅ Database query reduction: 30-40%
- ✅ Sub-10ms response for cached queries

---

## Next Steps

**User Decision Required**:

1. **Start with Quick Wins (RECOMMENDED)**:
   - Implement PyMySQL connection pooling (1-2 hours)
   - Add 2-4 workers (30 minutes)
   - Test and deploy
   - Expected: 200-300% overall improvement

2. **Full Async Migration (FUTURE)**:
   - Migrate to aiomysql (4-6 hours)
   - Convert all endpoints to async
   - More complex but better long-term

3. **Status Quo + Monitoring**:
   - Add monitoring only
   - Track current performance
   - Optimize when actual bottleneck observed

**My Recommendation**: Option 1 (Quick Wins)
- Low risk, high reward
- No architecture changes
- Can deploy today
- Provides runway for growth

---

## Questions for User

1. **What's the current traffic?**
   - Requests per day/hour?
   - Peak concurrent users?
   - Growth expectations?

2. **Database connection budget?**
   - What's `max_connections` on MySQL?
   - How many connections do other apps use?

3. **Acceptable downtime?**
   - Connection pooling: ~5 minutes
   - Multi-worker: ~2 minutes
   - Async migration: Requires staging test

4. **Performance issues observed?**
   - Slow response times?
   - Timeout errors?
   - Database connection errors?

---

**End of Analysis**
