"""
XCRI Rankings API - Configuration Management

Loads configuration from environment variables or .env file.
Supports both config file and individual database credentials.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    API Settings loaded from environment variables or .env file.

    Database connection can be configured via:
    1. Config file path (XCRI_DB_CONFIG_PATH) - recommended
    2. Individual environment variables (XCRI_DB_HOST, etc.)
    """

    # ===================================================================
    # Database Configuration
    # ===================================================================

    # Option 1: Config file path (uses existing database_connection.py)
    xcri_db_config_path: Optional[str] = Field(
        default=None,
        description="Path to MySQL config file (.ini or .cnf)"
    )

    # Option 2: Individual database credentials
    xcri_db_host: str = Field(default="web4.ustfccca.org", description="Database host")
    xcri_db_port: int = Field(default=3306, description="Database port")
    xcri_db_user: Optional[str] = Field(default=None, description="Database username")
    xcri_db_password: Optional[str] = Field(default=None, description="Database password")
    xcri_db_name: str = Field(default="ustfccca_v3", description="Database name")
    xcri_db_charset: str = Field(default="utf8mb4", description="Character set")

    # ===================================================================
    # API Configuration
    # ===================================================================

    api_host: str = Field(default="0.0.0.0", description="API host to bind")
    api_port: int = Field(default=8000, description="API port")
    api_title: str = Field(default="XCRI Rankings API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_description: str = Field(
        default="REST API for NCAA Cross Country Rankings (XCRI)",
        description="API description"
    )

    # ===================================================================
    # CORS Configuration
    # ===================================================================

    api_cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins (* for all)"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        if self.api_cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    # ===================================================================
    # Query Defaults
    # ===================================================================

    default_season_year: int = Field(default=2024, description="Default season year")
    default_limit: int = Field(default=100, description="Default pagination limit", ge=1)
    max_limit: int = Field(default=50000, description="Maximum pagination limit", ge=1)

    class Config:
        """Pydantic settings configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_database_config_path() -> Optional[str]:
    """
    Get the database config file path.

    Checks in order:
    1. XCRI_DB_CONFIG_PATH environment variable
    2. Default location: ~/.mysql/web4.ini
    3. Alternative: ~/.mysql/web4.cnf

    Returns:
        Path to config file if exists, None otherwise
    """
    # Check environment variable
    if settings.xcri_db_config_path:
        if os.path.exists(settings.xcri_db_config_path):
            return settings.xcri_db_config_path

    # Check default locations
    home = os.path.expanduser("~")
    default_paths = [
        os.path.join(home, ".mysql", "web4.ini"),
        os.path.join(home, ".mysql", "web4.cnf"),
    ]

    for path in default_paths:
        if os.path.exists(path):
            return path

    return None


def validate_settings():
    """
    Validate that we have sufficient database configuration.

    Raises:
        ValueError: If neither config file nor credentials are provided
    """
    config_path = get_database_config_path()

    # Check if we have config file
    if config_path:
        return True

    # Check if we have individual credentials
    if settings.xcri_db_user and settings.xcri_db_password:
        return True

    raise ValueError(
        "Database configuration not found. Please provide either:\n"
        "1. XCRI_DB_CONFIG_PATH pointing to a .ini/.cnf file, or\n"
        "2. Individual credentials: XCRI_DB_USER, XCRI_DB_PASSWORD, XCRI_DB_NAME"
    )
