"""
XCRI Rankings API - Snapshot Routes

FastAPI routes for historical snapshot endpoints.
Reads data from Excel files in data/weekly_rankings/ directory.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status

from models import ErrorResponse
from services.snapshot_service import snapshot_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"],
    responses={
        404: {"model": ErrorResponse, "description": "Snapshot not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/",
    summary="List all available snapshots",
    description="""
    Get list of all available historical snapshot dates.

    **Returns:**
    - List of snapshots with date, season, and display name
    - Sorted by date (most recent first)

    **Example:**
    ```
    GET /snapshots/
    ```
    """
)
async def list_snapshots():
    """List all available snapshot dates"""
    try:
        snapshots = await snapshot_service.list_snapshots()
        return {
            "total": len(snapshots),
            "snapshots": snapshots
        }
    except Exception as e:
        logger.error(f"Error listing snapshots: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list snapshots: {str(e)}"
        )


@router.get(
    "/{snapshot_date}/athletes",
    summary="Get athlete rankings from snapshot",
    description="""
    Get athlete rankings from a specific historical snapshot.

    **Path Parameters:**
    - snapshot_date: Date in YYYY-MM-DD format (e.g., 2024-11-25)

    **Query Parameters:**
    - division: Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA, 19781=NJCAA D1, 19782=NJCAA D2, 2034=NJCAA D3)
    - gender: Gender code (M or F)
    - limit: Results per page (default: 25, max: 500)
    - offset: Pagination offset
    - search: Search by athlete name or school name

    **Example:**
    ```
    GET /snapshots/2024-11-25/athletes?division=2030&gender=M&limit=25
    ```
    """
)
async def get_snapshot_athletes(
    snapshot_date: str,
    division: int = Query(
        ...,
        description="Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA, 19781=NJCAA D1, 19782=NJCAA D2, 2034=NJCAA D3)"
    ),
    gender: str = Query(
        ...,
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
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by athlete name or school name",
        min_length=2
    )
):
    """Get athlete rankings from a specific snapshot"""
    try:
        results, total = await snapshot_service.get_snapshot_athletes(
            snapshot_date=snapshot_date,
            division=division,
            gender=gender.upper(),
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
        logger.error(f"Error getting snapshot athletes for {snapshot_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve snapshot athletes: {str(e)}"
        )


@router.get(
    "/{snapshot_date}/teams",
    summary="Get team rankings from snapshot",
    description="""
    Get team rankings from a specific historical snapshot.

    **Path Parameters:**
    - snapshot_date: Date in YYYY-MM-DD format (e.g., 2024-11-25)

    **Query Parameters:**
    - division: Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA, 19781=NJCAA D1, 19782=NJCAA D2, 2034=NJCAA D3)
    - gender: Gender code (M or F)
    - limit: Results per page (default: 25, max: 500)
    - offset: Pagination offset
    - search: Search by team name

    **Example:**
    ```
    GET /snapshots/2024-11-25/teams?division=2030&gender=M&limit=25
    ```
    """
)
async def get_snapshot_teams(
    snapshot_date: str,
    division: int = Query(
        ...,
        description="Division code"
    ),
    gender: str = Query(
        ...,
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
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by team name",
        min_length=2
    )
):
    """Get team rankings from a specific snapshot"""
    try:
        results, total = await snapshot_service.get_snapshot_teams(
            snapshot_date=snapshot_date,
            division=division,
            gender=gender.upper(),
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
        logger.error(f"Error getting snapshot teams for {snapshot_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve snapshot teams: {str(e)}"
        )


@router.get(
    "/{snapshot_date}/metadata",
    summary="Get snapshot metadata",
    description="""
    Get metadata for a specific historical snapshot.

    **Path Parameters:**
    - snapshot_date: Date in YYYY-MM-DD format (e.g., 2024-11-25)

    **Returns:**
    - Snapshot date and season
    - List of available divisions/genders
    - Total number of files
    - Status

    **Example:**
    ```
    GET /snapshots/2024-11-25/metadata
    ```
    """
)
async def get_snapshot_metadata(snapshot_date: str):
    """Get metadata for a specific snapshot"""
    try:
        metadata = await snapshot_service.get_snapshot_metadata(snapshot_date)

        if metadata["status"] == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Snapshot {snapshot_date} not found"
            )

        return metadata

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting snapshot metadata for {snapshot_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve snapshot metadata: {str(e)}"
        )
