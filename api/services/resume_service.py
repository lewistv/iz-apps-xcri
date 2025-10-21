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
    anet_group_hnd: int,
    season_year: int = 2025,
    division_code: Optional[int] = None,
    gender_code: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get season resume for a specific team.

    Args:
        anet_group_hnd: AthleticNet group handle (team ID)
        season_year: Season year (default: 2025)
        division_code: Division code (optional, e.g., 2030 for D1)
        gender_code: Gender code M/F (optional)

    Returns:
        Resume record dictionary or None if not found
        {
            'group_resume_id': int,
            'season_year': int,
            'anet_group_hnd': int,
            'division_code': int,
            'gender_code': str,
            'resume_html': str,
            'created_at': datetime,
            'updated_at': datetime
        }
    """
    with get_db_cursor() as cursor:
        # Build WHERE clause
        where_clauses = [
            "anet_group_hnd = %s",
            "season_year = %s"
        ]
        params = [anet_group_hnd, season_year]

        if division_code is not None:
            where_clauses.append("division_code = %s")
            params.append(division_code)

        if gender_code:
            where_clauses.append("gender_code = %s")
            params.append(gender_code)

        where_sql = " AND ".join(where_clauses)

        query_sql = f"""
            SELECT
                group_resume_id,
                season_year,
                anet_group_hnd,
                division_code,
                gender_code,
                resume_html,
                created_at,
                updated_at
            FROM iz_groups_season_resumes
            WHERE {where_sql}
            ORDER BY updated_at DESC
            LIMIT 1
        """
        cursor.execute(query_sql, params)
        result = cursor.fetchone()

        if result:
            logger.info(
                f"Resume found: group_hnd={anet_group_hnd}, "
                f"season={season_year}, division={division_code}, gender={gender_code}"
            )
        else:
            logger.info(
                f"Resume not found: group_hnd={anet_group_hnd}, "
                f"season={season_year}, division={division_code}, gender={gender_code}"
            )

        return result
