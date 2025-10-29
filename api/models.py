"""
XCRI Rankings API - Pydantic Models

Request and response models for API validation and documentation.
Models match the database schema from iz_rankings_xcri_* tables.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ===================================================================
# Request Models (Query Parameters)
# ===================================================================

class AthleteQueryParams(BaseModel):
    """Query parameters for athlete rankings endpoint"""
    season_year: int = Field(default=2024, description="Season year")
    division: Optional[int] = Field(
        default=None,
        description="Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)"
    )
    gender: Optional[str] = Field(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    )
    scoring_group: str = Field(
        default="division",
        description="Scoring scope (division, region_XX, conference_XX)"
    )
    checkpoint_date: Optional[str] = Field(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for full season"
    )
    algorithm_type: str = Field(
        default="light",
        description="Algorithm type (light or heavy)"
    )
    limit: int = Field(default=100, ge=1, le=50000, description="Results per page")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
    search: Optional[str] = Field(
        default=None,
        description="Search by athlete name or school name"
    )
    min_races: Optional[int] = Field(
        default=None,
        ge=1,
        description="Minimum number of races"
    )
    region: Optional[str] = Field(
        default=None,
        description="Filter by region name"
    )
    conference: Optional[str] = Field(
        default=None,
        description="Filter by conference name"
    )


class TeamQueryParams(BaseModel):
    """Query parameters for team rankings endpoint"""
    season_year: int = Field(default=2024, description="Season year")
    division: Optional[int] = Field(
        default=None,
        description="Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)"
    )
    gender: Optional[str] = Field(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    )
    scoring_group: str = Field(
        default="division",
        description="Scoring scope (division, region_XX, conference_XX)"
    )
    checkpoint_date: Optional[str] = Field(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for full season"
    )
    algorithm_type: str = Field(
        default="light",
        description="Algorithm type (light or heavy)"
    )
    limit: int = Field(default=100, ge=1, le=50000, description="Results per page")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
    search: Optional[str] = Field(
        default=None,
        description="Search by school name"
    )
    region: Optional[str] = Field(
        default=None,
        description="Filter by region name"
    )
    conference: Optional[str] = Field(
        default=None,
        description="Filter by conference name"
    )


class MetadataQueryParams(BaseModel):
    """Query parameters for metadata endpoint"""
    season_year: int = Field(default=2024, description="Season year")
    division: Optional[int] = Field(
        default=None,
        description="Division code (2030=D1, 2031=D2, 2032=D3, 2028=NAIA)"
    )
    gender: Optional[str] = Field(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    )
    scoring_group: Optional[str] = Field(
        default=None,
        description="Scoring scope (division, region_XX, conference_XX)"
    )
    checkpoint_date: Optional[str] = Field(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for full season"
    )
    algorithm_type: Optional[str] = Field(
        default=None,
        description="Algorithm type (light or heavy)"
    )


# ===================================================================
# Response Models (Database Records)
# ===================================================================

class AthleteRanking(BaseModel):
    """
    Athlete ranking record from iz_rankings_xcri_athlete_rankings table.

    Includes ranking, performance stats, head-to-head records, and quality metrics.
    """
    ranking_id: int = Field(description="Primary key")

    # Context
    season_year: int = Field(description="Season year (e.g., 2024)")
    division_code: int = Field(description="Division code (2030=D1, 2031=D2, 2032=D3)")
    gender_code: str = Field(description="Gender: M or F")
    checkpoint_date: Optional[str] = Field(default=None, description="Rankings as of date")
    algorithm_type: str = Field(description="Algorithm used: light, heavy")
    scoring_group: str = Field(description="Scoring scope: division, region_XX, etc.")

    # Athlete identifiers
    anet_athlete_hnd: int = Field(description="AthleticNet athlete handle")
    athlete_name_first: Optional[str] = Field(description="Athlete first name")
    athlete_name_last: Optional[str] = Field(description="Athlete last name")

    # Team identifiers
    anet_team_hnd: int = Field(description="AthleticNet team handle")
    team_name: Optional[str] = Field(description="Team/school name")
    team_group_fk: Optional[int] = Field(description="Team group foreign key")

    # Geographic identifiers (Session 009B)
    regl_group_name: Optional[str] = Field(default=None, description="Region name (e.g., West, Southeast)")
    conf_group_name: Optional[str] = Field(default=None, description="Conference name (e.g., Big Ten, ACC)")

    # Ranking data
    athlete_rank: int = Field(description="Athlete rank (1 = best)")
    xcri_score: Optional[float] = Field(description="XCRI score")

    # Performance statistics
    races_count: Optional[int] = Field(description="Number of races")
    season_average: Optional[float] = Field(description="Season average per-km pace")
    best_performance: Optional[float] = Field(description="Best performance")
    most_recent_race_date: Optional[date] = Field(default=None, description="Most recent race date (YYYY-MM-DD)")

    # Head-to-head statistics
    h2h_wins: int = Field(default=0, description="Head-to-head wins")
    h2h_losses: int = Field(default=0, description="Head-to-head losses")
    h2h_meetings: int = Field(default=0, description="Total H2H meetings")
    h2h_win_rate: Optional[float] = Field(description="Win rate (0.0-1.0)")

    # Quality metrics
    min_opponent_quality: Optional[float] = Field(description="Minimum opponent quality")
    avg_opponent_quality: Optional[float] = Field(description="Average opponent quality")

    # Season Composite Score (SCS) - Session 044
    scs_score: Optional[float] = Field(default=None, description="Season Composite Score (Heavy XCRI)")
    scs_rank: Optional[int] = Field(default=None, description="Rank by SCS score")

    # SCS Component Scores - Frontend Session 003
    saga_score: Optional[float] = Field(default=None, description="SAGA component score")
    saga_rank: Optional[int] = Field(default=None, description="Rank by SAGA score")
    sewr_score: Optional[float] = Field(default=None, description="SEWR component score")
    sewr_rank: Optional[int] = Field(default=None, description="Rank by SEWR score")
    osma_score: Optional[float] = Field(default=None, description="OSMA component score")
    osma_rank: Optional[int] = Field(default=None, description="Rank by OSMA score")

    # Metadata
    calculated_at: datetime = Field(description="When this ranking was calculated")
    algorithm_version: Optional[str] = Field(description="Algorithm version")
    processing_time_seconds: Optional[float] = Field(description="Processing time")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ranking_id": 1,
                "season_year": 2024,
                "division_code": 2030,
                "gender_code": "M",
                "checkpoint_date": None,
                "algorithm_type": "light",
                "scoring_group": "division",
                "anet_athlete_hnd": 12345,
                "athlete_name_first": "John",
                "athlete_name_last": "Doe",
                "anet_team_hnd": 678,
                "team_name": "University of Example",
                "team_group_fk": 100,
                "athlete_rank": 1,
                "xcri_score": 245.67,
                "races_count": 8,
                "season_average": 248.5,
                "best_performance": 242.1,
                "h2h_wins": 42,
                "h2h_losses": 3,
                "h2h_meetings": 45,
                "h2h_win_rate": 0.9333,
                "min_opponent_quality": 250.0,
                "avg_opponent_quality": 265.5,
                "calculated_at": "2024-10-12T10:00:00",
                "algorithm_version": "light_v1",
                "processing_time_seconds": 3.14
            }
        }


class TeamRanking(BaseModel):
    """
    Team ranking record from iz_rankings_xcri_team_rankings table.

    Includes team rank, squad statistics, and top athlete IDs.
    """
    ranking_id: int = Field(description="Primary key")

    # Context
    season_year: int = Field(description="Season year (e.g., 2024)")
    division_code: int = Field(description="Division code (2030=D1, 2031=D2, 2032=D3)")
    gender_code: str = Field(description="Gender: M or F")
    checkpoint_date: Optional[str] = Field(default=None, description="Rankings as of date")
    algorithm_type: str = Field(description="Algorithm used: light, heavy")
    scoring_group: str = Field(description="Scoring scope: division, region_XX, etc.")

    # Team identifiers
    anet_team_hnd: int = Field(description="AthleticNet team handle")
    team_name: Optional[str] = Field(description="Team/school name")
    team_group_fk: Optional[int] = Field(description="Team group foreign key")

    # Geographic identifiers (Session 009B)
    regl_group_name: Optional[str] = Field(default=None, description="Region name (e.g., West, Southeast)")
    conf_group_name: Optional[str] = Field(default=None, description="Conference name (e.g., Big Ten, ACC)")

    # Ranking data
    team_rank: int = Field(description="Team rank (1 = best)")
    team_xcri_score: Optional[float] = Field(description="Team XCRI score")
    most_recent_race_date: Optional[date] = Field(default=None, description="Most recent race date among top athletes")

    # Squad statistics
    athletes_count: Optional[int] = Field(description="Total athletes on roster")
    top7_average: Optional[float] = Field(description="Average XCRI of top 7")
    top5_average: Optional[float] = Field(description="Average XCRI of top 5")
    squad_depth_score: Optional[float] = Field(description="Squad depth metric")

    # Top athletes (for quick roster access)
    top_athlete_1_hnd: Optional[int] = Field(description="Top athlete #1 handle")
    top_athlete_2_hnd: Optional[int] = Field(description="Top athlete #2 handle")
    top_athlete_3_hnd: Optional[int] = Field(description="Top athlete #3 handle")
    top_athlete_4_hnd: Optional[int] = Field(description="Top athlete #4 handle")
    top_athlete_5_hnd: Optional[int] = Field(description="Top athlete #5 handle")
    top_athlete_6_hnd: Optional[int] = Field(description="Top athlete #6 handle")
    top_athlete_7_hnd: Optional[int] = Field(description="Top athlete #7 handle")

    # Metadata
    calculated_at: datetime = Field(description="When this ranking was calculated")
    algorithm_version: Optional[str] = Field(description="Algorithm version")

    class Config:
        from_attributes = True


class CalculationMetadata(BaseModel):
    """
    Calculation metadata record from iz_rankings_xcri_calculation_metadata table.

    Contains processing information and performance metrics for each calculation run.
    """
    metadata_id: int = Field(description="Primary key")

    # Context
    season_year: int = Field(description="Season year (e.g., 2024)")
    division_code: int = Field(description="Division code (2030=D1, 2031=D2, 2032=D3)")
    gender_code: str = Field(description="Gender: M or F")
    checkpoint_date: Optional[str] = Field(default=None, description="Rankings as of date")
    algorithm_type: Optional[str] = Field(description="Algorithm used: light, heavy")
    scoring_group: str = Field(description="Scoring scope: division, region_XX, etc.")

    # Processing info
    calculated_at: datetime = Field(description="When calculation completed")
    algorithm_version: Optional[str] = Field(description="Algorithm version")

    # Performance metrics
    total_performances: Optional[int] = Field(description="Total performance records")
    total_athletes: Optional[int] = Field(description="Total athletes ranked")
    total_teams: Optional[int] = Field(description="Total teams ranked")
    total_races: Optional[int] = Field(description="Total unique races")
    processing_time_seconds: Optional[float] = Field(description="Processing time")
    cache_used: bool = Field(default=False, description="Whether cache was used")
    cache_hit_rate: Optional[float] = Field(description="Cache hit rate (0.0-1.0)")

    # Data quality indicators
    athletes_with_h2h: Optional[int] = Field(description="Athletes with H2H data")
    athletes_no_h2h: Optional[int] = Field(description="Athletes without H2H data")
    heavy_fallback_count: Optional[int] = Field(description="Heavy XCRI fallback count")

    # Success indicators
    calculation_status: str = Field(default="success", description="Status: success, partial, failed")
    error_message: Optional[str] = Field(description="Error message if failed")

    class Config:
        from_attributes = True


# ===================================================================
# List Response Models (with Pagination)
# ===================================================================

class AthleteListResponse(BaseModel):
    """Paginated list of athlete rankings"""
    total: int = Field(description="Total number of results")
    limit: int = Field(description="Results per page")
    offset: int = Field(description="Pagination offset")
    results: List[AthleteRanking] = Field(description="List of athlete rankings")


class TeamListResponse(BaseModel):
    """Paginated list of team rankings"""
    total: int = Field(description="Total number of results")
    limit: int = Field(description="Results per page")
    offset: int = Field(description="Pagination offset")
    results: List[TeamRanking] = Field(description="List of team rankings")


class MetadataListResponse(BaseModel):
    """List of calculation metadata records"""
    total: int = Field(description="Total number of results")
    results: List[CalculationMetadata] = Field(description="List of metadata records")


# ===================================================================
# Utility Response Models
# ===================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="API status: healthy, degraded, unhealthy")
    api_version: str = Field(description="API version")
    database_connected: bool = Field(description="Database connection status")
    database_tables: Optional[dict] = Field(description="Table record counts")
    timestamp: datetime = Field(description="Current server time")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")


# ===================================================================
# SCS Component Models (Session 046)
# ===================================================================

class SCSComponents(BaseModel):
    """
    Detailed SCS component breakdown for an athlete.

    Includes all component scores (SAGA, SEWR, OSMA, XCRI) with ranks
    and supporting metrics.
    """
    component_id: int = Field(description="Primary key")
    ranking_id: int = Field(description="Link to main athlete ranking")

    # Identifiers
    season_year: int = Field(description="Season year")
    division_code: int = Field(description="Division code")
    gender_code: str = Field(description="Gender (M/F)")
    anet_athlete_hnd: int = Field(description="AthleticNet athlete handle")

    # Athlete info
    athlete_name_first: Optional[str] = Field(description="First name")
    athlete_name_last: Optional[str] = Field(description="Last name")
    team_name: Optional[str] = Field(description="Team/school name")

    # Component scores and ranks
    saga_score: Optional[float] = Field(description="Season Adjusted Gap Average")
    saga_rank: Optional[int] = Field(description="SAGA ranking")

    sewr_score: Optional[float] = Field(description="Season Equal-Weight Rating")
    sewr_rank: Optional[int] = Field(description="SEWR ranking")

    osma_score: Optional[float] = Field(description="Opponent SEWR Moving Average")
    osma_rank: Optional[int] = Field(description="OSMA ranking")

    xcri_score: Optional[float] = Field(description="Final SCS composite score")
    xcri_rank: Optional[int] = Field(description="SCS ranking")

    # Supporting metrics
    races_used: Optional[int] = Field(description="Number of races in calculation")
    best_ags: Optional[float] = Field(description="Best Adjusted Gap Score")
    avg_ags: Optional[float] = Field(description="Average Adjusted Gap Score")
    worst_ags: Optional[float] = Field(description="Worst Adjusted Gap Score")

    best_cpr: Optional[float] = Field(description="Best Contest Performance Rating")
    avg_cpr: Optional[float] = Field(description="Average CPR")
    worst_cpr: Optional[float] = Field(description="Worst CPR")

    avg_race_quality: Optional[float] = Field(description="Average race quality")
    best_race_quality: Optional[float] = Field(description="Best race quality")
    avg_opponent_count: Optional[float] = Field(description="Avg opponents per race")
    total_opponents: Optional[int] = Field(description="Total unique opponents")

    created_at: datetime = Field(description="Record creation time")
    updated_at: datetime = Field(description="Last update time")

    class Config:
        from_attributes = True


class SCSComponentLeaderboard(BaseModel):
    """Leaderboard of athletes ranked by specific SCS component"""
    component: str = Field(description="Component name (SAGA, SEWR, OSMA, XCRI)")
    season_year: int = Field(description="Season year")
    division_code: int = Field(description="Division code")
    gender_code: str = Field(description="Gender (M/F)")
    total_athletes: int = Field(description="Total athletes with this component")
    limit: int = Field(description="Results returned")
    results: List[dict] = Field(description="Top athletes by component")


class SCSComponentComparison(BaseModel):
    """
    Athlete's SCS components with division context.

    Includes percentiles and contextual ranking information.
    """
    athlete_info: dict = Field(description="Athlete identifiers and basic info")
    components: dict = Field(description="Component scores, ranks, and percentiles")
    detail_metrics: dict = Field(description="AGS and CPR details")
    context: dict = Field(description="Division totals and context")


class SCSComponentDistribution(BaseModel):
    """Distribution statistics for an SCS component"""
    component: str = Field(description="Component name (SAGA, SEWR, OSMA, XCRI)")
    statistics: dict = Field(description="Min, max, mean, std, count")
    percentiles: dict = Field(description="25th, 50th, 75th percentiles")
    context: dict = Field(description="Season, division, gender context")


# ===================================================================
# Component Breakdown Models (Backend Session 003)
# ===================================================================

class ComponentBreakdown(BaseModel):
    """
    Detailed SCS component score breakdown for an athlete.

    From iz_rankings_xcri_scs_components table.
    Includes all four components (SAGA, SEWR, OSMA, XCRI) with ranks,
    plus AGS, CPR, and race quality metrics.
    """
    component_id: int = Field(description="Component record ID")
    ranking_id: int = Field(description="Foreign key to athlete ranking")

    # Context
    season_year: int = Field(description="Season year")
    division_code: int = Field(description="Division code")
    gender_code: str = Field(description="Gender: M or F")

    # Athlete identifiers
    anet_athlete_hnd: int = Field(description="AthleticNet athlete handle")
    athlete_name_first: str = Field(description="Athlete first name")
    athlete_name_last: str = Field(description="Athlete last name")
    team_name: str = Field(description="Team/school name")

    # Component scores (SAGA, SEWR, OSMA, XCRI)
    saga_score: Optional[float] = Field(description="SAGA - Season Adjusted Gap Average (lower is better)")
    saga_rank: Optional[int] = Field(description="Rank by SAGA score")
    sewr_score: Optional[float] = Field(description="SEWR - Season Equivalent Win Rate (higher is better)")
    sewr_rank: Optional[int] = Field(description="Rank by SEWR score")
    osma_score: Optional[float] = Field(description="OSMA - Opponent Season Meet Average (higher is better)")
    osma_rank: Optional[int] = Field(description="Rank by OSMA score")
    xcri_score: Optional[float] = Field(description="XCRI - Heavy XCRI composite (higher is better)")
    xcri_rank: Optional[int] = Field(description="Rank by XCRI score")

    # Additional detail metrics
    races_used: Optional[int] = Field(description="Number of races used in calculation")
    best_ags: Optional[float] = Field(description="Best Adjusted Gap Score")
    avg_ags: Optional[float] = Field(description="Average Adjusted Gap Score")
    worst_ags: Optional[float] = Field(description="Worst Adjusted Gap Score")
    best_cpr: Optional[float] = Field(description="Best Contest Performance Rating")
    avg_cpr: Optional[float] = Field(description="Average Contest Performance Rating")
    worst_cpr: Optional[float] = Field(description="Worst Contest Performance Rating")
    avg_race_quality: Optional[float] = Field(description="Average race quality rating")
    best_race_quality: Optional[float] = Field(description="Best race quality rating")
    avg_opponent_count: Optional[float] = Field(description="Average opponents per race")
    total_opponents: Optional[int] = Field(description="Total unique opponents")

    # Timestamps
    created_at: datetime = Field(description="Record creation time")
    updated_at: datetime = Field(description="Last update time")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "component_id": 1,
                "ranking_id": 100,
                "season_year": 2024,
                "division_code": 2030,
                "gender_code": "M",
                "anet_athlete_hnd": 19019918,
                "athlete_name_first": "Graham",
                "athlete_name_last": "Blanks",
                "team_name": "Harvard",
                "saga_score": 790.76,
                "saga_rank": 7,
                "sewr_score": 1039.09,
                "sewr_rank": 7,
                "osma_score": 1027.90,
                "osma_rank": 1,
                "xcri_score": 1026.82,
                "xcri_rank": 7,
                "races_used": 4,
                "best_ags": 160.5,
                "avg_ags": 165.3,
                "worst_ags": 170.2,
                "best_cpr": 1050.0,
                "avg_cpr": 1035.0,
                "worst_cpr": 1020.0,
                "avg_race_quality": 850.0,
                "best_race_quality": 900.0,
                "avg_opponent_count": 150.5,
                "total_opponents": 600
            }
        }


class ComponentLeaderboardItem(BaseModel):
    """Single athlete in component leaderboard results"""
    component_id: int = Field(description="Component record ID")
    ranking_id: int = Field(description="Foreign key to athlete ranking")
    season_year: int = Field(description="Season year")
    division_code: int = Field(description="Division code")
    gender_code: str = Field(description="Gender: M or F")
    anet_athlete_hnd: int = Field(description="AthleticNet athlete handle")
    athlete_name_first: str = Field(description="Athlete first name")
    athlete_name_last: str = Field(description="Athlete last name")
    team_name: str = Field(description="Team/school name")

    # Primary component being ranked by
    score: Optional[float] = Field(description="Score for the component being queried")
    rank: Optional[int] = Field(description="Rank for the component being queried")

    # All component scores for comparison
    saga_score: Optional[float] = Field(description="SAGA score")
    saga_rank: Optional[int] = Field(description="SAGA rank")
    sewr_score: Optional[float] = Field(description="SEWR score")
    sewr_rank: Optional[int] = Field(description="SEWR rank")
    osma_score: Optional[float] = Field(description="OSMA score")
    osma_rank: Optional[int] = Field(description="OSMA rank")
    xcri_score: Optional[float] = Field(description="XCRI score")
    xcri_rank: Optional[int] = Field(description="XCRI rank")

    races_used: Optional[int] = Field(description="Number of races used")

    class Config:
        from_attributes = True


class ComponentLeaderboardResponse(BaseModel):
    """Response for component leaderboard endpoint"""
    total: int = Field(description="Total athletes with this component")
    limit: int = Field(description="Results per page")
    offset: int = Field(description="Pagination offset")
    component: str = Field(description="Component name (saga, sewr, osma, or xcri)")
    results: List[ComponentLeaderboardItem] = Field(description="Top athletes by component")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 3981,
                "limit": 25,
                "offset": 0,
                "component": "saga",
                "results": [
                    {
                        "anet_athlete_hnd": 19019918,
                        "athlete_name_first": "Graham",
                        "athlete_name_last": "Blanks",
                        "team_name": "Harvard",
                        "score": 790.76,
                        "rank": 7,
                        "saga_score": 790.76,
                        "saga_rank": 7,
                        "sewr_score": 1039.09,
                        "sewr_rank": 7,
                        "osma_score": 1027.90,
                        "osma_rank": 1,
                        "xcri_score": 1026.82,
                        "xcri_rank": 7
                    }
                ]
            }
        }


# Session 004: Season Resume Models (Issue #15)
from datetime import datetime as dt

class SeasonResume(BaseModel):
    """Season resume for a team"""
    id: int = Field(description="Resume record ID")
    season_year: int = Field(description="Season year")
    group_fk: int = Field(description="USTFCCCA group ID")
    gender_fk: int = Field(description="Gender foreign key (1=M, 2=F)")
    sport_fk: int = Field(description="Sport foreign key (3=Cross Country)")
    season_html: str = Field(description="Season resume HTML content")
    created_at: Optional[dt] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[dt] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True
        json_encoders = {
            dt: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "id": 1234,
                "season_year": 2025,
                "group_fk": 567,
                "gender_fk": 1,
                "sport_fk": 3,
                "season_html": "<div class='season-resume'>...</div>",
                "created_at": "2025-10-15T12:00:00",
                "updated_at": "2025-10-20T15:30:00"
            }
        }


# ===================================================================
# Team Knockout Models (Session 015)
# ===================================================================

class TeamKnockoutQueryParams(BaseModel):
    """Query parameters for Team Knockout rankings endpoint"""
    season_year: int = Field(default=2025, description="Season year")
    rank_group_type: str = Field(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    )
    rank_group_fk: Optional[int] = Field(
        default=None,
        description="Ranking group ID (division_code for D, regl_group_fk for R, conf_group_fk for C)"
    )
    gender_code: Optional[str] = Field(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    )
    checkpoint_date: Optional[str] = Field(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE rankings"
    )
    limit: int = Field(default=100, ge=1, le=500, description="Results per page")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
    search: Optional[str] = Field(
        default=None,
        description="Search by team name"
    )


class MatchupQueryParams(BaseModel):
    """Query parameters for matchup endpoints"""
    season_year: int = Field(default=2025, description="Season year")
    rank_group_type: str = Field(
        default="D",
        description="Ranking group type (D=Division, R=Regional, C=Conference)",
        pattern="^[DRC]$"
    )
    rank_group_fk: Optional[int] = Field(
        default=None,
        description="Ranking group ID (division_code, regl_group_fk, or conf_group_fk)"
    )
    gender_code: Optional[str] = Field(
        default=None,
        description="Gender code (M or F)",
        pattern="^[MFmf]$"
    )
    checkpoint_date: Optional[str] = Field(
        default=None,
        description="Rankings as of date (YYYY-MM-DD), null for LIVE rankings"
    )
    limit: int = Field(default=50, ge=1, le=500, description="Results per page")
    offset: int = Field(default=0, ge=0, description="Pagination offset")


class TeamKnockoutRanking(BaseModel):
    """
    Team Knockout ranking record from iz_rankings_xcri_team_knockout table.

    H2H-based team rankings with flexible ranking contexts (Division, Regional, Conference).
    """
    # Primary key
    id: int = Field(description="Primary key")

    # Team identification
    team_id: int = Field(description="Team identifier (anet_team_hnd)")
    team_name: str = Field(description="Team display name")
    team_code: Optional[str] = Field(default=None, description="Team code/abbreviation")

    # Ranking context
    rank_group_type: str = Field(description="Ranking group type: D=Division, R=Regional, C=Conference")
    rank_group_fk: int = Field(description="Ranking group ID")
    gender_code: str = Field(description="Gender: M or F")

    # Regional/Conference context
    regl_group_fk: Optional[int] = Field(default=None, description="Regional group ID")
    conf_group_fk: Optional[int] = Field(default=None, description="Conference group ID")
    regl_finish: Optional[int] = Field(default=None, description="Regional championship finish")
    conf_finish: Optional[int] = Field(default=None, description="Conference championship finish")

    # Ranking data
    knockout_rank: int = Field(description="Team Knockout ranking (H2H-based, 1=best)")
    team_five_rank: Optional[int] = Field(default=None, description="Team Five aggregate rank (for comparison)")
    elimination_method: Optional[str] = Field(default=None, description="Tiebreaker method used")

    # Team statistics
    team_size: Optional[int] = Field(default=None, description="Total roster size")
    athletes_with_xcri: Optional[int] = Field(default=None, description="Number of athletes with XCRI scores")
    team_five_xcri_pts: Optional[float] = Field(default=None, description="SUM of top 5 athlete XCRI scores")

    # H2H statistics
    h2h_wins: Optional[int] = Field(default=None, description="Head-to-head wins in pool")
    h2h_losses: Optional[int] = Field(default=None, description="Head-to-head losses in pool")
    h2h_win_pct: Optional[float] = Field(default=None, description="Head-to-head win percentage")

    # Snapshot metadata
    checkpoint_date: Optional[str] = Field(default=None, description="Snapshot date (NULL = LIVE)")
    season_year: int = Field(description="Season year (2024, 2025, etc.)")
    calculation_date: datetime = Field(description="When this ranking was calculated")

    class Config:
        from_attributes = True


class TeamKnockoutMatchup(BaseModel):
    """
    Individual H2H matchup record from iz_rankings_xcri_team_knockout_matchups table.

    Stores head-to-head results between two teams at a specific meet.
    """
    # Primary key
    matchup_id: int = Field(description="Primary key")

    # Race/Meet information
    race_hnd: int = Field(description="AthleticNET race handle")
    race_date: date = Field(description="Date of the meet")
    meet_name: str = Field(description="Name of the meet")

    # Team A
    team_a_id: int = Field(description="Team A anet_team_hnd")
    team_a_name: Optional[str] = Field(default=None, description="Team A name (from join)")
    team_a_rank: int = Field(description="Team A finish place in race")
    team_a_score: int = Field(description="Team A XC scoring points")

    # Team B
    team_b_id: int = Field(description="Team B anet_team_hnd")
    team_b_name: Optional[str] = Field(default=None, description="Team B name (from join)")
    team_b_rank: int = Field(description="Team B finish place in race")
    team_b_score: int = Field(description="Team B XC scoring points")

    # Winner
    winner_team_id: int = Field(description="Winner anet_team_hnd")
    winner_team_name: Optional[str] = Field(default=None, description="Winner team name (from join)")

    # Ranking context
    season_year: int = Field(description="Season year")
    rank_group_type: str = Field(description="D=Division, R=Regional, C=Conference")
    rank_group_fk: int = Field(description="Group ID (division_code, etc.)")
    gender_code: str = Field(description="M or F")

    # Snapshot support
    checkpoint_date: Optional[str] = Field(default=None, description="Snapshot date (NULL = LIVE)")

    # Metadata
    calculation_date: datetime = Field(description="When this data was calculated")

    class Config:
        from_attributes = True


class MatchupStatsSummary(BaseModel):
    """
    Summary statistics for matchups (wins/losses).

    Used to provide quick statistics in list responses.
    """
    total_matchups: int = Field(description="Total number of matchups")
    wins: int = Field(description="Number of wins")
    losses: int = Field(description="Number of losses")
    win_pct: float = Field(description="Win percentage (0.0-100.0)")


class CommonOpponent(BaseModel):
    """
    Common opponent record showing how two teams performed against the same opponent.

    Used for common opponent analysis between two teams.
    """
    opponent_id: int = Field(description="Common opponent team ID")
    opponent_name: Optional[str] = Field(default=None, description="Common opponent team name")
    team_a_wins: int = Field(description="Team A wins vs this opponent")
    team_a_losses: int = Field(description="Team A losses vs this opponent")
    team_b_wins: int = Field(description="Team B wins vs this opponent")
    team_b_losses: int = Field(description="Team B losses vs this opponent")


class TeamKnockoutListResponse(BaseModel):
    """Paginated list of Team Knockout rankings"""
    total: int = Field(description="Total number of results")
    limit: int = Field(description="Results per page")
    offset: int = Field(description="Pagination offset")
    results: List[TeamKnockoutRanking] = Field(description="List of Team Knockout rankings")


class MatchupListResponse(BaseModel):
    """
    Paginated list of matchups with summary statistics.

    Includes win-loss record and list of individual matchups.
    """
    total: int = Field(description="Total number of matchups")
    limit: int = Field(description="Results per page")
    offset: int = Field(description="Pagination offset")
    stats: MatchupStatsSummary = Field(description="Win-loss summary statistics")
    matchups: List[TeamKnockoutMatchup] = Field(description="List of matchup records")


class HeadToHeadResponse(BaseModel):
    """
    Direct head-to-head comparison between two teams.

    Provides overall record and complete matchup history.
    """
    team_a_id: int = Field(description="Team A identifier")
    team_a_name: Optional[str] = Field(default=None, description="Team A name")
    team_b_id: int = Field(description="Team B identifier")
    team_b_name: Optional[str] = Field(default=None, description="Team B name")

    total_matchups: int = Field(description="Total matchups between these teams")
    team_a_wins: int = Field(description="Team A wins")
    team_b_wins: int = Field(description="Team B wins")

    # Latest matchup info
    latest_matchup_date: Optional[date] = Field(default=None, description="Date of most recent matchup")
    latest_winner_id: Optional[int] = Field(default=None, description="Winner of most recent matchup")

    # Complete history
    matchups: List[TeamKnockoutMatchup] = Field(description="Complete matchup history")


class MeetMatchupsResponse(BaseModel):
    """
    All matchups from a specific meet.

    Shows all head-to-head results from a particular race.
    """
    race_hnd: int = Field(description="AthleticNET race handle")
    meet_name: str = Field(description="Name of the meet")
    race_date: date = Field(description="Date of the race")
    total_matchups: int = Field(description="Total number of matchups at this meet")
    matchups: List[TeamKnockoutMatchup] = Field(description="List of matchup records")


class CommonOpponentsResponse(BaseModel):
    """
    Common opponent analysis between two teams.

    Shows how both teams performed against shared opponents.
    """
    team_a_id: int = Field(description="Team A identifier")
    team_a_name: Optional[str] = Field(default=None, description="Team A name")
    team_b_id: int = Field(description="Team B identifier")
    team_b_name: Optional[str] = Field(default=None, description="Team B name")

    total_common_opponents: int = Field(description="Number of common opponents")
    team_a_record_vs_common: str = Field(description="Team A record vs common opponents (e.g., '5-2')")
    team_b_record_vs_common: str = Field(description="Team B record vs common opponents (e.g., '4-3')")

    common_opponents: List[CommonOpponent] = Field(description="List of common opponents with records")
