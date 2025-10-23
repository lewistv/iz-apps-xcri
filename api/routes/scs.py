"""
XCRI Rankings API - SCS Component Routes

REST endpoints for accessing SCS component breakdowns.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from services import scs_service
from models import (
    SCSComponents,
    SCSComponentLeaderboard,
    SCSComponentComparison,
    SCSComponentDistribution
)

router = APIRouter(prefix="/scs", tags=["SCS Components"])


@router.get("/athletes/{athlete_hnd}/components", response_model=SCSComponents)
async def get_athlete_scs_components(
    athlete_hnd: int,
    season_year: int = Query(2024, description="Season year"),
    division: Optional[int] = Query(None, description="Division code (e.g., 2030 for D1)"),
    gender: Optional[str] = Query(None, description="Gender (M/F)")
):
    """
    Get detailed SCS component breakdown for a specific athlete.

    Returns all SCS components (SAGA, SEWR, OSMA, XCRI) with scores and ranks.

    **Example**: `/scs/athletes/12345678/components?season_year=2024&division=2030&gender=M`
    """
    result = await scs_service.get_athlete_scs_components(
        athlete_hnd=athlete_hnd,
        season_year=season_year,
        division=division,
        gender=gender
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"SCS components not found for athlete {athlete_hnd}"
        )

    return result


@router.get("/leaderboard/{component}", response_model=SCSComponentLeaderboard)
async def get_component_leaderboard(
    component: str,
    season_year: int = Query(2024, description="Season year"),
    division: int = Query(2030, description="Division code"),
    gender: str = Query("M", description="Gender (M/F)"),
    limit: int = Query(25, description="Number of results", le=100)
):
    """
    Get top athletes ranked by a specific SCS component.

    **Components available**:
    - `saga`: Season Adjusted Gap Average
    - `sewr`: Season Equal-Weight Rating (own performance)
    - `osma`: Opponent Strength of Schedule
    - `xcri`: Final SCS (composite score)

    **Example**: `/scs/leaderboard/saga?season_year=2024&division=2030&gender=M&limit=25`
    """
    try:
        results, total = await scs_service.get_component_leaderboard(
            component=component,
            season_year=season_year,
            division=division,
            gender=gender,
            limit=limit
        )

        return {
            'component': component.upper(),
            'season_year': season_year,
            'division_code': division,
            'gender_code': gender,
            'total_athletes': total,
            'limit': limit,
            'results': results
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/athletes/{athlete_hnd}/comparison", response_model=SCSComponentComparison)
async def get_athlete_component_comparison(
    athlete_hnd: int,
    season_year: int = Query(2024, description="Season year"),
    division: int = Query(2030, description="Division code"),
    gender: str = Query("M", description="Gender (M/F)")
):
    """
    Get athlete's SCS components with division context (percentiles, etc.).

    Provides detailed comparison showing where the athlete ranks on each
    component relative to all athletes in the division.

    **Example**: `/scs/athletes/12345678/comparison?season_year=2024&division=2030&gender=M`
    """
    result = await scs_service.get_component_comparison(
        athlete_hnd=athlete_hnd,
        season_year=season_year,
        division=division,
        gender=gender
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"SCS components not found for athlete {athlete_hnd}"
        )

    return result


@router.get("/distribution/{component}", response_model=SCSComponentDistribution)
async def get_component_distribution(
    component: str,
    season_year: int = Query(2024, description="Season year"),
    division: int = Query(2030, description="Division code"),
    gender: str = Query("M", description="Gender (M/F)"),
    bins: int = Query(10, description="Number of histogram bins", ge=5, le=20)
):
    """
    Get distribution statistics for a specific SCS component.

    Returns min, max, mean, median, standard deviation, and percentiles
    for the specified component across all athletes in the division.

    **Components available**:
    - `saga`: Season Adjusted Gap Average
    - `sewr`: Season Equal-Weight Rating
    - `osma`: Opponent Strength of Schedule
    - `xcri`: Final SCS

    **Example**: `/scs/distribution/sewr?season_year=2024&division=2030&gender=M`
    """
    try:
        result = await scs_service.get_component_distribution(
            component=component,
            season_year=season_year,
            division=division,
            gender=gender,
            bins=bins
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Additional convenience endpoints

@router.get("/athletes/{athlete_hnd}/discrepancy")
async def get_athlete_rank_discrepancy(
    athlete_hnd: int,
    season_year: int = Query(2024, description="Season year"),
    division: int = Query(2030, description="Division code"),
    gender: str = Query("M", description="Gender (M/F)")
):
    """
    Get athlete's rank discrepancies between XCRI Light and SCS components.

    Useful for identifying athletes who perform differently in competitive
    rankings vs. statistical metrics.

    **Example**: `/scs/athletes/12345678/discrepancy?season_year=2024&division=2030&gender=M`
    """
    # This endpoint would join with main athlete_rankings table
    # to compare XCRI Light rank vs SCS component ranks
    # Implementation left as future enhancement
    raise HTTPException(
        status_code=501,
        detail="Endpoint not yet implemented - coming soon"
    )


@router.get("/biggest-discrepancies")
async def get_biggest_rank_discrepancies(
    season_year: int = Query(2024, description="Season year"),
    division: int = Query(2030, description="Division code"),
    gender: str = Query("M", description="Gender (M/F)"),
    limit: int = Query(25, description="Number of results", le=100)
):
    """
    Get athletes with the biggest discrepancies between XCRI Light rank
    and SCS rank.

    Highlights tactical racers (win races despite slower times) or
    statistical stars (fast times but fewer quality wins).

    **Example**: `/scs/biggest-discrepancies?season_year=2024&division=2030&gender=M&limit=25`
    """
    # This endpoint would join with main athlete_rankings table
    # Implementation left as future enhancement
    raise HTTPException(
        status_code=501,
        detail="Endpoint not yet implemented - coming soon"
    )
