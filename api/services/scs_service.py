"""
XCRI Rankings API - SCS Component Service

Business logic for querying SCS component breakdowns from database.
"""

import logging
from typing import Optional, Dict, Any

from webapp.api.database import get_db_cursor

logger = logging.getLogger(__name__)


def get_athlete_scs_components(
    athlete_hnd: int,
    season_year: int = 2024,
    division: Optional[int] = None,
    gender: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get detailed SCS component breakdown for a specific athlete.

    Args:
        athlete_hnd: AthleticNet athlete handle (required)
        season_year: Season year (default: 2024)
        division: Division code (optional, e.g., 2030 for D1)
        gender: Gender code M/F (optional)

    Returns:
        Dict with component scores and ranks, or None if not found
    """
    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = [
            "season_year = %s",
            "anet_athlete_hnd = %s"
        ]
        params = [season_year, athlete_hnd]

        if division is not None:
            where_clauses.append("division_code = %s")
            params.append(division)

        if gender is not None:
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

                -- Component scores and ranks
                saga_score,
                saga_rank,
                sewr_score,
                sewr_rank,
                osma_score,
                osma_rank,
                xcri_score,
                xcri_rank,

                -- Supporting metrics
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
                f"SCS components found: athlete_hnd={athlete_hnd}, "
                f"SAGA rank={result['saga_rank']}, SEWR rank={result['sewr_rank']}, "
                f"OSMA rank={result['osma_rank']}, SCS rank={result['xcri_rank']}"
            )
        else:
            logger.warning(f"SCS components not found: athlete_hnd={athlete_hnd}")

        return result


def get_component_leaderboard(
    component: str,
    season_year: int = 2024,
    division: int = 2030,
    gender: str = 'M',
    limit: int = 25
) -> tuple[list[Dict[str, Any]], int]:
    """
    Get top athletes ranked by a specific SCS component.

    Args:
        component: Component name ('saga', 'sewr', 'osma', or 'xcri')
        season_year: Season year (default: 2024)
        division: Division code (default: 2030 for D1)
        gender: Gender code (default: 'M')
        limit: Number of results (default: 25)

    Returns:
        Tuple of (results: List[Dict], total_count: int)
    """
    # Validate component parameter
    valid_components = {'saga', 'sewr', 'osma', 'xcri'}
    if component.lower() not in valid_components:
        raise ValueError(f"Invalid component: {component}. Must be one of {valid_components}")

    component = component.lower()
    score_col = f"{component}_score"
    rank_col = f"{component}_rank"

    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_sql = """
            season_year = %s
            AND division_code = %s
            AND gender_code = %s
        """
        params = [season_year, division, gender]

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM iz_rankings_xcri_scs_components
            WHERE {where_sql}
              AND {rank_col} IS NOT NULL
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # Get results
        query_sql = f"""
            SELECT
                anet_athlete_hnd,
                athlete_name_first,
                athlete_name_last,
                team_name,
                {score_col} as component_score,
                {rank_col} as component_rank,
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
              AND {rank_col} IS NOT NULL
            ORDER BY {rank_col}
            LIMIT %s
        """
        cursor.execute(query_sql, params + [limit])
        results = cursor.fetchall()

        logger.info(
            f"Component leaderboard query: {component.upper()}, "
            f"season={season_year}, division={division}, gender={gender}, "
            f"total={total}, returned={len(results)}"
        )

        return results, total


def get_component_comparison(
    athlete_hnd: int,
    season_year: int = 2024,
    division: int = 2030,
    gender: str = 'M'
) -> Optional[Dict[str, Any]]:
    """
    Get athlete's SCS components with division context (percentiles, etc.).

    Args:
        athlete_hnd: AthleticNet athlete handle
        season_year: Season year
        division: Division code
        gender: Gender code

    Returns:
        Dict with component scores, ranks, and context
    """
    with get_db_cursor() as cursor:
        # Get athlete's component data
        athlete_sql = """
            SELECT
                anet_athlete_hnd,
                athlete_name_first,
                athlete_name_last,
                team_name,
                saga_score, saga_rank,
                sewr_score, sewr_rank,
                osma_score, osma_rank,
                xcri_score, xcri_rank,
                races_used,
                best_ags, avg_ags, worst_ags,
                best_cpr, avg_cpr, worst_cpr,
                total_opponents
            FROM iz_rankings_xcri_scs_components
            WHERE season_year = %s
              AND division_code = %s
              AND gender_code = %s
              AND anet_athlete_hnd = %s
        """
        cursor.execute(athlete_sql, [season_year, division, gender, athlete_hnd])
        athlete_data = cursor.fetchone()

        if not athlete_data:
            return None

        # Get division totals for percentile calculation
        totals_sql = """
            SELECT COUNT(*) as total_athletes
            FROM iz_rankings_xcri_scs_components
            WHERE season_year = %s
              AND division_code = %s
              AND gender_code = %s
        """
        cursor.execute(totals_sql, [season_year, division, gender])
        totals = cursor.fetchone()
        total_athletes = totals['total_athletes']

        # Calculate percentiles
        def calc_percentile(rank, total):
            if rank is None or total == 0:
                return None
            return round((1 - (rank / total)) * 100, 1)

        result = {
            'athlete_info': {
                'athlete_hnd': athlete_data['anet_athlete_hnd'],
                'name': f"{athlete_data['athlete_name_first']} {athlete_data['athlete_name_last']}",
                'team': athlete_data['team_name'],
                'races_used': athlete_data['races_used'],
                'total_opponents': athlete_data['total_opponents']
            },
            'components': {
                'saga': {
                    'score': float(athlete_data['saga_score']) if athlete_data['saga_score'] else None,
                    'rank': athlete_data['saga_rank'],
                    'percentile': calc_percentile(athlete_data['saga_rank'], total_athletes),
                    'description': 'Season Adjusted Gap Average'
                },
                'sewr': {
                    'score': float(athlete_data['sewr_score']) if athlete_data['sewr_score'] else None,
                    'rank': athlete_data['sewr_rank'],
                    'percentile': calc_percentile(athlete_data['sewr_rank'], total_athletes),
                    'description': 'Season Equal-Weight Rating (own performance)'
                },
                'osma': {
                    'score': float(athlete_data['osma_score']) if athlete_data['osma_score'] else None,
                    'rank': athlete_data['osma_rank'],
                    'percentile': calc_percentile(athlete_data['osma_rank'], total_athletes),
                    'description': 'Opponent Strength of Schedule'
                },
                'xcri': {
                    'score': float(athlete_data['xcri_score']) if athlete_data['xcri_score'] else None,
                    'rank': athlete_data['xcri_rank'],
                    'percentile': calc_percentile(athlete_data['xcri_rank'], total_athletes),
                    'description': 'Final SCS = (0.6 × SEWR) + (0.4 × OSMA)'
                }
            },
            'detail_metrics': {
                'ags': {
                    'best': float(athlete_data['best_ags']) if athlete_data['best_ags'] else None,
                    'average': float(athlete_data['avg_ags']) if athlete_data['avg_ags'] else None,
                    'worst': float(athlete_data['worst_ags']) if athlete_data['worst_ags'] else None
                },
                'cpr': {
                    'best': float(athlete_data['best_cpr']) if athlete_data['best_cpr'] else None,
                    'average': float(athlete_data['avg_cpr']) if athlete_data['avg_cpr'] else None,
                    'worst': float(athlete_data['worst_cpr']) if athlete_data['worst_cpr'] else None
                }
            },
            'context': {
                'total_athletes': total_athletes,
                'season_year': season_year,
                'division_code': division,
                'gender_code': gender
            }
        }

        logger.info(
            f"Component comparison: athlete_hnd={athlete_hnd}, "
            f"SAGA %tile={result['components']['saga']['percentile']}, "
            f"SEWR %tile={result['components']['sewr']['percentile']}"
        )

        return result


def get_component_distribution(
    component: str,
    season_year: int = 2024,
    division: int = 2030,
    gender: str = 'M',
    bins: int = 10
) -> Dict[str, Any]:
    """
    Get distribution statistics for a specific component.

    Args:
        component: Component name ('saga', 'sewr', 'osma', or 'xcri')
        season_year: Season year
        division: Division code
        gender: Gender code
        bins: Number of bins for histogram (default: 10)

    Returns:
        Dict with min, max, mean, median, std, histogram
    """
    # Validate component
    valid_components = {'saga', 'sewr', 'osma', 'xcri'}
    if component.lower() not in valid_components:
        raise ValueError(f"Invalid component: {component}")

    component = component.lower()
    score_col = f"{component}_score"

    with get_db_cursor() as cursor:
        # Get distribution statistics
        stats_sql = f"""
            SELECT
                MIN({score_col}) as min_score,
                MAX({score_col}) as max_score,
                AVG({score_col}) as mean_score,
                STDDEV({score_col}) as std_score,
                COUNT(*) as total_count
            FROM iz_rankings_xcri_scs_components
            WHERE season_year = %s
              AND division_code = %s
              AND gender_code = %s
              AND {score_col} IS NOT NULL
        """
        cursor.execute(stats_sql, [season_year, division, gender])
        stats = cursor.fetchone()

        # Get percentiles (25th, 50th, 75th)
        # Note: MySQL doesn't have built-in PERCENTILE function, so we approximate
        percentile_sql = f"""
            SELECT {score_col}
            FROM iz_rankings_xcri_scs_components
            WHERE season_year = %s
              AND division_code = %s
              AND gender_code = %s
              AND {score_col} IS NOT NULL
            ORDER BY {score_col}
        """
        cursor.execute(percentile_sql, [season_year, division, gender])
        all_scores = [row[score_col] for row in cursor.fetchall()]

        def get_percentile(scores, p):
            if not scores:
                return None
            index = int(len(scores) * p / 100)
            return float(scores[index])

        result = {
            'component': component.upper(),
            'statistics': {
                'min': float(stats['min_score']) if stats['min_score'] else None,
                'max': float(stats['max_score']) if stats['max_score'] else None,
                'mean': float(stats['mean_score']) if stats['mean_score'] else None,
                'std': float(stats['std_score']) if stats['std_score'] else None,
                'count': stats['total_count']
            },
            'percentiles': {
                '25th': get_percentile(all_scores, 25),
                '50th': get_percentile(all_scores, 50),  # median
                '75th': get_percentile(all_scores, 75)
            },
            'context': {
                'season_year': season_year,
                'division_code': division,
                'gender_code': gender
            }
        }

        logger.info(
            f"Component distribution: {component.upper()}, "
            f"mean={result['statistics']['mean']:.2f}, "
            f"std={result['statistics']['std']:.2f}"
        )

        return result
