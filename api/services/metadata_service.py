"""
XCRI Rankings API - Metadata Service

Business logic for querying calculation metadata from database.
"""

import logging
from typing import Optional, List, Dict, Any

from database import get_db_cursor

logger = logging.getLogger(__name__)


def get_metadata(
    season_year: int,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: Optional[str] = None,
    checkpoint_date: Optional[str] = None,
    algorithm_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get calculation metadata records with filters.

    Args:
        season_year: Season year (required)
        division: Division code (optional)
        gender: Gender code (optional)
        scoring_group: Scoring scope (optional)
        checkpoint_date: Checkpoint date (optional)
        algorithm_type: Algorithm type (optional)

    Returns:
        List of metadata records
    """
    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = ["season_year = %s"]
        params = [season_year]

        if division is not None:
            where_clauses.append("division_code = %s")
            params.append(division)

        if gender is not None:
            where_clauses.append("gender_code = %s")
            params.append(gender.upper())

        if scoring_group is not None:
            where_clauses.append("scoring_group = %s")
            params.append(scoring_group)

        if checkpoint_date is not None:
            where_clauses.append("checkpoint_date = %s")
            params.append(checkpoint_date)
        else:
            # If not specified, default to full season (NULL checkpoint_date)
            where_clauses.append("checkpoint_date IS NULL")

        if algorithm_type is not None:
            where_clauses.append("algorithm_type = %s")
            params.append(algorithm_type)

        where_sql = " AND ".join(where_clauses)

        query_sql = f"""
            SELECT
                metadata_id,
                season_year,
                division_code,
                gender_code,
                checkpoint_date,
                algorithm_type,
                scoring_group,
                calculated_at,
                algorithm_version,
                total_performances,
                total_athletes,
                total_teams,
                total_races,
                processing_time_seconds,
                cache_used,
                cache_hit_rate,
                athletes_with_h2h,
                athletes_no_h2h,
                heavy_fallback_count,
                calculation_status,
                error_message
            FROM iz_rankings_xcri_calculation_metadata
            WHERE {where_sql}
            ORDER BY calculated_at DESC
        """
        cursor.execute(query_sql, params)
        results = cursor.fetchall()

        logger.info(
            f"Metadata query: season={season_year}, division={division}, "
            f"gender={gender}, found={len(results)} records"
        )

        return results


def get_latest_metadata() -> List[Dict[str, Any]]:
    """
    Get the most recent calculation metadata for each division/gender combination.

    Returns all 6 divisions (D1/D2/D3 x Men/Women) for the current season.

    Returns:
        List of metadata records (one per division/gender)
    """
    with get_db_cursor() as cursor:
        query_sql = """
            SELECT
                m.metadata_id,
                m.season_year,
                m.division_code,
                m.gender_code,
                m.checkpoint_date,
                m.algorithm_type,
                m.scoring_group,
                m.calculated_at,
                m.algorithm_version,
                m.total_performances,
                m.total_athletes,
                m.total_teams,
                m.total_races,
                m.processing_time_seconds,
                m.cache_used,
                m.cache_hit_rate,
                m.athletes_with_h2h,
                m.athletes_no_h2h,
                m.heavy_fallback_count,
                m.calculation_status,
                m.error_message
            FROM iz_rankings_xcri_calculation_metadata m
            INNER JOIN (
                SELECT
                    division_code,
                    gender_code,
                    MAX(calculated_at) as max_calculated_at
                FROM iz_rankings_xcri_calculation_metadata
                WHERE checkpoint_date IS NULL
                  AND algorithm_type = 'light'
                  AND scoring_group = 'division'
                GROUP BY division_code, gender_code
            ) latest
            ON m.division_code = latest.division_code
               AND m.gender_code = latest.gender_code
               AND m.calculated_at = latest.max_calculated_at
            WHERE m.checkpoint_date IS NULL
              AND m.algorithm_type = 'light'
              AND m.scoring_group = 'division'
            ORDER BY m.division_code, m.gender_code
        """
        cursor.execute(query_sql)
        results = cursor.fetchall()

        logger.info(f"Latest metadata query: found {len(results)} recent calculations")

        return results


def get_metadata_by_id(metadata_id: int) -> Optional[Dict[str, Any]]:
    """
    Get single metadata record by ID.

    Args:
        metadata_id: Metadata primary key

    Returns:
        Metadata record or None if not found
    """
    with get_db_cursor() as cursor:
        query_sql = """
            SELECT
                metadata_id,
                season_year,
                division_code,
                gender_code,
                checkpoint_date,
                algorithm_type,
                scoring_group,
                calculated_at,
                algorithm_version,
                total_performances,
                total_athletes,
                total_teams,
                total_races,
                processing_time_seconds,
                cache_used,
                cache_hit_rate,
                athletes_with_h2h,
                athletes_no_h2h,
                heavy_fallback_count,
                calculation_status,
                error_message
            FROM iz_rankings_xcri_calculation_metadata
            WHERE metadata_id = %s
        """
        cursor.execute(query_sql, [metadata_id])
        result = cursor.fetchone()

        if result:
            logger.info(f"Metadata found: id={metadata_id}")
        else:
            logger.warning(f"Metadata not found: id={metadata_id}")

        return result


def get_processing_summary() -> Dict[str, Any]:
    """
    Get aggregate processing statistics across all calculations.

    Returns summary of:
    - Total calculations
    - Average processing time
    - Average cache hit rate
    - Total athletes/teams ranked

    Returns:
        Dictionary with summary statistics
    """
    with get_db_cursor() as cursor:
        query_sql = """
            SELECT
                COUNT(*) as total_calculations,
                SUM(total_athletes) as total_athletes_all,
                SUM(total_teams) as total_teams_all,
                AVG(processing_time_seconds) as avg_processing_time,
                AVG(cache_hit_rate) as avg_cache_hit_rate,
                MIN(calculated_at) as first_calculation,
                MAX(calculated_at) as latest_calculation
            FROM iz_rankings_xcri_calculation_metadata
            WHERE checkpoint_date IS NULL
              AND algorithm_type = 'light'
              AND scoring_group = 'division'
        """
        cursor.execute(query_sql)
        result = cursor.fetchone()

        logger.info("Processing summary retrieved")

        return result or {}
