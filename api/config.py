"""
XCRI Rankings API - Configuration Management

Loads configuration from environment variables or .env file.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """API Settings loaded from environment variables or .env file"""

    # ===================================================================
    # Database Configuration
    # ===================================================================

    database_host: str = Field(default="localhost", description="Database host")
    database_port: int = Field(default=3306, description="Database port")
    database_name: str = Field(default="web4ustfccca_iz", description="Database name")
    database_user: str = Field(default="web4ustfccca_public", description="Database username")
    database_password: str = Field(description="Database password")

    # ===================================================================
    # API Configuration
    # ===================================================================

    api_title: str = Field(default="XCRI Rankings API", description="API title")
    api_description: str = Field(
        default="Display-only API for USTFCCCA Cross Country Running Index rankings",
        description="API description"
    )
    api_version: str = Field(default="2.0.0", description="API version")

    api_host: str = Field(default="127.0.0.1", description="API host to bind")
    api_port: int = Field(default=8001, description="API port")
    api_cors_origins: str = Field(
        default="https://web4.ustfccca.org",
        description="Comma-separated list of allowed CORS origins"
    )

    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment name")

    # ===================================================================
    # Application Configuration
    # ===================================================================

    snapshot_dir: str = Field(
        default="/home/web4ustfccca/izzypy_xcri/data/exports",
        description="Directory containing historical snapshot Excel files"
    )

    # ===================================================================
    # Query Defaults
    # ===================================================================

    default_season_year: int = Field(default=2025, description="Default season year")
    default_limit: int = Field(default=100, description="Default pagination limit")
    max_limit: int = Field(default=50000, description="Maximum pagination limit")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        if self.api_cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    class Config:
        """Pydantic settings configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow extra fields in .env without validation errors
        extra = "ignore"


# Global settings instance
settings = Settings()
