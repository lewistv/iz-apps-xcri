"""
XCRI Rankings API - Snapshot Service

Business logic for retrieving historical snapshot data from MySQL database.
"""

import logging
from typing import List, Dict, Tuple, Optional
from database_async import get_db_cursor

logger = logging.getLogger(__name__)


class SnapshotService:
    """Service for managing historical ranking snapshots"""

    def __init__(self):
        """Initialize snapshot service"""
        pass

    async def list_snapshots(self) -> List[Dict]:
        """
        List all available snapshot dates from MySQL.

        Returns:
            List of snapshot dictionaries with date, season, divisions, and athlete count
        """
        snapshots = []

        try:
            async with get_db_cursor() as cursor:
                query = """
                SELECT
                    checkpoint_date as date,
                    season_year as season,
                    COUNT(DISTINCT division_code) as divisions,
                    COUNT(DISTINCT gender_code) as genders,
                    COUNT(*) as total_athletes
                FROM iz_rankings_xcri_athlete_rankings
                WHERE checkpoint_date IS NOT NULL
                    AND algorithm_type = %s
                    AND scoring_group = %s
                GROUP BY checkpoint_date, season_year
                ORDER BY checkpoint_date DESC
                """
                await cursor.execute(query, ["light", "division"])
                results = await cursor.fetchall()

                for row in results:
                    snapshot_date = row['date'].strftime('%Y-%m-%d') if row['date'] else None
                    if snapshot_date:
                        snapshots.append({
                            "date": snapshot_date,
                            "season": row['season'],
                            "divisions": row['divisions'],
                            "genders": row['genders'],
                            "total_athletes": row['total_athletes'],
                            "display_name": self._format_display_date(snapshot_date)
                        })

                logger.info(f"Found {len(snapshots)} snapshots in MySQL")
                return snapshots

        except Exception as e:
            logger.error(f"Error listing snapshots from MySQL: {e}", exc_info=True)
            return []

    async def get_snapshot_athletes(
        self,
        snapshot_date: str,
        division: int,
        gender: str,
        limit: int = 25,
        offset: int = 0,
        search: Optional[str] = None,
        region: Optional[str] = None,
        conference: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """
        Get athlete rankings from a specific snapshot via MySQL.

        Args:
            snapshot_date: Date string (YYYY-MM-DD)
            division: Division code (2030=D1, 2031=D2, etc.)
            gender: Gender code (M or F)
            limit: Maximum results to return
            offset: Pagination offset
            search: Optional search term for athlete/school name
            region: Optional filter by region name
            conference: Optional filter by conference name

        Returns:
            Tuple of (athletes list, total count)
        """
        try:
            async with get_db_cursor() as cursor:
                # Build base WHERE clause
                where_clauses = [
                    "checkpoint_date = %s",
                    "division_code = %s",
                    "gender_code = %s",
                    "algorithm_type = %s",
                    "scoring_group = %s"
                ]
                params = [snapshot_date, division, gender.upper(), "light", "division"]

                # Add search filter if provided
                if search:
                    where_clauses.append("(athlete_name_first LIKE %s OR athlete_name_last LIKE %s OR team_name LIKE %s)")
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern, search_pattern])

                # Add region filter if provided
                if region:
                    where_clauses.append("regl_group_name = %s")
                    params.append(region)

                # Add conference filter if provided
                if conference:
                    where_clauses.append("conf_group_name = %s")
                    params.append(conference)

                where_sql = " AND ".join(where_clauses)

                # Get total count
                count_query = f"""
                SELECT COUNT(*) as total
                FROM iz_rankings_xcri_athlete_rankings
                WHERE {where_sql}
                """
                await cursor.execute(count_query, params)
                total = (await cursor.fetchone())['total']

                # Get paginated results
                data_query = f"""
                SELECT
                    athlete_rank as rank,
                    CONCAT(athlete_name_first, ' ', athlete_name_last) as athlete_name,
                    team_name,
                    division_code as division,
                    xcri_score,
                    races_count as num_races,
                    season_average as season_avg,
                    h2h_wins,
                    h2h_losses,
                    min_opponent_quality as quality_of_wins,
                    anet_athlete_hnd,
                    saga_score,
                    sewr_score,
                    osma_score,
                    scs_score,
                    regl_group_name,
                    conf_group_name
                FROM iz_rankings_xcri_athlete_rankings
                WHERE {where_sql}
                ORDER BY athlete_rank ASC
                LIMIT %s OFFSET %s
                """
                await cursor.execute(data_query, params + [limit, offset])
                results = await cursor.fetchall()

                athletes = [dict(row) for row in results]
                logger.info(f"Loaded {len(athletes)} athletes from MySQL snapshot {snapshot_date}")

                return athletes, total

        except Exception as e:
            logger.error(f"Error reading snapshot {snapshot_date} from MySQL: {e}", exc_info=True)
            return [], 0

    async def get_snapshot_teams(
        self,
        snapshot_date: str,
        division: int,
        gender: str,
        limit: int = 25,
        offset: int = 0,
        search: Optional[str] = None,
        region: Optional[str] = None,
        conference: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """
        Get team rankings from a specific snapshot via MySQL.

        Args:
            snapshot_date: Date string (YYYY-MM-DD)
            division: Division code
            gender: Gender code (M or F)
            limit: Maximum results to return
            offset: Pagination offset
            search: Optional search term for team name
            region: Optional filter by region name
            conference: Optional filter by conference name

        Returns:
            Tuple of (teams list, total count)
        """
        try:
            async with get_db_cursor() as cursor:
                # Build base WHERE clause
                where_clauses = [
                    "checkpoint_date = %s",
                    "division_code = %s",
                    "gender_code = %s",
                    "algorithm_type = %s",
                    "scoring_group = %s"
                ]
                params = [snapshot_date, division, gender.upper(), "light", "division"]

                # Add search filter if provided
                if search:
                    where_clauses.append("team_name LIKE %s")
                    params.append(f"%{search}%")

                # Add region filter if provided
                if region:
                    where_clauses.append("regl_group_name = %s")
                    params.append(region)

                # Add conference filter if provided
                if conference:
                    where_clauses.append("conf_group_name = %s")
                    params.append(conference)

                where_sql = " AND ".join(where_clauses)

                # Get total count
                count_query = f"""
                SELECT COUNT(*) as total
                FROM iz_rankings_xcri_team_rankings
                WHERE {where_sql}
                """
                await cursor.execute(count_query, params)
                total = (await cursor.fetchone())['total']

                # Get paginated results
                data_query = f"""
                SELECT
                    team_rank as rank,
                    team_name,
                    anet_team_hnd,
                    division_code as division,
                    gender_code,
                    team_xcri_score as team_score,
                    athletes_count as squad_size,
                    top5_average as top5_avg,
                    top7_average as top7_avg,
                    regl_group_name,
                    conf_group_name
                FROM iz_rankings_xcri_team_rankings
                WHERE {where_sql}
                ORDER BY team_rank ASC
                LIMIT %s OFFSET %s
                """
                await cursor.execute(data_query, params + [limit, offset])
                results = await cursor.fetchall()

                teams = [dict(row) for row in results]
                logger.info(f"Loaded {len(teams)} teams from MySQL snapshot {snapshot_date}")

                return teams, total

        except Exception as e:
            logger.error(f"Error reading snapshot teams {snapshot_date} from MySQL: {e}", exc_info=True)
            return [], 0

    async def get_snapshot_metadata(self, snapshot_date: str) -> Dict:
        """
        Get metadata for a specific snapshot from MySQL.

        Args:
            snapshot_date: Date string (YYYY-MM-DD)

        Returns:
            Metadata dictionary
        """
        try:
            season = int(snapshot_date[:4])

            async with get_db_cursor() as cursor:
                # Get divisions/genders available for this snapshot
                query = """
                SELECT
                    division_code,
                    gender_code,
                    COUNT(*) as athlete_count
                FROM iz_rankings_xcri_athlete_rankings
                WHERE checkpoint_date = %s
                    AND algorithm_type = %s
                    AND scoring_group = %s
                GROUP BY division_code, gender_code
                ORDER BY division_code, gender_code
                """
                await cursor.execute(query, [snapshot_date, "light", "division"])
                results = await cursor.fetchall()

                if not results:
                    return {
                        "date": snapshot_date,
                        "season": season,
                        "divisions_available": [],
                        "total_combinations": 0,
                        "status": "not_found"
                    }

                divisions_available = []
                for row in results:
                    divisions_available.append({
                        "division_code": row['division_code'],
                        "gender": row['gender_code'],
                        "athlete_count": row['athlete_count']
                    })

                return {
                    "date": snapshot_date,
                    "season": season,
                    "divisions_available": divisions_available,
                    "total_combinations": len(divisions_available),
                    "status": "available"
                }

        except Exception as e:
            logger.error(f"Error getting snapshot metadata for {snapshot_date}: {e}", exc_info=True)
            return {
                "date": snapshot_date,
                "season": int(snapshot_date[:4]) if snapshot_date else None,
                "divisions_available": [],
                "total_combinations": 0,
                "status": "error"
            }

    def _format_display_date(self, date_str: str) -> str:
        """Format date string for display (YYYY-MM-DD -> Month DD, YYYY)"""
        from datetime import datetime
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except:
            return date_str


# Create singleton instance
snapshot_service = SnapshotService()
