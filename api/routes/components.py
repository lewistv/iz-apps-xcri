"""
XCRI Rankings API - Components Routes

FastAPI routes for SCS component score endpoints (SAGA, SEWR, OSMA, XCRI).
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status, Path

from models import (
    ComponentBreakdown,
    ComponentLeaderboardResponse,
    ErrorResponse
)
from services import components_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/components",
    tags=["components"],
    responses={
        404: {"model": ErrorResponse, "description": "Component data not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/athletes/{athlete_hnd}",
    response_model=ComponentBreakdown,
    summary="Get athlete component breakdown",
    description="""
    Get detailed SCS component score breakdown for a specific athlete.

    Returns all four components with ranks and additional metrics:
    - **SAGA** (Season Adjusted Gap Average): Raw performance quality (lower is better)
    - **SEWR** (Season Equivalent Win Rate): Competitive success (higher is better)
    - **OSMA** (Opponent Season Meet Average): Strength of schedule (higher is better)
    - **XCRI** (Heavy XCRI): Final composite score (higher is better)

    Also includes AGS (Adjusted Gap Score), CPR (Contest Performance Rating),
    race quality metrics, and opponent counts.

    **Example:**
    ```
    GET /components/athletes/19019918?season_year=2024&division=2030&gender=M
    ```
    """
)
async def get_athlete_components(
    athlete_hnd: int = Path(
        ...,
        description="AthleticNet athlete handle"
    ),
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
    )
):
    """Get component score breakdown for specific athlete."""
    try:
        result = components_service.get_athlete_components(
            athlete_hnd=athlete_hnd,
            season_year=season_year,
            division=division,
            gender=gender
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component data not found for athlete {athlete_hnd}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting athlete components: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve component data"
        )


@router.get(
    "/leaderboard",
    response_model=ComponentLeaderboardResponse,
    summary="Get component leaderboard",
    description="""
    Get top athletes ranked by a specific SCS component.

    **Components:**
    - **saga**: Season Adjusted Gap Average (raw performance, lower is better)
    - **sewr**: Season Equivalent Win Rate (competitive success, higher is better)
    - **osma**: Opponent Season Meet Average (strength of schedule, higher is better)
    - **xcri**: Heavy XCRI composite score (overall rating, higher is better)

    Results include all component scores for each athlete to enable comparison.

    **Example:**
    ```
    GET /components/leaderboard?component=saga&division=2030&gender=M&limit=25
    ```
    """
)
async def get_component_leaderboard(
    component: str = Query(
        ...,
        description="Component name (saga, sewr, osma, or xcri)",
        pattern="^(saga|sewr|osma|xcri)$"
    ),
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
    )
):
    """Get top athletes ranked by specific component."""
    try:
        results, total = components_service.get_component_leaderboard(
            component=component,
            season_year=season_year,
            division=division,
            gender=gender,
            limit=limit,
            offset=offset
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "component": component,
            "results": results
        }

    except ValueError as e:
        # Invalid component name
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting component leaderboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve component leaderboard"
        )
