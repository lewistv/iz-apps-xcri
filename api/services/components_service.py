"""
XCRI Rankings API - Components Service

Business logic for querying SCS component scores (SAGA, SEWR, OSMA, XCRI) from database.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any

from database import get_db_cursor, build_where_clause

logger = logging.getLogger(__name__)


def get_athlete_components(
    athlete_hnd: int,
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get component score breakdown for a specific athlete.

    Returns SAGA, SEWR, OSMA, and XCRI scores with ranks and additional metrics
    like AGS (Adjusted Gap Score), CPR (Contest Performance Rating), and race quality.

    Args:
        athlete_hnd: AthleticNet athlete handle (required)
        season_year: Season year (default: 2024)
        division: Division code (optional)
        gender: Gender code M/F (optional)

    Returns:
        Component breakdown dictionary or None if not found
    """
    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = ["season_year = %s", "anet_athlete_hnd = %s"]
        params = [season_year, athlete_hnd]

        if division:
            where_clauses.append("division_code = %s")
            params.append(division)

        if gender:
            where_clauses.append("gender_code = %s")
            params.append(gender)

        where_sql = " AND ".join(where_clauses)

        query_sql = f"""
            SELECT
                component_id,
                ranking_id,
                season_year,
                division_code,
                gender_code,
                anet_athlete_hnd,
                athlete_name_first,
                athlete_name_last,
                team_name,
                saga_score,
                saga_rank,
                sewr_score,
                sewr_rank,
                osma_score,
                osma_rank,
                xcri_score,
                xcri_rank,
                races_used,
                best_ags,
                avg_ags,
                worst_ags,
                best_cpr,
                avg_cpr,
                worst_cpr,
                avg_race_quality,
                best_race_quality,
                avg_opponent_count,
                total_opponents,
                created_at,
                updated_at
            FROM iz_rankings_xcri_scs_components
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT 1
        """
        cursor.execute(query_sql, params)
        result = cursor.fetchone()

        if result:
            logger.info(
                f"Components found: athlete_hnd={athlete_hnd}, "
                f"SAGA={result['saga_score']}, SEWR={result['sewr_score']}, "
                f"OSMA={result['osma_score']}, XCRI={result['xcri_score']}"
            )
        else:
            logger.warning(f"Components not found: athlete_hnd={athlete_hnd}")

        return result


def get_component_leaderboard(
    component: str,
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None,
    limit: int = 25,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get top athletes by a specific component score.

    Args:
        component: Component name ('saga', 'sewr', 'osma', or 'xcri')
        season_year: Season year (default: 2024)
        division: Division code (optional)
        gender: Gender code M/F (optional)
        limit: Results per page (default: 25)
        offset: Pagination offset (default: 0)

    Returns:
        Tuple of (results: List[Dict], total_count: int)

    Raises:
        ValueError: If component name is invalid
    """
    # Validate component name
    valid_components = {'saga', 'sewr', 'osma', 'xcri'}
    if component.lower() not in valid_components:
        raise ValueError(
            f"Invalid component '{component}'. "
            f"Must be one of: {', '.join(valid_components)}"
        )

    component_lower = component.lower()
    score_col = f"{component_lower}_score"
    rank_col = f"{component_lower}_rank"

    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = ["season_year = %s"]
        params = [season_year]

        if division:
            where_clauses.append("division_code = %s")
            params.append(division)

        if gender:
            where_clauses.append("gender_code = %s")
            params.append(gender)

        # Filter out NULL scores for this component
        where_clauses.append(f"{score_col} IS NOT NULL")

        where_sql = " AND ".join(where_clauses)

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM iz_rankings_xcri_scs_components
            WHERE {where_sql}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # Get results with pagination
        # Order by rank (ascending) for most components, but SAGA is lower-is-better
        order_direction = "ASC"

        query_sql = f"""
            SELECT
                component_id,
                ranking_id,
                season_year,
                division_code,
                gender_code,
                anet_athlete_hnd,
                athlete_name_first,
                athlete_name_last,
                team_name,
                {score_col} as score,
                {rank_col} as rank,
                saga_score,
                saga_rank,
                sewr_score,
                sewr_rank,
                osma_score,
                osma_rank,
                xcri_score,
                xcri_rank,
                races_used
            FROM iz_rankings_xcri_scs_components
            WHERE {where_sql}
            ORDER BY {rank_col} {order_direction}
            LIMIT %s OFFSET %s
        """
        cursor.execute(query_sql, params + [limit, offset])
        results = cursor.fetchall()

        logger.info(
            f"Component leaderboard query: component={component}, "
            f"season={season_year}, division={division}, gender={gender}, "
            f"total={total}, returned={len(results)}"
        )

        return results, total


def get_all_components_for_athletes(
    athlete_hnds: List[int],
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Batch fetch component scores for multiple athletes.

    This is useful for enriching athlete rankings with component data.

    Args:
        athlete_hnds: List of AthleticNet athlete handles
        season_year: Season year (default: 2024)
        division: Division code (optional)
        gender: Gender code (optional)

    Returns:
        Dictionary mapping athlete_hnd -> component data
    """
    if not athlete_hnds:
        return {}

    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = ["season_year = %s"]
        params = [season_year]

        if division:
            where_clauses.append("division_code = %s")
            params.append(division)

        if gender:
            where_clauses.append("gender_code = %s")
            params.append(gender)

        # Add athlete handles filter with IN clause
        placeholders = ",".join(["%s"] * len(athlete_hnds))
        where_clauses.append(f"anet_athlete_hnd IN ({placeholders})")
        params.extend(athlete_hnds)

        where_sql = " AND ".join(where_clauses)

        query_sql = f"""
            SELECT
                anet_athlete_hnd,
                saga_score,
                saga_rank,
                sewr_score,
                sewr_rank,
                osma_score,
                osma_rank,
                xcri_score,
                xcri_rank,
                races_used,
                best_ags,
                avg_ags,
                worst_ags
            FROM iz_rankings_xcri_scs_components
            WHERE {where_sql}
        """
        cursor.execute(query_sql, params)
        results = cursor.fetchall()

        # Convert to dictionary keyed by athlete_hnd
        components_by_athlete = {
            row['anet_athlete_hnd']: row
            for row in results
        }

        logger.info(
            f"Batch components fetch: requested={len(athlete_hnds)}, "
            f"found={len(components_by_athlete)}"
        )

        return components_by_athlete
