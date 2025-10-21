"""
XCRI Rankings API - Main Application

FastAPI backend for NCAA Cross Country Rankings (XCRI).
Provides REST API access to athlete and team rankings from web4 database.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Documentation:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import validate_database_connection, get_table_counts
from models import HealthCheckResponse, ErrorResponse
from routes import athletes, teams, metadata, snapshots, scs, components, feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===================================================================
# Lifespan Event Handler
# ===================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Validate database connection
    - Check table record counts
    - Log configuration

    Shutdown:
    - Clean up resources
    """
    # Startup
    logger.info("=" * 60)
    logger.info("XCRI Rankings API - Starting Up")
    logger.info("=" * 60)
    logger.info(f"API Version: {settings.api_version}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")

    try:
        # Validate database connection
        validate_database_connection()
        logger.info("✓ Database connection validated")

    except Exception as e:
        logger.error(f"✗ Startup failed: {e}")
        raise

    logger.info("=" * 60)
    logger.info("XCRI Rankings API - Ready")
    logger.info("=" * 60)
    logger.info(f"Swagger UI: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"ReDoc: http://{settings.api_host}:{settings.api_port}/redoc")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("XCRI Rankings API - Shutting Down")


# ===================================================================
# FastAPI Application
# ===================================================================

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ===================================================================
# Middleware Configuration
# ===================================================================

# CORS - Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression - Reduce response sizes (Session 010)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Only compress responses > 1KB
)


# ===================================================================
# Exception Handlers
# ===================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.api_version != "1.0.0" else None
        }
    )


# ===================================================================
# Root Endpoints
# ===================================================================

@app.get(
    "/",
    response_model=HealthCheckResponse,
    summary="API root and health check",
    description="Get API information and health status",
    tags=["system"]
)
async def root():
    """
    API root endpoint with health check.

    Returns API version, status, and database connectivity.
    """
    try:
        # Test database connection
        table_counts = get_table_counts()
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        table_counts = None
        db_connected = False

    return {
        "status": "healthy" if db_connected else "degraded",
        "api_version": settings.api_version,
        "database_connected": db_connected,
        "database_tables": table_counts,
        "timestamp": datetime.now()
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Detailed health check",
    description="Comprehensive health check with database status",
    tags=["system"]
)
async def health_check():
    """
    Detailed health check endpoint.

    Returns comprehensive status including:
    - API version
    - Database connectivity
    - Table record counts
    - Current timestamp
    """
    try:
        # Test database and get table counts
        table_counts = get_table_counts()
        db_connected = True

        # Determine overall status
        if table_counts and all(count > 0 for count in table_counts.values()):
            health_status = "healthy"
        elif table_counts:
            health_status = "degraded"
        else:
            health_status = "unhealthy"

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        table_counts = None
        db_connected = False
        health_status = "unhealthy"

    return {
        "status": health_status,
        "api_version": settings.api_version,
        "database_connected": db_connected,
        "database_tables": table_counts,
        "timestamp": datetime.now()
    }


# ===================================================================
# Include Routers
# ===================================================================

app.include_router(athletes.router)
app.include_router(teams.router)
app.include_router(metadata.router)
app.include_router(snapshots.router)
app.include_router(scs.router)  # Frontend Session 004: SCS component endpoints
app.include_router(components.router)  # Backend Session 003: Component score API
app.include_router(feedback.router)  # User feedback submission (creates GitHub issues)


# ===================================================================
# Run Application (for development)
# ===================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting XCRI Rankings API...")
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
