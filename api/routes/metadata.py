"""
XCRI Rankings API - Metadata Routes

FastAPI routes for calculation metadata endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status

from models import (
    MetadataListResponse,
    CalculationMetadata,
    ErrorResponse
)
from services import metadata_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
    responses={
        404: {"model": ErrorResponse, "description": "Metadata not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=MetadataListResponse,
    summary="List calculation metadata",
    description="""
    Get list of calculation metadata records with optional filters.

    Returns information about each calculation run including:
    - Processing time
    - Athletes/teams ranked
    - Cache performance
    - Data quality metrics

    **Example:**
    ```
    GET /metadata?season_year=2024
    ```
    """
)
async def list_metadata(
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
    scoring_group: Optional[str] = Query(
        default=None,
        description="Scoring scope (division, region_XX, conference_XX)"
    ),
    checkpoint_date: Optional[str] = Query(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for full season"
    ),
    algorithm_type: Optional[str] = Query(
        default=None,
        description="Algorithm type (light or heavy)"
    )
):
    """List calculation metadata records"""
    try:
        results = metadata_service.get_metadata(
            season_year=season_year,
            division=division,
            gender=gender,
            scoring_group=scoring_group,
            checkpoint_date=checkpoint_date,
            algorithm_type=algorithm_type
        )

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error listing metadata: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metadata: {str(e)}"
        )


@router.get(
    "/latest",
    response_model=MetadataListResponse,
    summary="Get latest calculations",
    description="""
    Get the most recent calculation metadata for each division/gender combination.

    Returns one record per division/gender (typically 6 records: D1/D2/D3 x Men/Women).

    **Example:**
    ```
    GET /metadata/latest
    ```
    """
)
async def get_latest_metadata():
    """Get latest calculation metadata for each division/gender"""
    try:
        results = metadata_service.get_latest_metadata()

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error getting latest metadata: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest metadata: {str(e)}"
        )


@router.get(
    "/{metadata_id}",
    response_model=CalculationMetadata,
    summary="Get metadata by ID",
    description="""
    Get a single metadata record by its ID.

    **Example:**
    ```
    GET /metadata/1
    ```
    """
)
async def get_metadata_by_id(metadata_id: int):
    """Get single metadata record by ID"""
    try:
        result = metadata_service.get_metadata_by_id(metadata_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata record {metadata_id} not found"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata {metadata_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metadata: {str(e)}"
        )


@router.get(
    "/summary/processing",
    summary="Get processing summary",
    description="""
    Get aggregate processing statistics across all calculations.

    Returns summary including:
    - Total calculations performed
    - Average processing time
    - Average cache hit rate
    - Total athletes/teams ranked

    **Example:**
    ```
    GET /metadata/summary/processing
    ```
    """
)
async def get_processing_summary():
    """Get aggregate processing statistics"""
    try:
        result = metadata_service.get_processing_summary()

        if not result:
            return {
                "message": "No processing data available"
            }

        return result

    except Exception as e:
        logger.error(f"Error getting processing summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve processing summary: {str(e)}"
        )
