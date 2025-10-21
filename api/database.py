"""
XCRI Rankings API - Database Connection Management

Standalone database module for XCRI API using PyMySQL.
"""

import logging
from contextlib import contextmanager
from typing import Dict, Any, Tuple, Optional, List

import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


# ===================================================================
# Database Configuration
# ===================================================================

class DatabaseConfig:
    """Database configuration from Pydantic settings"""

    def __init__(self, settings=None):
        # Import here to avoid circular dependency
        if settings is None:
            from config import settings as app_settings
            settings = app_settings

        self.host = settings.database_host
        self.port = settings.database_port
        self.database = settings.database_name
        self.user = settings.database_user
        self.password = settings.database_password
        self.charset = getattr(settings, 'database_charset', 'utf8mb4')

        if not self.password:
            raise ValueError("DATABASE_PASSWORD is required in settings")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for pymysql.connect()"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'charset': self.charset,
            'cursorclass': DictCursor,
            'autocommit': True
        }


# Global database config (lazily initialized on first use)
db_config = None


# ===================================================================
# Connection Helpers
# ===================================================================

@contextmanager
def get_db():
    """
    Context manager for database connections.

    Usage:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()

    Yields:
        pymysql.Connection
    """
    global db_config
    if db_config is None:
        db_config = DatabaseConfig()

    conn = None
    try:
        conn = pymysql.connect(**db_config.to_dict())
        yield conn
    except pymysql.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor (simplified).

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()

    Yields:
        pymysql.cursors.DictCursor
    """
    with get_db() as conn:
        cursor = None
        try:
            cursor = conn.cursor()
            yield cursor
        except pymysql.Error as e:
            logger.error(f"Database query error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


# ===================================================================
# Helper Functions
# ===================================================================

def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            logger.info("✓ Database connection test passed")
            return True
    except pymysql.Error as e:
        logger.error(f"✗ Database connection test failed: {e}")
        return False

    return False


def get_table_counts() -> Dict[str, int]:
    """
    Get record counts from XCRI ranking tables.

    Returns:
        Dictionary with table names and record counts
    """
    with get_db_cursor() as cursor:
        counts = {}

        tables = [
            'iz_rankings_xcri_athlete_rankings',
            'iz_rankings_xcri_team_rankings',
            'iz_rankings_xcri_scs_components'
        ]

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                result = cursor.fetchone()
                counts[table] = result['cnt'] if result else 0
            except pymysql.Error as e:
                logger.warning(f"Could not count {table}: {e}")
                counts[table] = 0

        return counts


# ===================================================================
# Query Builder Helper
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

    Args:
        season_year: Season year (required)
        division: Division code (optional)
        gender: Gender code M/F (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Checkpoint date or None for full season (optional)
        algorithm_type: Algorithm type (default: 'light')

    Returns:
        Tuple of (where_sql, params)
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

def validate_database_connection():
    """
    Validate database connection on application startup.

    Raises:
        Exception: If connection fails or tables don't exist
    """
    logger.info("Validating database connection...")

    # Test connection
    if not test_connection():
        raise Exception("Database connection failed")

    # Check table counts
    try:
        counts = get_table_counts()
        logger.info("Database validation successful:")
        for table, count in counts.items():
            logger.info(f"  - {table}: {count:,} records")

        if counts.get('iz_rankings_xcri_athlete_rankings', 0) == 0:
            logger.warning("WARNING: No athlete rankings found in database")

    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        raise Exception(f"Database tables not found or inaccessible: {e}")
