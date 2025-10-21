"""
XCRI Rankings API - Athlete Routes

FastAPI routes for athlete ranking endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status

from models import (
    AthleteListResponse,
    AthleteRanking,
    ErrorResponse
)
from services import athlete_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/athletes",
    tags=["athletes"],
    responses={
        404: {"model": ErrorResponse, "description": "Athlete not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=AthleteListResponse,
    summary="List athlete rankings",
    description="""
    Get paginated list of athlete rankings with optional filters.

    **Filters:**
    - division: Filter by NCAA division (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)
    - gender: Filter by gender (M or F)
    - region: Filter by region name
    - conference: Filter by conference name
    - search: Search by athlete name or school name
    - min_races: Filter by minimum number of races

    **Pagination:**
    - limit: Results per page (default: 25, max: 500)
    - offset: Number of results to skip (for pagination)

    **Example:**
    ```
    GET /athletes?division=2030&gender=M&limit=25
    ```
    """
)
async def list_athletes(
    season_year: int = Query(
        default=2024,
        description="Season year"
    ),
    division: Optional[int] = Query(
        default=None,
        description="Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)"
    ),
    gender: Optional[str] = Query(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    ),
    scoring_group: str = Query(
        default="division",
        description="Scoring scope (division, region_XX, conference_XX)"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for full season"
    ),
    algorithm_type: str = Query(
        default="light",
        description="Algorithm type (light or heavy)"
    ),
    limit: int = Query(
        default=settings.default_limit,
        ge=1,
        le=settings.max_limit,
        description="Results per page"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination offset"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by athlete name or school name",
        min_length=2
    ),
    min_races: Optional[int] = Query(
        default=None,
        ge=1,
        description="Minimum number of races"
    ),
    region: Optional[str] = Query(
        default=None,
        description="Filter by region name"
    ),
    conference: Optional[str] = Query(
        default=None,
        description="Filter by conference name"
    )
):
    """List athlete rankings with filters and pagination"""
    try:
        results, total = athlete_service.get_athletes(
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type,
            limit=limit,
            offset=offset,
            search=search,
            min_races=min_races,
            region=region,
            conference=conference
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"Error listing athletes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve athlete rankings: {str(e)}"
        )


@router.get(
    "/{athlete_hnd}",
    response_model=AthleteRanking,
    summary="Get athlete by ID",
    description="""
    Get a single athlete's ranking by AthleticNet athlete handle.

    **Example:**
    ```
    GET /athletes/12345?season_year=2024&division=2030&gender=M
    ```
    """
)
async def get_athlete(
    athlete_hnd: int,
    season_year: int = Query(default=2024, description="Season year"),
    division: Optional[int] = Query(
        default=None,
        description="Division code (optional, for disambiguation)"
    ),
    gender: Optional[str] = Query(
        default=None,
        description="Gender code (optional, for disambiguation)",
        pattern="^[MFmf]$"
    ),
    scoring_group: str = Query(
        default="division",
        description="Scoring scope"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD)"
    ),
    algorithm_type: str = Query(
        default="light",
        description="Algorithm type"
    )
):
    """Get single athlete by AthleticNet athlete handle"""
    try:
        result = athlete_service.get_athlete_by_id(
            athlete_hnd=athlete_hnd,
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Athlete {athlete_hnd} not found for season {season_year}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting athlete {athlete_hnd}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve athlete: {str(e)}"
        )


@router.get(
    "/team/{team_hnd}/roster",
    response_model=AthleteListResponse,
    summary="Get team roster",
    description="""
    Get all athletes on a team's roster.

    Returns athletes sorted by rank (best to worst).

    **Example:**
    ```
    GET /athletes/team/123/roster?season_year=2024&division=2030&gender=M
    ```
    """
)
async def get_team_roster(
    team_hnd: int,
    season_year: int = Query(default=2024, description="Season year"),
    division: Optional[int] = Query(
        default=None,
        description="Division code"
    ),
    gender: Optional[str] = Query(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    ),
    scoring_group: str = Query(
        default="division",
        description="Scoring scope"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD)"
    ),
    algorithm_type: str = Query(
        default="light",
        description="Algorithm type"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Maximum athletes to return"
    )
):
    """Get team roster (all athletes on team)"""
    try:
        results, total = athlete_service.get_team_roster(
            team_hnd=team_hnd,
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type,
            limit=limit
        )

        return {
            "total": total,
            "limit": limit,
            "offset": 0,
            "results": results
        }

    except Exception as e:
        logger.error(f"Error getting team roster {team_hnd}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team roster: {str(e)}"
        )
