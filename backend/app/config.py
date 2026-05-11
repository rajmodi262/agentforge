"""StartupOS AI — Configuration (Pydantic Settings)"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://startupos:startupos_dev@localhost:5432/startupos_db"

    # Claude API
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Mock Mode — CRITICAL for development
    mock_mode: bool = True

    # Brave Search
    brave_search_api_key: str = ""

    # JWT Auth
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # CORS
    frontend_url: str = "http://localhost:5173"

    # AWS (Phase 4)
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    s3_bucket_name: str = "startupos-reports"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
