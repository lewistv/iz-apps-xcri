"""
XCRI Rankings API - Async Database Connection Management with Pooling

This module provides async database operations using aiomysql with connection pooling
for improved performance and scalability. Designed for multi-worker uvicorn deployment.

Key Features:
- Connection pooling (5-10 connections per worker)
- Async/await support for non-blocking I/O
- Automatic connection recycling
- Graceful startup/shutdown lifecycle management

Usage:
    # In lifespan:
    await create_pool(config, pool_size=10)

    # In async functions:
    async with get_db_cursor() as cursor:
        await cursor.execute("SELECT * FROM table")
        results = await cursor.fetchall()

    # At shutdown:
    await close_pool()
"""

import logging
import aiomysql
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

# Global connection pool (initialized at app startup)
pool: Optional[aiomysql.Pool] = None


# ===================================================================
# Connection Pool Management
# ===================================================================

async def create_pool(config: Dict[str, Any], pool_size: int = 10) -> None:
    """
    Create async MySQL connection pool at application startup.

    Args:
        config: Database configuration dictionary with keys:
            - host: MySQL server host
            - port: MySQL server port
            - user: Database username
            - password: Database password
            - database: Database name
        pool_size: Number of connections in pool (default: 10 per worker)

    Raises:
        Exception: If pool creation fails
    """
    global pool

    try:
        logger.info(f"Creating async connection pool (size: {pool_size})...")

        pool = await aiomysql.create_pool(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            db=config['database'],
            minsize=5,              # Keep 5 connections ready
            maxsize=pool_size,      # Maximum connections per worker
            autocommit=True,        # Auto-commit for read operations
            charset='utf8mb4',
            connect_timeout=5,      # 5 second connection timeout
            pool_recycle=3600,      # Recycle connections after 1 hour
            echo=False,             # Disable SQL echo (can enable for debugging)
        )

        logger.info(f"✓ Async connection pool initialized successfully")
        logger.info(f"  - Pool size: {pool_size} connections")
        logger.info(f"  - Min ready: 5 connections")
        logger.info(f"  - Recycle: 3600 seconds (1 hour)")

    except Exception as e:
        logger.error(f"✗ Failed to create connection pool: {e}")
        raise Exception(f"Database pool initialization failed: {e}")


async def close_pool() -> None:
    """
    Close connection pool at application shutdown.

    Gracefully closes all connections in the pool.
    """
    global pool

    if pool:
        logger.info("Closing async connection pool...")
        pool.close()
        await pool.wait_closed()
        logger.info("✓ Connection pool closed successfully")
    else:
        logger.warning("No connection pool to close")


def get_pool_status() -> Dict[str, Any]:
    """
    Get current pool status for monitoring.

    Returns:
        Dictionary with pool statistics
    """
    if not pool:
        return {"status": "not_initialized"}

    return {
        "status": "active",
        "size": pool.size,
        "free": pool.freesize,
        "min_size": pool.minsize,
        "max_size": pool.maxsize,
    }


# ===================================================================
# Connection Context Managers
# ===================================================================

@asynccontextmanager
async def get_db():
    """
    Async context manager for database connections from pool.

    Acquires a connection from the pool and yields it for use.
    Connection is automatically returned to pool after use.

    Usage:
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM table")
                results = await cursor.fetchall()

    Yields:
        aiomysql.Connection: Database connection from pool

    Raises:
        RuntimeError: If pool not initialized
    """
    if not pool:
        raise RuntimeError(
            "Connection pool not initialized. "
            "Call create_pool() in application startup."
        )

    async with pool.acquire() as conn:
        yield conn


@asynccontextmanager
async def get_db_cursor(cursor_class=aiomysql.DictCursor):
    """
    Async context manager for database cursor (simplified).

    Automatically handles connection acquisition and cursor creation.
    Cursor is automatically closed after use, connection returned to pool.

    Args:
        cursor_class: Cursor class to use (default: DictCursor for dict results)

    Usage:
        async with get_db_cursor() as cursor:
            await cursor.execute("SELECT * FROM table")
            results = await cursor.fetchall()

    Yields:
        aiomysql.Cursor: Database cursor (DictCursor by default)

    Raises:
        RuntimeError: If pool not initialized
    """
    async with get_db() as conn:
        async with conn.cursor(cursor_class) as cursor:
            yield cursor


