"""
XCRI Rankings API - Resume Service

Business logic for querying season resumes from database.
Session 004: Created for Issue #15 (Season Resume Integration)
"""

import logging
from typing import Optional, Dict, Any

from database import get_db_cursor

logger = logging.getLogger(__name__)


def get_team_resume(
    anet_team_hnd: int,
    season_year: int = 2025,
    division_code: Optional[int] = None,
    gender_code: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get season resume for a specific team.

    Args:
        anet_team_hnd: AthleticNet team handle (IDSchool in iz_athnet_teams)
        season_year: Season year (default: 2025)
        division_code: Division code (optional, currently not used in query)
        gender_code: Gender code M/F (optional)

    Returns:
        Resume record dictionary or None if not found
        {
            'id': int,
            'season_year': int,
            'group_fk': int,
            'gender_fk': int,
            'sport_fk': int,
            'season_html': str,
            'created_at': datetime,
            'updated_at': datetime
        }
    """
    with get_db_cursor() as cursor:
        # Build WHERE clause
        # Map gender code (M/F) to gender_fk (1/2)
        gender_fk = None
        if gender_code:
            gender_fk = 1 if gender_code.upper() == 'M' else 2

        where_clauses = [
            "t.IDSchool = %s",
            "r.season_year = %s",
            "r.sport_fk = 3"  # 3 = Cross Country
        ]
        params = [anet_team_hnd, season_year]

        if gender_fk is not None:
            where_clauses.append("r.gender_fk = %s")
            params.append(gender_fk)

        where_sql = " AND ".join(where_clauses)

        # Join through iz_athnet_teams to map anet_team_hnd to group_fk
        query_sql = f"""
            SELECT
                r.id,
                r.season_year,
                r.group_fk,
                r.gender_fk,
                r.sport_fk,
                r.season_html,
                r.created_at,
                r.updated_at
            FROM iz_groups_season_resumes r
            JOIN iz_athnet_teams t ON r.group_fk = t.UstfcccaId
            WHERE {where_sql}
            ORDER BY r.updated_at DESC
            LIMIT 1
        """
        cursor.execute(query_sql, params)
        result = cursor.fetchone()

        if result:
            logger.info(
                f"Resume found: anet_team_hnd={anet_team_hnd}, "
                f"season={season_year}, gender_code={gender_code}"
            )
        else:
            logger.info(
                f"Resume not found: anet_team_hnd={anet_team_hnd}, "
                f"season={season_year}, gender_code={gender_code}"
            )

        return result
