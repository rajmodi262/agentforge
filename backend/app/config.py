"""StartupOS AI — Configuration (Pydantic Settings)

Includes startup validation and security checks.
"""

import os
import secrets
import logging
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache

logger = logging.getLogger(__name__)

_DEFAULT_JWT_SECRET = "dev-secret-change-in-production"


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://startupos:startupos_dev@localhost:5432/startupos_db"

    # Claude API
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Gemini API (fallback / alternative)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Groq API (fast Llama inference)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # AI Provider: "groq" | "claude" | "gemini" | "auto" (auto picks whichever key is available)
    ai_provider: str = "auto"

    # Mock Mode — CRITICAL for development
    mock_mode: bool = True

    # Brave Search
    brave_search_api_key: str = ""

    # JWT Auth
    jwt_secret_key: str = _DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # CORS
    frontend_url: str = "http://localhost:5173"

    # AWS (Phase 4)
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"

    # n8n Integration (400+ external integrations)
    n8n_base_url: str = ""
    n8n_api_key: str = ""

    # Redis (task queue + caching)
    redis_url: str = "redis://localhost:6379/0"
    s3_bucket_name: str = "startupos-reports"

    # Rate Limiting
    rate_limit_login: str = "10/minute"
    rate_limit_register: str = "5/minute"
    rate_limit_global: str = "100/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate_on_startup(self):
        """Run validation checks after settings are loaded.
        Called manually after settings are created.
        """
        warnings = []
        errors = []

        # JWT secret check
        if self.jwt_secret_key == _DEFAULT_JWT_SECRET:
            if not self.mock_mode:
                errors.append(
                    "JWT_SECRET_KEY is still the default! Set a secure value in .env for production."
                )
            else:
                # Auto-generate a secure secret for dev mode
                self.jwt_secret_key = secrets.token_urlsafe(32)
                warnings.append(
                    "JWT_SECRET_KEY was default — auto-generated a random secret for this session."
                )

        # API key checks
        if not self.mock_mode and not self.anthropic_api_key and not self.gemini_api_key and not self.groq_api_key:
            errors.append(
                "MOCK_MODE is false but no AI API key is set! Set GROQ_API_KEY, ANTHROPIC_API_KEY or GEMINI_API_KEY, or enable mock mode."
            )

        if not self.anthropic_api_key or self.anthropic_api_key.startswith("sk-ant-xxxx"):
            warnings.append("ANTHROPIC_API_KEY is not set — mock mode will be used for AI generation.")

        if not self.brave_search_api_key or self.brave_search_api_key.startswith("BSAxxxx"):
            warnings.append("BRAVE_SEARCH_API_KEY is not set — mock search results will be used.")

        # Log all issues
        for w in warnings:
            logger.warning(f"⚠ CONFIG: {w}")
        for e in errors:
            logger.error(f"✗ CONFIG: {e}")

        if errors and not self.mock_mode:
            raise ValueError(
                "Critical configuration errors found:\n" + "\n".join(f"  - {e}" for e in errors)
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_on_startup()
    return settings