# ===================================================================
# Helper Functions
# ===================================================================

async def test_connection() -> bool:
    """
    Test database connection from pool.

    Returns:
        True if connection test passed, False otherwise
    """
    try:
        async with get_db_cursor() as cursor:
            await cursor.execute("SELECT 1 as test")
            result = await cursor.fetchone()

            if result and result.get('test') == 1:
                logger.info("✓ Database connection test passed")
                return True
            else:
                logger.error("✗ Database connection test failed: unexpected result")
                return False

    except Exception as e:
        logger.error(f"✗ Database connection test failed: {e}")
        return False


async def get_table_counts() -> Dict[str, int]:
    """
    Get record counts from XCRI ranking tables.

    Returns:
        Dictionary with table names and record counts
    """
    async with get_db_cursor() as cursor:
        counts = {}

        tables = [
            'iz_rankings_xcri_athlete_rankings',
            'iz_rankings_xcri_team_rankings',
            'iz_rankings_xcri_scs_components',
            'iz_rankings_xcri_calculation_metadata'
        ]

        for table in tables:
            try:
                await cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                result = await cursor.fetchone()
                counts[table] = result['cnt'] if result else 0
            except Exception as e:
                logger.warning(f"Could not count {table}: {e}")
                counts[table] = 0

        return counts


# ===================================================================
# Query Builder Helper (from original database.py)
# ===================================================================

def build_where_clause(
    season_year: int,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: str = "division",
    checkpoint_date: Optional[str] = None,
    algorithm_type: str = "light"
) -> Tuple[str, List[Any]]:
    """
    Build WHERE clause for common XCRI queries.

    This is a pure function (no async needed) that constructs SQL WHERE clauses.

    Args:
        season_year: Season year (required)
        division: Division code (optional)
        gender: Gender code M/F (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Checkpoint date or None for full season (optional)
        algorithm_type: Algorithm type (default: 'light')

    Returns:
        Tuple of (where_sql, params) for parameterized queries
    """
    where_clauses = ["season_year = %s"]
    params = [season_year]

    # Always filter by scoring group
    where_clauses.append("scoring_group = %s")
    params.append(scoring_group)

    # Always filter by algorithm type
    where_clauses.append("algorithm_type = %s")
    params.append(algorithm_type)

    # Checkpoint date (NULL for full season)
    if checkpoint_date:
        where_clauses.append("checkpoint_date = %s")
        params.append(checkpoint_date)
    else:
        where_clauses.append("checkpoint_date IS NULL")

    # Optional filters
    if division:
        where_clauses.append("division_code = %s")
        params.append(division)

    if gender:
        where_clauses.append("gender_code = %s")
        params.append(gender.upper())

    where_sql = " AND ".join(where_clauses)
    return where_sql, params


# ===================================================================
# Startup Validation
# ===================================================================

async def validate_database_connection() -> None:
    """
    Validate database connection and tables on application startup.

    Raises:
        Exception: If connection fails or tables don't exist
    """
    logger.info("Validating async database connection...")

    # Test connection
    if not await test_connection():
        raise Exception("Database connection test failed")

    # Check table counts
    try:
        counts = await get_table_counts()
        logger.info("Database validation successful:")
        for table, count in counts.items():
            # Simplify table name for logging
            short_name = table.replace('iz_rankings_xcri_', '')
            logger.info(f"  - {short_name}: {count:,} records")

        # Warn if no athlete rankings
        if counts.get('iz_rankings_xcri_athlete_rankings', 0) == 0:
            logger.warning("WARNING: No athlete rankings found in database")

    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        raise Exception(f"Database tables not found or inaccessible: {e}")
