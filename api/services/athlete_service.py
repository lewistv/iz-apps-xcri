"""
XCRI Rankings API - Athlete Service

Business logic for querying athlete rankings from database.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any

from webapp.api.database import get_db_cursor, build_where_clause

logger = logging.getLogger(__name__)


def get_athletes(
    season_year: int,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: str = "division",
    checkpoint_date: Optional[str] = None,
    algorithm_type: str = "light",
    limit: int = 25,
    offset: int = 0,
    search: Optional[str] = None,
    min_races: Optional[int] = None,
    region: Optional[str] = None,
    conference: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get athlete rankings with filters and pagination.

    Args:
        season_year: Season year (required)
        division: Division code (optional, e.g., 2030 for D1)
        gender: Gender code M/F (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Rankings as of date (optional, None = full season)
        algorithm_type: Algorithm type (default: 'light')
        limit: Results per page (default: 25)
        offset: Pagination offset (default: 0)
        search: Search by athlete/school name (optional)
        min_races: Minimum race count filter (optional)
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

        # Add table alias prefix for JOIN query (Session 009D)
        where_sql = where_sql.replace('season_year =', 'a.season_year =') \
                           .replace('scoring_group =', 'a.scoring_group =') \
                           .replace('algorithm_type =', 'a.algorithm_type =') \
                           .replace('checkpoint_date =', 'a.checkpoint_date =') \
                           .replace('checkpoint_date IS', 'a.checkpoint_date IS') \
                           .replace('division_code =', 'a.division_code =') \
                           .replace('gender_code =', 'a.gender_code =')

        # Add optional filters (with table alias for JOIN - Session 009D)
        where_clauses = [where_sql]

        if search:
            where_clauses.append(
                "(a.athlete_name_first LIKE %s OR a.athlete_name_last LIKE %s OR a.team_name LIKE %s)"
            )
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        if min_races is not None:
            where_clauses.append("a.races_count >= %s")
            params.append(min_races)

        if region:
            where_clauses.append("t.regl_group_name = %s")
            params.append(region)

        if conference:
            where_clauses.append("t.conf_group_name = %s")
            params.append(conference)

        final_where = " AND ".join(where_clauses)

        # Get total count (use JOIN for region/conference filtering - Session 010)
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM iz_rankings_xcri_athlete_rankings a
            LEFT JOIN iz_rankings_xcri_team_rankings t
                ON a.anet_team_hnd = t.anet_team_hnd
                AND a.season_year = t.season_year
                AND a.division_code = t.division_code
                AND a.gender_code = t.gender_code
                AND COALESCE(a.checkpoint_date, '') = COALESCE(t.checkpoint_date, '')
            WHERE {final_where}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # Get results with pagination (JOIN with team rankings for region/conference - Session 009D)
        query_sql = f"""
            SELECT
                a.ranking_id,
                a.season_year,
                a.division_code,
                a.gender_code,
                a.checkpoint_date,
                a.algorithm_type,
                a.scoring_group,
                a.anet_athlete_hnd,
                a.athlete_name_first,
                a.athlete_name_last,
                a.anet_team_hnd,
                a.team_name,
                a.team_group_fk,
                a.athlete_rank,
                a.xcri_score,
                a.races_count,
                a.season_average,
                a.best_performance,
                a.most_recent_race_date,
                a.h2h_wins,
                a.h2h_losses,
                a.h2h_meetings,
                a.h2h_win_rate,
                a.min_opponent_quality,
                a.avg_opponent_quality,
                a.scs_score,
                a.scs_rank,
                a.saga_score,
                a.saga_rank,
                a.sewr_score,
                a.sewr_rank,
                a.osma_score,
                a.osma_rank,
                a.calculated_at,
                a.algorithm_version,
                a.processing_time_seconds,
                t.regl_group_name,
                t.conf_group_name
            FROM iz_rankings_xcri_athlete_rankings a
            LEFT JOIN iz_rankings_xcri_team_rankings t
                ON a.anet_team_hnd = t.anet_team_hnd
                AND a.season_year = t.season_year
                AND a.division_code = t.division_code
                AND a.gender_code = t.gender_code
                AND COALESCE(a.checkpoint_date, '') = COALESCE(t.checkpoint_date, '')
            WHERE {final_where}
            ORDER BY a.athlete_rank
            LIMIT %s OFFSET %s
        """
        cursor.execute(query_sql, params + [limit, offset])
        results = cursor.fetchall()

        logger.info(
            f"Athletes query: season={season_year}, division={division}, "
            f"gender={gender}, total={total}, returned={len(results)}"
        )

        return results, total


def get_athlete_by_id(
    athlete_hnd: int,
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: str = "division",
    checkpoint_date: Optional[str] = None,
    algorithm_type: str = "light"
) -> Optional[Dict[str, Any]]:
    """
    Get single athlete by AthleticNet athlete handle.

    If multiple records exist (e.g., different divisions), returns the most recent.

    Args:
        athlete_hnd: AthleticNet athlete handle (required)
        season_year: Season year (default: 2024)
        division: Division code (optional)
        gender: Gender code (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Rankings as of date (optional, None = full season)
        algorithm_type: Algorithm type (default: 'light')

    Returns:
        Athlete record dictionary or None if not found
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

        # Add athlete handle filter
        where_sql += " AND anet_athlete_hnd = %s"
        params.append(athlete_hnd)

        query_sql = f"""
            SELECT
                ranking_id,
                season_year,
                division_code,
                gender_code,
                checkpoint_date,
                algorithm_type,
                scoring_group,
                anet_athlete_hnd,
                athlete_name_first,
                athlete_name_last,
                anet_team_hnd,
                team_name,
                team_group_fk,
                athlete_rank,
                xcri_score,
                races_count,
                season_average,
                best_performance,
                h2h_wins,
                h2h_losses,
                h2h_meetings,
                h2h_win_rate,
                min_opponent_quality,
                avg_opponent_quality,
                scs_score,
                scs_rank,
                saga_score,
                saga_rank,
                sewr_score,
                sewr_rank,
                osma_score,
                osma_rank,
                calculated_at,
                algorithm_version,
                processing_time_seconds
            FROM iz_rankings_xcri_athlete_rankings
            WHERE {where_sql}
            ORDER BY calculated_at DESC
            LIMIT 1
        """
        cursor.execute(query_sql, params)
        result = cursor.fetchone()

        if result:
            logger.info(
                f"Athlete found: athlete_hnd={athlete_hnd}, "
                f"rank={result['athlete_rank']}, "
                f"name={result['athlete_name_first']} {result['athlete_name_last']}"
            )
        else:
            logger.warning(f"Athlete not found: athlete_hnd={athlete_hnd}")

        return result


def get_team_roster(
    team_hnd: int,
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    scoring_group: str = "division",
    checkpoint_date: Optional[str] = None,
    algorithm_type: str = "light",
    limit: int = 100
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get all athletes on a team roster.

    Args:
        team_hnd: AthleticNet team handle (required)
        season_year: Season year (default: 2024)
        division: Division code (optional)
        gender: Gender code (optional)
        scoring_group: Scoring scope (default: 'division')
        checkpoint_date: Rankings as of date (optional)
        algorithm_type: Algorithm type (default: 'light')
        limit: Maximum athletes to return (default: 100)

    Returns:
        Tuple of (results: List[Dict], total_count: int)
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

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM iz_rankings_xcri_athlete_rankings
            WHERE {where_sql}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # Get results ordered by rank
        query_sql = f"""
            SELECT
                ranking_id,
                season_year,
                division_code,
                gender_code,
                checkpoint_date,
                algorithm_type,
                scoring_group,
                anet_athlete_hnd,
                athlete_name_first,
                athlete_name_last,
                anet_team_hnd,
                team_name,
                team_group_fk,
                athlete_rank,
                xcri_score,
                races_count,
                season_average,
                best_performance,
                h2h_wins,
                h2h_losses,
                h2h_meetings,
                h2h_win_rate,
                min_opponent_quality,
                avg_opponent_quality,
                scs_score,
                scs_rank,
                saga_score,
                saga_rank,
                sewr_score,
                sewr_rank,
                osma_score,
                osma_rank,
                calculated_at,
                algorithm_version,
                processing_time_seconds
            FROM iz_rankings_xcri_athlete_rankings
            WHERE {where_sql}
            ORDER BY athlete_rank
            LIMIT %s
        """
        cursor.execute(query_sql, params + [limit])
        results = cursor.fetchall()

        logger.info(
            f"Team roster query: team_hnd={team_hnd}, season={season_year}, "
            f"total={total}, returned={len(results)}"
        )

        return results, total
