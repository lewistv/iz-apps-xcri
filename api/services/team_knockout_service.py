"""
Team Knockout API - Service Layer

Business logic for querying Team Knockout rankings and matchup data from MySQL.
Adapted from existing service patterns in iz-apps-clean/xcri/api/services/

Created: Team Knockout Session 015
"""

import logging
from typing import Optional, Tuple, List, Dict, Any
from datetime import date

from database_async import get_db_cursor

logger = logging.getLogger(__name__)


# ===================================================================
# Team Knockout Rankings Queries
# ===================================================================

async def get_team_knockout_rankings(
    season_year: int,
    rank_group_type: str = "D",
    rank_group_fk: Optional[int] = None,
    gender_code: Optional[str] = None,
    checkpoint_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get Team Knockout rankings with filters and pagination.

    Args:
        season_year: Season year (required)
        rank_group_type: Ranking group type - D/R/C (default: 'D' for Division)
        rank_group_fk: Ranking group ID (division_code, regl_group_fk, or conf_group_fk)
        gender_code: Gender code M/F (optional)
        checkpoint_date: Rankings as of date (optional, None = LIVE rankings)
        limit: Results per page (default: 100)
        offset: Pagination offset (default: 0)
        search: Search by team name (optional)

    Returns:
        Tuple of (results: List[Dict], total_count: int)
    """
    async with get_db_cursor() as cursor:
        # Build WHERE clause (use table alias 'ko' for knockout table)
        where_clauses = ["ko.season_year = %s", "ko.rank_group_type = %s"]
        params = [season_year, rank_group_type]

        if rank_group_fk is not None:
            where_clauses.append("ko.rank_group_fk = %s")
            params.append(rank_group_fk)

        if gender_code:
            where_clauses.append("ko.gender_code = %s")
            params.append(gender_code.upper())

        if checkpoint_date:
            where_clauses.append("ko.checkpoint_date = %s")
            params.append(checkpoint_date)
        else:
            where_clauses.append("ko.checkpoint_date IS NULL")

        if search:
            where_clauses.append("ko.team_name LIKE %s")
            params.append(f"%{search}%")

        where_sql = " AND ".join(where_clauses)

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM iz_rankings_xcri_team_knockout ko
            WHERE {where_sql}
        """
        await cursor.execute(count_sql, params)
        total = (await cursor.fetchone())['total']

        # Get results with pagination
        # Join with team_five table to get region/conference names
        query_sql = f"""
            SELECT
                ko.id,
                ko.team_id,
                ko.team_name,
                ko.team_code,
                ko.rank_group_type,
                ko.rank_group_fk,
                ko.gender_code,
                ko.regl_group_fk,
                ko.conf_group_fk,
                ko.regl_finish,
                ko.conf_finish,
                ko.knockout_rank,
                ko.team_five_rank,
                ko.elimination_method,
                ko.team_size,
                ko.athletes_with_xcri,
                ko.team_five_xcri_pts,
                ko.h2h_wins,
                ko.h2h_losses,
                ko.h2h_win_pct,
                ko.checkpoint_date,
                ko.season_year,
                ko.calculation_date,
                tf.regl_group_name,
                tf.conf_group_name,
                tf.most_recent_race_date
            FROM iz_rankings_xcri_team_knockout ko
            LEFT JOIN iz_rankings_xcri_team_five tf
                ON ko.team_id = tf.anet_team_hnd
                AND ko.season_year = tf.season_year
                AND ko.rank_group_fk = tf.division_code
                AND ko.gender_code = tf.gender_code
                AND COALESCE(ko.checkpoint_date, '') = COALESCE(tf.checkpoint_date, '')
            WHERE {where_sql}
            ORDER BY ko.knockout_rank
            LIMIT %s OFFSET %s
        """
        await cursor.execute(query_sql, params + [limit, offset])
        results = await cursor.fetchall()

        logger.info(
            f"Team Knockout query: season={season_year}, type={rank_group_type}, "
            f"group_fk={rank_group_fk}, gender={gender_code}, total={total}, returned={len(results)}"
        )

        return results, total


async def get_team_knockout_by_id(
    team_id: int,
    season_year: int,
    rank_group_type: str = "D",
    rank_group_fk: Optional[int] = None,
    gender_code: Optional[str] = None,
    checkpoint_date: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get single Team Knockout ranking by team ID.

    Args:
        team_id: Team identifier (anet_team_hnd)
        season_year: Season year (required)
        rank_group_type: Ranking group type - D/R/C (default: 'D')
        rank_group_fk: Ranking group ID (optional)
        gender_code: Gender code M/F (optional)
        checkpoint_date: Rankings as of date (optional, None = LIVE)

    Returns:
        Single team record or None if not found
    """
    async with get_db_cursor() as cursor:
        # Build WHERE clause (use table alias 'ko' for knockout table)
        where_clauses = [
            "ko.team_id = %s",
            "ko.season_year = %s",
            "ko.rank_group_type = %s"
        ]
        params = [team_id, season_year, rank_group_type]

        if rank_group_fk is not None:
            where_clauses.append("ko.rank_group_fk = %s")
            params.append(rank_group_fk)

        if gender_code:
            where_clauses.append("ko.gender_code = %s")
            params.append(gender_code.upper())

        if checkpoint_date:
            where_clauses.append("ko.checkpoint_date = %s")
            params.append(checkpoint_date)
        else:
            where_clauses.append("ko.checkpoint_date IS NULL")

        where_sql = " AND ".join(where_clauses)

        # Join with team_five table to get region/conference names
        query_sql = f"""
            SELECT
                ko.id, ko.team_id, ko.team_name, ko.team_code,
                ko.rank_group_type, ko.rank_group_fk, ko.gender_code,
                ko.regl_group_fk, ko.conf_group_fk, ko.regl_finish, ko.conf_finish,
                ko.knockout_rank, ko.team_five_rank, ko.elimination_method,
                ko.team_size, ko.athletes_with_xcri, ko.team_five_xcri_pts,
                ko.h2h_wins, ko.h2h_losses, ko.h2h_win_pct,
                ko.checkpoint_date, ko.season_year, ko.calculation_date,
                tf.regl_group_name, tf.conf_group_name, tf.most_recent_race_date
            FROM iz_rankings_xcri_team_knockout ko
            LEFT JOIN iz_rankings_xcri_team_five tf
                ON ko.team_id = tf.anet_team_hnd
                AND ko.season_year = tf.season_year
                AND ko.rank_group_fk = tf.division_code
                AND ko.gender_code = tf.gender_code
                AND COALESCE(ko.checkpoint_date, '') = COALESCE(tf.checkpoint_date, '')
            WHERE {where_sql}
            ORDER BY ko.calculation_date DESC
            LIMIT 1
        """
        await cursor.execute(query_sql, params)
        result = await cursor.fetchone()

        logger.info(f"Team Knockout by ID: team_id={team_id}, found={result is not None}")

        return result


# ===================================================================
# Matchup Queries
# ===================================================================

async def get_team_matchups(
    team_id: int,
    season_year: int,
    rank_group_type: str = "D",
    rank_group_fk: Optional[int] = None,
    gender_code: Optional[str] = None,
    checkpoint_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
    """
    Get all matchups for a specific team with win-loss statistics.

    Args:
        team_id: Team identifier (required)
        season_year: Season year (required)
        rank_group_type: Ranking group type - D/R/C (default: 'D')
        rank_group_fk: Ranking group ID (optional)
        gender_code: Gender code M/F (optional)
        checkpoint_date: Rankings as of date (optional, None = LIVE)
        limit: Results per page (default: 50)
        offset: Pagination offset (default: 0)

    Returns:
        Tuple of (matchups: List[Dict], total_count: int, stats: Dict)
        stats includes: total_matchups, wins, losses, win_pct
    """
    async with get_db_cursor() as cursor:
        # Build WHERE clause (use m. alias for JOINs)
        where_clauses = [
            "(m.team_a_id = %s OR m.team_b_id = %s)",
            "m.season_year = %s",
            "m.rank_group_type = %s"
        ]
        params = [team_id, team_id, season_year, rank_group_type]

        if rank_group_fk is not None:
            where_clauses.append("m.rank_group_fk = %s")
            params.append(rank_group_fk)

        if gender_code:
            where_clauses.append("m.gender_code = %s")
            params.append(gender_code.upper())

        if checkpoint_date:
            where_clauses.append("m.checkpoint_date = %s")
            params.append(checkpoint_date)
        else:
            where_clauses.append("m.checkpoint_date IS NULL")

        where_sql = " AND ".join(where_clauses)

        # Get win-loss statistics
        stats_sql = f"""
            SELECT
                COUNT(*) as total_matchups,
                SUM(CASE WHEN m.winner_team_id = %s THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN m.winner_team_id != %s THEN 1 ELSE 0 END) as losses,
                ROUND(
                    SUM(CASE WHEN m.winner_team_id = %s THEN 1 ELSE 0 END) * 100.0 /
                    NULLIF(COUNT(*), 0),
                    1
                ) as win_pct
            FROM iz_rankings_xcri_team_knockout_matchups m
            WHERE {where_sql}
        """
        await cursor.execute(stats_sql, [team_id, team_id, team_id] + params)
        stats_row = await cursor.fetchone()

        # Get matchup details with pagination
        query_sql = f"""
            SELECT
                m.matchup_id,
                m.race_hnd,
                m.race_date,
                m.meet_name,
                m.team_a_id,
                m.team_a_rank,
                m.team_a_score,
                m.team_b_id,
                m.team_b_rank,
                m.team_b_score,
                m.winner_team_id,
                m.season_year,
                m.rank_group_type,
                m.rank_group_fk,
                m.gender_code,
                m.checkpoint_date,
                m.calculation_date,
                ta.team_name as team_a_name,
                tb.team_name as team_b_name,
                tw.team_name as winner_team_name
            FROM iz_rankings_xcri_team_knockout_matchups m
            LEFT JOIN iz_rankings_xcri_team_knockout ta
                ON m.team_a_id = ta.team_id
                AND m.season_year = ta.season_year
                AND m.rank_group_type = ta.rank_group_type
                AND m.rank_group_fk = ta.rank_group_fk
                AND m.gender_code = ta.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(ta.checkpoint_date, '9999-12-31')
            LEFT JOIN iz_rankings_xcri_team_knockout tb
                ON m.team_b_id = tb.team_id
                AND m.season_year = tb.season_year
                AND m.rank_group_type = tb.rank_group_type
                AND m.rank_group_fk = tb.rank_group_fk
                AND m.gender_code = tb.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(tb.checkpoint_date, '9999-12-31')
            LEFT JOIN iz_rankings_xcri_team_knockout tw
                ON m.winner_team_id = tw.team_id
                AND m.season_year = tw.season_year
                AND m.rank_group_type = tw.rank_group_type
                AND m.rank_group_fk = tw.rank_group_fk
                AND m.gender_code = tw.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(tw.checkpoint_date, '9999-12-31')
            WHERE {where_sql}
            ORDER BY m.race_date DESC
            LIMIT %s OFFSET %s
        """
        await cursor.execute(query_sql, params + [limit, offset])
        matchups = await cursor.fetchall()

        stats = {
            'total_matchups': stats_row['total_matchups'] or 0,
            'wins': stats_row['wins'] or 0,
            'losses': stats_row['losses'] or 0,
            'win_pct': float(stats_row['win_pct'] or 0.0)
        }

        logger.info(
            f"Team matchups: team_id={team_id}, total={stats['total_matchups']}, "
            f"wins={stats['wins']}, losses={stats['losses']}"
        )

        return matchups, stats['total_matchups'], stats


async def get_head_to_head(
    team_a_id: int,
    team_b_id: int,
    season_year: int,
    rank_group_type: str = "D",
    rank_group_fk: Optional[int] = None,
    gender_code: Optional[str] = None,
    checkpoint_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get head-to-head record between two teams.

    Args:
        team_a_id: First team identifier (required)
        team_b_id: Second team identifier (required)
        season_year: Season year (required)
        rank_group_type: Ranking group type - D/R/C (default: 'D')
        rank_group_fk: Ranking group ID (optional)
        gender_code: Gender code M/F (optional)
        checkpoint_date: Rankings as of date (optional, None = LIVE)

    Returns:
        Dict with h2h stats and matchup list
    """
    async with get_db_cursor() as cursor:
        # Build WHERE clause (with table alias for use in subqueries)
        where_clauses = [
            "((team_a_id = %s AND team_b_id = %s) OR (team_a_id = %s AND team_b_id = %s))",
            "season_year = %s",
            "rank_group_type = %s"
        ]
        params = [team_a_id, team_b_id, team_b_id, team_a_id, season_year, rank_group_type]

        if rank_group_fk is not None:
            where_clauses.append("rank_group_fk = %s")
            params.append(rank_group_fk)

        if gender_code:
            where_clauses.append("gender_code = %s")
            params.append(gender_code.upper())

        if checkpoint_date:
            where_clauses.append("checkpoint_date = %s")
            params.append(checkpoint_date)
        else:
            where_clauses.append("checkpoint_date IS NULL")

        where_sql = " AND ".join(where_clauses)

        # Build WHERE clause with table alias for main query
        where_sql_with_alias = where_sql.replace("team_a_id", "m.team_a_id") \
                                       .replace("team_b_id", "m.team_b_id") \
                                       .replace("season_year", "m.season_year") \
                                       .replace("rank_group_type", "m.rank_group_type") \
                                       .replace("rank_group_fk", "m.rank_group_fk") \
                                       .replace("gender_code", "m.gender_code") \
                                       .replace("checkpoint_date", "m.checkpoint_date")

        # Get H2H statistics
        stats_sql = f"""
            SELECT
                COUNT(*) as total_matchups,
                SUM(CASE WHEN m.winner_team_id = %s THEN 1 ELSE 0 END) as team_a_wins,
                SUM(CASE WHEN m.winner_team_id = %s THEN 1 ELSE 0 END) as team_b_wins,
                MAX(m.race_date) as latest_matchup_date,
                MAX(CASE WHEN m.race_date = (SELECT MAX(race_date) FROM iz_rankings_xcri_team_knockout_matchups WHERE {where_sql})
                    THEN m.winner_team_id ELSE NULL END) as latest_winner_id
            FROM iz_rankings_xcri_team_knockout_matchups m
            WHERE {where_sql_with_alias}
        """
        await cursor.execute(stats_sql, [team_a_id, team_b_id] + params + params)
        stats = await cursor.fetchone()

        # Get matchup details
        query_sql = f"""
            SELECT
                m.matchup_id,
                m.race_hnd,
                m.race_date,
                m.meet_name,
                m.team_a_id,
                m.team_a_rank,
                m.team_a_score,
                m.team_b_id,
                m.team_b_rank,
                m.team_b_score,
                m.winner_team_id,
                m.season_year,
                m.rank_group_type,
                m.rank_group_fk,
                m.gender_code,
                m.checkpoint_date,
                m.calculation_date,
                ta.team_name as team_a_name,
                tb.team_name as team_b_name,
                tw.team_name as winner_team_name
            FROM iz_rankings_xcri_team_knockout_matchups m
            LEFT JOIN iz_rankings_xcri_team_knockout ta
                ON m.team_a_id = ta.team_id
                AND m.season_year = ta.season_year
                AND m.rank_group_type = ta.rank_group_type
                AND m.rank_group_fk = ta.rank_group_fk
                AND m.gender_code = ta.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(ta.checkpoint_date, '9999-12-31')
            LEFT JOIN iz_rankings_xcri_team_knockout tb
                ON m.team_b_id = tb.team_id
                AND m.season_year = tb.season_year
                AND m.rank_group_type = tb.rank_group_type
                AND m.rank_group_fk = tb.rank_group_fk
                AND m.gender_code = tb.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(tb.checkpoint_date, '9999-12-31')
            LEFT JOIN iz_rankings_xcri_team_knockout tw
                ON m.winner_team_id = tw.team_id
                AND m.season_year = tw.season_year
                AND m.rank_group_type = tw.rank_group_type
                AND m.rank_group_fk = tw.rank_group_fk
                AND m.gender_code = tw.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(tw.checkpoint_date, '9999-12-31')
            WHERE {where_sql_with_alias}
            ORDER BY m.race_date DESC
        """
        await cursor.execute(query_sql, params)
        matchups = await cursor.fetchall()

        # Get team names
        team_a_name = matchups[0]['team_a_name'] if matchups and matchups[0]['team_a_id'] == team_a_id else None
        if not team_a_name and matchups:
            team_a_name = matchups[0]['team_b_name'] if matchups[0]['team_b_id'] == team_a_id else None

        team_b_name = matchups[0]['team_b_name'] if matchups and matchups[0]['team_b_id'] == team_b_id else None
        if not team_b_name and matchups:
            team_b_name = matchups[0]['team_a_name'] if matchups[0]['team_a_id'] == team_b_id else None

        result = {
            'team_a_id': team_a_id,
            'team_a_name': team_a_name,
            'team_b_id': team_b_id,
            'team_b_name': team_b_name,
            'total_matchups': stats['total_matchups'] or 0,
            'team_a_wins': stats['team_a_wins'] or 0,
            'team_b_wins': stats['team_b_wins'] or 0,
            'latest_matchup_date': stats['latest_matchup_date'],
            'latest_winner_id': stats['latest_winner_id'],
            'matchups': matchups
        }

        logger.info(
            f"H2H: team_a={team_a_id} vs team_b={team_b_id}, "
            f"total={result['total_matchups']}, a_wins={result['team_a_wins']}, b_wins={result['team_b_wins']}"
        )

        return result


async def get_meet_matchups(
    race_hnd: int,
    season_year: int,
    checkpoint_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all matchups from a specific meet/race.

    Args:
        race_hnd: Race handle (required)
        season_year: Season year (required)
        checkpoint_date: Rankings as of date (optional, None = LIVE)

    Returns:
        Dict with meet info and matchup list
    """
    async with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = ["m.race_hnd = %s", "m.season_year = %s"]
        params = [race_hnd, season_year]

        if checkpoint_date:
            where_clauses.append("m.checkpoint_date = %s")
            params.append(checkpoint_date)
        else:
            where_clauses.append("m.checkpoint_date IS NULL")

        where_sql = " AND ".join(where_clauses)

        # Get matchups with team names
        query_sql = f"""
            SELECT
                m.matchup_id,
                m.race_hnd,
                m.race_date,
                m.meet_name,
                m.team_a_id,
                m.team_a_rank,
                m.team_a_score,
                m.team_b_id,
                m.team_b_rank,
                m.team_b_score,
                m.winner_team_id,
                m.season_year,
                m.rank_group_type,
                m.rank_group_fk,
                m.gender_code,
                m.checkpoint_date,
                m.calculation_date,
                ta.team_name as team_a_name,
                tb.team_name as team_b_name,
                tw.team_name as winner_team_name
            FROM iz_rankings_xcri_team_knockout_matchups m
            LEFT JOIN iz_rankings_xcri_team_knockout ta
                ON m.team_a_id = ta.team_id
                AND m.season_year = ta.season_year
                AND m.rank_group_type = ta.rank_group_type
                AND m.rank_group_fk = ta.rank_group_fk
                AND m.gender_code = ta.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(ta.checkpoint_date, '9999-12-31')
            LEFT JOIN iz_rankings_xcri_team_knockout tb
                ON m.team_b_id = tb.team_id
                AND m.season_year = tb.season_year
                AND m.rank_group_type = tb.rank_group_type
                AND m.rank_group_fk = tb.rank_group_fk
                AND m.gender_code = tb.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(tb.checkpoint_date, '9999-12-31')
            LEFT JOIN iz_rankings_xcri_team_knockout tw
                ON m.winner_team_id = tw.team_id
                AND m.season_year = tw.season_year
                AND m.rank_group_type = tw.rank_group_type
                AND m.rank_group_fk = tw.rank_group_fk
                AND m.gender_code = tw.gender_code
                AND COALESCE(m.checkpoint_date, '9999-12-31') = COALESCE(tw.checkpoint_date, '9999-12-31')
            WHERE {where_sql}
            ORDER BY m.team_a_rank ASC, m.team_b_rank ASC
        """
        await cursor.execute(query_sql, params)
        matchups = await cursor.fetchall()

        if not matchups:
            return {
                'race_hnd': race_hnd,
                'meet_name': None,
                'race_date': None,
                'total_matchups': 0,
                'matchups': []
            }

        result = {
            'race_hnd': race_hnd,
            'meet_name': matchups[0]['meet_name'],
            'race_date': matchups[0]['race_date'],
            'total_matchups': len(matchups),
            'matchups': matchups
        }

        logger.info(f"Meet matchups: race_hnd={race_hnd}, total={result['total_matchups']}")

        return result


async def get_common_opponents(
    team_a_id: int,
    team_b_id: int,
    season_year: int,
    rank_group_type: str = "D",
    rank_group_fk: Optional[int] = None,
    gender_code: Optional[str] = None,
    checkpoint_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find common opponents between two teams.

    Args:
        team_a_id: First team identifier (required)
        team_b_id: Second team identifier (required)
        season_year: Season year (required)
        rank_group_type: Ranking group type - D/R/C (default: 'D')
        rank_group_fk: Ranking group ID (optional)
        gender_code: Gender code M/F (optional)
        checkpoint_date: Rankings as of date (optional, None = LIVE)

    Returns:
        Dict with common opponent analysis
    """
    async with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = ["m1.season_year = %s", "m1.rank_group_type = %s"]
        params = [season_year, rank_group_type]

        if rank_group_fk is not None:
            where_clauses.append("m1.rank_group_fk = %s")
            params.append(rank_group_fk)

        if gender_code:
            where_clauses.append("m1.gender_code = %s")
            params.append(gender_code.upper())

        if checkpoint_date:
            where_clauses.append("m1.checkpoint_date = %s")
            where_clauses.append("m2.checkpoint_date = %s")
            params.extend([checkpoint_date, checkpoint_date])
        else:
            where_clauses.append("m1.checkpoint_date IS NULL")
            where_clauses.append("m2.checkpoint_date IS NULL")

        where_sql = " AND ".join(where_clauses)

        # Find common opponents
        query_sql = f"""
            SELECT
                CASE
                    WHEN m1.team_a_id = %s THEN m1.team_b_id
                    ELSE m1.team_a_id
                END as opponent_id,
                MAX(t.team_name) as opponent_name,
                SUM(CASE WHEN m1.winner_team_id = %s THEN 1 ELSE 0 END) as team_a_wins,
                SUM(CASE WHEN m1.winner_team_id != %s THEN 1 ELSE 0 END) as team_a_losses,
                SUM(CASE WHEN m2.winner_team_id = %s THEN 1 ELSE 0 END) as team_b_wins,
                SUM(CASE WHEN m2.winner_team_id != %s THEN 1 ELSE 0 END) as team_b_losses
            FROM iz_rankings_xcri_team_knockout_matchups m1
            INNER JOIN iz_rankings_xcri_team_knockout_matchups m2
                ON (
                    (m1.team_a_id != %s AND m1.team_a_id != %s AND (m2.team_a_id = m1.team_a_id OR m2.team_b_id = m1.team_a_id))
                    OR
                    (m1.team_b_id != %s AND m1.team_b_id != %s AND (m2.team_a_id = m1.team_b_id OR m2.team_b_id = m1.team_b_id))
                )
                AND (m2.team_a_id = %s OR m2.team_b_id = %s)
                AND m1.season_year = m2.season_year
                AND m1.rank_group_type = m2.rank_group_type
                AND m1.rank_group_fk = m2.rank_group_fk
                AND m1.gender_code = m2.gender_code
            LEFT JOIN iz_rankings_xcri_team_knockout t
                ON CASE
                    WHEN m1.team_a_id = %s THEN m1.team_b_id
                    ELSE m1.team_a_id
                END = t.team_id
                AND m1.season_year = t.season_year
                AND m1.rank_group_type = t.rank_group_type
                AND m1.rank_group_fk = t.rank_group_fk
                AND m1.gender_code = t.gender_code
                AND COALESCE(m1.checkpoint_date, '9999-12-31') = COALESCE(t.checkpoint_date, '9999-12-31')
            WHERE (m1.team_a_id = %s OR m1.team_b_id = %s)
              AND {where_sql}
            GROUP BY opponent_id
            HAVING opponent_id NOT IN (%s, %s)
            ORDER BY (SUM(CASE WHEN m1.winner_team_id = %s THEN 1 ELSE 0 END) + SUM(CASE WHEN m2.winner_team_id = %s THEN 1 ELSE 0 END)) DESC
        """

        query_params = [
            team_a_id, team_a_id, team_a_id, team_b_id, team_b_id,  # CASE and SUM clauses
            team_a_id, team_b_id, team_a_id, team_b_id, team_b_id, team_b_id,  # JOIN conditions
            team_a_id, team_a_id, team_a_id,  # WHERE and LEFT JOIN
        ] + params + [team_a_id, team_b_id, team_a_id, team_b_id]  # HAVING + ORDER BY clauses

        await cursor.execute(query_sql, query_params)
        common_opponents = await cursor.fetchall()

        # Calculate summary statistics
        team_a_total_wins = sum(opp['team_a_wins'] for opp in common_opponents)
        team_a_total_losses = sum(opp['team_a_losses'] for opp in common_opponents)
        team_b_total_wins = sum(opp['team_b_wins'] for opp in common_opponents)
        team_b_total_losses = sum(opp['team_b_losses'] for opp in common_opponents)

        result = {
            'team_a_id': team_a_id,
            'team_a_name': None,  # Will be filled by route handler if needed
            'team_b_id': team_b_id,
            'team_b_name': None,  # Will be filled by route handler if needed
            'total_common_opponents': len(common_opponents),
            'team_a_record_vs_common': f"{team_a_total_wins}-{team_a_total_losses}",
            'team_b_record_vs_common': f"{team_b_total_wins}-{team_b_total_losses}",
            'common_opponents': common_opponents
        }

        logger.info(
            f"Common opponents: team_a={team_a_id} vs team_b={team_b_id}, "
            f"total_common={result['total_common_opponents']}"
        )

        return result
