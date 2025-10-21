"""
XCRI Rankings API - Team Service

Business logic for querying team rankings from database.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any

from database import get_db_cursor, build_where_clause

logger = logging.getLogger(__name__)


def get_teams(
    season_year: int,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: str = "division",
    checkpoint_date: Optional[str] = None,
    algorithm_type: str = "light",
    limit: int = 25,
    offset: int = 0,
    search: Optional[str] = None,
    region: Optional[str] = None,
    conference: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get team rankings with filters and pagination.

    Args:
        season_year: Season year (required)
        division: Division code (optional, e.g., 2030 for D1)
        gender: Gender code M/F (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Rankings as of date (optional, None = full season)
        algorithm_type: Algorithm type (default: 'light')
        limit: Results per page (default: 25)
        offset: Pagination offset (default: 0)
        search: Search by school name (optional)
        region: Filter by region name (optional)
        conference: Filter by conference name (optional)

    Returns:
        Tuple of (results: List[Dict], total_count: int)
    """
    with get_db_cursor() as cursor:
        # Build base WHERE clause
        where_sql, params = build_where_clause(
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type
        )

        # Add optional search filter
        where_clauses = [where_sql]

        if search:
            where_clauses.append("team_name LIKE %s")
            search_term = f"%{search}%"
            params.append(search_term)

        if region:
            where_clauses.append("regl_group_name = %s")
            params.append(region)

        if conference:
            where_clauses.append("conf_group_name = %s")
            params.append(conference)

        final_where = " AND ".join(where_clauses)

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM iz_rankings_xcri_team_rankings
            WHERE {final_where}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # Get results with pagination
        query_sql = f"""
            SELECT
                ranking_id,
                season_year,
                division_code,
                gender_code,
                checkpoint_date,
                algorithm_type,
                scoring_group,
                anet_team_hnd,
                team_name,
                team_group_fk,
                regl_group_name,
                conf_group_name,
                team_rank,
                team_xcri_score,
                most_recent_race_date,
                athletes_count,
                top7_average,
                top5_average,
                squad_depth_score,
                top_athlete_1_hnd,
                top_athlete_2_hnd,
                top_athlete_3_hnd,
                top_athlete_4_hnd,
                top_athlete_5_hnd,
                top_athlete_6_hnd,
                top_athlete_7_hnd,
                calculated_at,
                algorithm_version
            FROM iz_rankings_xcri_team_rankings
            WHERE {final_where}
            ORDER BY team_rank
            LIMIT %s OFFSET %s
        """
        cursor.execute(query_sql, params + [limit, offset])
        results = cursor.fetchall()

        logger.info(
            f"Teams query: season={season_year}, division={division}, "
            f"gender={gender}, total={total}, returned={len(results)}"
        )

        return results, total


def get_team_by_id(
    team_hnd: int,
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: str = "division",
    checkpoint_date: Optional[str] = None,
    algorithm_type: str = "light"
) -> Optional[Dict[str, Any]]:
    """
    Get single team by AthleticNet team handle.

    If multiple records exist (e.g., different divisions), returns the most recent.

    Args:
        team_hnd: AthleticNet team handle (required)
        season_year: Season year (default: 2024)
        division: Division code (optional)
        gender: Gender code (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Rankings as of date (optional, None = full season)
        algorithm_type: Algorithm type (default: 'light')

    Returns:
        Team record dictionary or None if not found
    """
    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_sql, params = build_where_clause(
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type
        )

        # Add team handle filter
        where_sql += " AND anet_team_hnd = %s"
        params.append(team_hnd)

        query_sql = f"""
            SELECT
                ranking_id,
                season_year,
                division_code,
                gender_code,
                checkpoint_date,
                algorithm_type,
                scoring_group,
                anet_team_hnd,
                team_name,
                team_group_fk,
                regl_group_name,
                conf_group_name,
                team_rank,
                team_xcri_score,
                most_recent_race_date,
                athletes_count,
                top7_average,
                top5_average,
                squad_depth_score,
                top_athlete_1_hnd,
                top_athlete_2_hnd,
                top_athlete_3_hnd,
                top_athlete_4_hnd,
                top_athlete_5_hnd,
                top_athlete_6_hnd,
                top_athlete_7_hnd,
                calculated_at,
                algorithm_version
            FROM iz_rankings_xcri_team_rankings
            WHERE {where_sql}
            ORDER BY calculated_at DESC
            LIMIT 1
        """
        cursor.execute(query_sql, params)
        result = cursor.fetchone()

        if result:
            logger.info(
                f"Team found: team_hnd={team_hnd}, "
                f"rank={result['team_rank']}, "
                f"name={result['team_name']}"
            )
        else:
            logger.warning(f"Team not found: team_hnd={team_hnd}")

        return result
