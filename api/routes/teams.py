"""
XCRI Rankings API - Team Routes

FastAPI routes for team ranking endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status

from webapp.api.models import (
    TeamListResponse,
    TeamRanking,
    ErrorResponse
)
from webapp.api.services import team_service
from webapp.api.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={
        404: {"model": ErrorResponse, "description": "Team not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=TeamListResponse,
    summary="List team rankings",
    description="""
    Get paginated list of team rankings with optional filters.

    **Filters:**
    - division: Filter by NCAA division (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)
    - gender: Filter by gender (M or F)
    - region: Filter by region name
    - conference: Filter by conference name
    - search: Search by school name

    **Pagination:**
    - limit: Results per page (default: 25, max: 500)
    - offset: Number of results to skip (for pagination)

    **Example:**
    ```
    GET /teams?division=2030&gender=M&limit=25
    ```
    """
)
async def list_teams(
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
        description="Search by school name",
        min_length=2
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
    """List team rankings with filters and pagination"""
    try:
        results, total = team_service.get_teams(
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type,
            limit=limit,
            offset=offset,
            search=search,
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
        logger.error(f"Error listing teams: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team rankings: {str(e)}"
        )


@router.get(
    "/{team_hnd}",
    response_model=TeamRanking,
    summary="Get team by ID",
    description="""
    Get a single team's ranking by AthleticNet team handle.

    **Example:**
    ```
    GET /teams/123?season_year=2024&division=2030&gender=M
    ```
    """
)
async def get_team(
    team_hnd: int,
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
    """Get single team by AthleticNet team handle"""
    try:
        result = team_service.get_team_by_id(
            team_hnd=team_hnd,
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
                detail=f"Team {team_hnd} not found for season {season_year}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team {team_hnd}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team: {str(e)}"
        )
