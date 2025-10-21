"""
XCRI Rankings API - Database Connection Management

Wraps the existing database_connection module from algorithms/shared/
and provides connection helpers for FastAPI routes.
"""

import sys
import logging
from pathlib import Path
from contextlib import contextmanager

# Add parent directory to Python path to import from algorithms/
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from algorithms.shared.database_connection import (
    DatabaseConfig,
    get_db_connection,
    test_connection
)
from webapp.api.config import settings, get_database_config_path

logger = logging.getLogger(__name__)


# ===================================================================
# Database Configuration Initialization
# ===================================================================

def initialize_db_config() -> DatabaseConfig:
    """
    Initialize database configuration from settings.

    Tries in order:
    1. Config file (if XCRI_DB_CONFIG_PATH is set)
    2. Environment variables (if credentials provided)

    Returns:
        DatabaseConfig instance

    Raises:
        ValueError: If configuration is insufficient
    """
    # Try config file first
    config_path = get_database_config_path()
    if config_path:
        logger.info(f"Loading database config from file: {config_path}")
        return DatabaseConfig.from_config_file(config_path)

    # Try environment variables
    if settings.xcri_db_user and settings.xcri_db_password:
        logger.info("Loading database config from environment variables")
        return DatabaseConfig(
            host=settings.xcri_db_host,
            port=settings.xcri_db_port,
            user=settings.xcri_db_user,
            password=settings.xcri_db_password,
            database=settings.xcri_db_name,
            charset=settings.xcri_db_charset
        )

    raise ValueError(
        "Database configuration not found. Please provide either:\n"
        "1. XCRI_DB_CONFIG_PATH pointing to a .ini/.cnf file, or\n"
        "2. Individual credentials: XCRI_DB_USER, XCRI_DB_PASSWORD"
    )


# Global database config instance
db_config = initialize_db_config()


# ===================================================================
# Connection Helpers for FastAPI
# ===================================================================

@contextmanager
def get_db():
    """
    Context manager for database connections in FastAPI routes.

    Usage:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()

    Yields:
        pymysql.Connection with DictCursor

    Raises:
        Exception: Any database connection errors
    """
    with get_db_connection(db_config) as conn:
        yield conn


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor (simplified).

    Automatically commits on success, rolls back on error.

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()

    Yields:
        pymysql.cursors.DictCursor

    Raises:
        Exception: Any database errors
    """
    with get_db_connection(db_config) as conn:
        try:
            with conn.cursor() as cursor:
                yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise


def test_db_connection() -> bool:
    """
    Test database connection and log result.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        result = test_connection(db_config, verbose=True)
        if result:
            logger.info("✓ Database connection test passed")
        else:
            logger.error("✗ Database connection test failed")
        return result
    except Exception as e:
        logger.error(f"✗ Database connection test error: {e}")
        return False


def get_table_counts() -> dict:
    """
    Get record counts from XCRI ranking tables.

    Returns:
        Dictionary with table names and record counts

    Raises:
        Exception: If database query fails
    """
    with get_db_cursor() as cursor:
        # Get athlete rankings count
        cursor.execute("SELECT COUNT(*) as cnt FROM iz_rankings_xcri_athlete_rankings")
        athlete_count = cursor.fetchone()['cnt']

        # Get team rankings count
        cursor.execute("SELECT COUNT(*) as cnt FROM iz_rankings_xcri_team_rankings")
        team_count = cursor.fetchone()['cnt']

        # Get metadata count
        cursor.execute("SELECT COUNT(*) as cnt FROM iz_rankings_xcri_calculation_metadata")
        metadata_count = cursor.fetchone()['cnt']

        return {
            "athlete_rankings": athlete_count,
            "team_rankings": team_count,
            "calculation_metadata": metadata_count
        }


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
    if not test_db_connection():
        raise Exception("Database connection failed")

    # Check table counts
    try:
        counts = get_table_counts()
        logger.info(f"Database validation successful:")
        logger.info(f"  - Athlete rankings: {counts['athlete_rankings']:,} records")
        logger.info(f"  - Team rankings: {counts['team_rankings']:,} records")
        logger.info(f"  - Metadata: {counts['calculation_metadata']} records")

        if counts['athlete_rankings'] == 0:
            logger.warning("WARNING: No athlete rankings found in database")

    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        raise Exception(f"Database tables not found or inaccessible: {e}")


# ===================================================================
# Helper Functions for Common Queries
# ===================================================================

def build_where_clause(
    season_year: int,
    division: int = None,
    gender: str = None,
    scoring_group: str = "division",
    checkpoint_date: str = None,
    algorithm_type: str = "light"
) -> tuple:
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
