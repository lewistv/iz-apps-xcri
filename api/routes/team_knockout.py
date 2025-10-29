"""
Team Knockout API - Route Handlers

FastAPI routes for Team Knockout rankings and matchup endpoints.
Adapted from existing route patterns in iz-apps-clean/xcri/api/routes/

Created: Team Knockout Session 015
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status, Path

from models import (
    TeamKnockoutListResponse,
    TeamKnockoutRanking,
    MatchupListResponse,
    HeadToHeadResponse,
    MeetMatchupsResponse,
    CommonOpponentsResponse,
    ErrorResponse
)
from services import team_knockout_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/team-knockout",
    tags=["team-knockout"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ===================================================================
# Team Knockout Rankings Endpoints
# ===================================================================

@router.get(
    "/",
    response_model=TeamKnockoutListResponse,
    summary="List Team Knockout rankings",
    description="""
    Get paginated list of Team Knockout rankings (H2H-based) with optional filters.

    Team Knockout uses head-to-head matchup results to determine rankings, rather than
    aggregate scoring like Team Five.

    **Filters:**
    - rank_group_type: Ranking context (D=Division, R=Regional, C=Conference)
    - rank_group_fk: Specific group ID (division code, regional ID, or conference ID)
    - gender: Filter by gender (M or F)
    - checkpoint_date: Historical snapshot date (NULL for LIVE rankings)
    - search: Search by team name

    **Pagination:**
    - limit: Results per page (default: 100, max: 500)
    - offset: Number of results to skip

    **Example:**
    ```
    GET /team-knockout?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M&limit=25
    ```
    """
)
async def list_team_knockout_rankings(
    season_year: int = Query(
        default=2025,
        description="Season year"
    ),
    rank_group_type: str = Query(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    ),
    rank_group_fk: Optional[int] = Query(
        default=None,
        description="Ranking group ID (division_code, regl_group_fk, or conf_group_fk)"
    ),
    gender_code: Optional[str] = Query(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE rankings"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Results per page"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination offset"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by team name",
        min_length=2
    )
):
    """List Team Knockout rankings with filters and pagination"""
    try:
        results, total = await team_knockout_service.get_team_knockout_rankings(
            season_year=season_year,
            rank_group_type=rank_group_type,
            rank_group_fk=rank_group_fk,
            gender_code=gender_code,
            checkpoint_date=checkpoint_date,
            limit=limit,
            offset=offset,
            search=search
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"Error listing Team Knockout rankings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Team Knockout rankings: {str(e)}"
        )


# ===================================================================
# Matchup Endpoints
# ===================================================================

@router.get(
    "/matchups",
    response_model=MatchupListResponse,
    summary="Get team matchups",
    description="""
    Get all head-to-head matchups for a specific team with win-loss statistics.

    Returns paginated list of matchups showing opponent, scores, and results.
    Includes summary statistics: total matchups, wins, losses, and win percentage.

    **Required:**
    - team_id: Team identifier

    **Filters:**
    - rank_group_type: D=Division, R=Regional, C=Conference
    - rank_group_fk: Specific group ID
    - gender_code: M or F
    - checkpoint_date: Historical snapshot (NULL for LIVE)

    **Pagination:**
    - limit: Results per page (default: 50, max: 500)
    - offset: Number of results to skip

    **Example:**
    ```
    GET /team-knockout/matchups?team_id=20690&season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M
    ```
    """
)
async def get_team_matchups(
    team_id: int = Query(..., description="Team identifier (required)"),
    season_year: int = Query(default=2025, description="Season year"),
    rank_group_type: str = Query(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    ),
    rank_group_fk: Optional[int] = Query(
        default=None,
        description="Ranking group ID"
    ),
    gender_code: Optional[str] = Query(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Results per page"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination offset"
    )
):
    """Get all matchups for a specific team"""
    try:
        matchups, total, stats = await team_knockout_service.get_team_matchups(
            team_id=team_id,
            season_year=season_year,
            rank_group_type=rank_group_type,
            rank_group_fk=rank_group_fk,
            gender_code=gender_code,
            checkpoint_date=checkpoint_date,
            limit=limit,
            offset=offset
        )

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "stats": stats,
            "matchups": matchups
        }

    except Exception as e:
        logger.error(f"Error getting matchups for team_id={team_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve matchups: {str(e)}"
        )


@router.get(
    "/matchups/head-to-head",
    response_model=HeadToHeadResponse,
    summary="Get head-to-head record between two teams",
    description="""
    Get direct head-to-head comparison between two teams.

    Returns overall H2H record, most recent matchup info, and complete matchup history.

    **Required:**
    - team_a_id: First team identifier
    - team_b_id: Second team identifier

    **Filters:**
    - season_year: Season year
    - rank_group_type: D=Division, R=Regional, C=Conference
    - rank_group_fk: Specific group ID
    - gender_code: M or F
    - checkpoint_date: Historical snapshot

    **Example:**
    ```
    GET /team-knockout/matchups/head-to-head?team_a_id=20690&team_b_id=20710&season_year=2025
    ```
    """
)
async def get_head_to_head(
    team_a_id: int = Query(..., description="First team identifier (required)"),
    team_b_id: int = Query(..., description="Second team identifier (required)"),
    season_year: int = Query(default=2025, description="Season year"),
    rank_group_type: str = Query(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    ),
    rank_group_fk: Optional[int] = Query(
        default=None,
        description="Ranking group ID"
    ),
    gender_code: Optional[str] = Query(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE"
    )
):
    """Get head-to-head record between two teams"""
    try:
        if team_a_id == team_b_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="team_a_id and team_b_id must be different"
            )

        result = await team_knockout_service.get_head_to_head(
            team_a_id=team_a_id,
            team_b_id=team_b_id,
            season_year=season_year,
            rank_group_type=rank_group_type,
            rank_group_fk=rank_group_fk,
            gender_code=gender_code,
            checkpoint_date=checkpoint_date
        )

        if result['total_matchups'] == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No matchups found between team_a_id={team_a_id} and team_b_id={team_b_id}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting H2H for team_a_id={team_a_id} vs team_b_id={team_b_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve head-to-head record: {str(e)}"
        )


@router.get(
    "/matchups/meet/{race_hnd}",
    response_model=MeetMatchupsResponse,
    summary="Get all matchups from a specific meet",
    description="""
    Get all head-to-head matchup results from a particular race/meet.

    Returns meet information and all matchups that occurred at that meet,
    ordered by team finish place.

    **Example:**
    ```
    GET /team-knockout/matchups/meet/1064835?season_year=2025
    ```
    """
)
async def get_meet_matchups(
    race_hnd: int = Path(..., description="Race handle (AthleticNET race ID)"),
    season_year: int = Query(default=2025, description="Season year"),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE"
    )
):
    """Get all matchups from a specific meet"""
    try:
        result = await team_knockout_service.get_meet_matchups(
            race_hnd=race_hnd,
            season_year=season_year,
            checkpoint_date=checkpoint_date
        )

        if result['total_matchups'] == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No matchups found for race_hnd={race_hnd}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matchups for race_hnd={race_hnd}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve meet matchups: {str(e)}"
        )


@router.get(
    "/matchups/common-opponents",
    response_model=CommonOpponentsResponse,
    summary="Find common opponents between two teams",
    description="""
    Analyze how two teams performed against shared opponents.

    Useful for comparing teams that haven't faced each other directly.
    Returns list of common opponents with each team's record against them.

    **Required:**
    - team_a_id: First team identifier
    - team_b_id: Second team identifier

    **Filters:**
    - season_year: Season year
    - rank_group_type: D=Division, R=Regional, C=Conference
    - rank_group_fk: Specific group ID
    - gender_code: M or F
    - checkpoint_date: Historical snapshot

    **Example:**
    ```
    GET /team-knockout/matchups/common-opponents?team_a_id=20690&team_b_id=20710&season_year=2025
    ```
    """
)
async def get_common_opponents(
    team_a_id: int = Query(..., description="First team identifier (required)"),
    team_b_id: int = Query(..., description="Second team identifier (required)"),
    season_year: int = Query(default=2025, description="Season year"),
    rank_group_type: str = Query(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    ),
    rank_group_fk: Optional[int] = Query(
        default=None,
        description="Ranking group ID"
    ),
    gender_code: Optional[str] = Query(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE"
    )
):
    """Find common opponents between two teams"""
    try:
        if team_a_id == team_b_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="team_a_id and team_b_id must be different"
            )

        result = await team_knockout_service.get_common_opponents(
            team_a_id=team_a_id,
            team_b_id=team_b_id,
            season_year=season_year,
            rank_group_type=rank_group_type,
            rank_group_fk=rank_group_fk,
            gender_code=gender_code,
            checkpoint_date=checkpoint_date
        )

        if result['total_common_opponents'] == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No common opponents found between team_a_id={team_a_id} and team_b_id={team_b_id}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting common opponents for team_a_id={team_a_id} vs team_b_id={team_b_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve common opponents: {str(e)}"
        )


# ===================================================================
# Single Team Ranking Endpoint (MUST BE LAST - parameterized route)
# ===================================================================

@router.get(
    "/{team_id}",
    response_model=TeamKnockoutRanking,
    summary="Get Team Knockout ranking by team ID",
    description="""
    Get a single team's Team Knockout ranking by team identifier.

    Returns the team's H2H-based ranking with elimination method details.

    **Example:**
    ```
    GET /team-knockout/20690?season_year=2025&rank_group_type=D&rank_group_fk=2030&gender_code=M
    ```
    """
)
async def get_team_knockout_ranking(
    team_id: int = Path(..., description="Team identifier (anet_team_hnd)"),
    season_year: int = Query(default=2025, description="Season year"),
    rank_group_type: str = Query(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    ),
    rank_group_fk: Optional[int] = Query(
        default=None,
        description="Ranking group ID (optional, for disambiguation)"
    ),
    gender_code: Optional[str] = Query(
        default=None,
        description="Gender code (optional, for disambiguation)",
        pattern="^[MFmf]$"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE"
    )
):
    """Get single Team Knockout ranking by team ID"""
    try:
        result = await team_knockout_service.get_team_knockout_by_id(
            team_id=team_id,
            season_year=season_year,
            rank_group_type=rank_group_type,
            rank_group_fk=rank_group_fk,
            gender_code=gender_code,
            checkpoint_date=checkpoint_date
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team Knockout ranking not found for team_id={team_id}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Team Knockout ranking for team_id={team_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Team Knockout ranking: {str(e)}"
        )
