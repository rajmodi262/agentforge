"""StartupOS AI — Pydantic Request Schemas

Input validation with sanitization for all API endpoints.
"""

import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


# --- Auth ---
class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Projects ---
class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    business_idea: str = Field(..., min_length=10, max_length=5000)
    target_market: Optional[str] = Field(None, max_length=255)
    budget_range: Optional[str] = Field(None, max_length=100)

    @field_validator("business_idea")
    @classmethod
    def sanitize_business_idea(cls, v: str) -> str:
        """Strip potentially dangerous HTML/script content."""
        try:
            import bleach
            v = bleach.clean(v, tags=[], strip=True)
        except ImportError:
            # Fallback: strip basic HTML tags
            v = re.sub(r"<[^>]+>", "", v)
        return v.strip()

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        try:
            import bleach
            v = bleach.clean(v, tags=[], strip=True)
        except ImportError:
            v = re.sub(r"<[^>]+>", "", v)
        return v.strip()


class StartWorkflowRequest(BaseModel):
    """Optional overrides when starting a workflow."""
    use_mock: Optional[bool] = None  # Override global mock setting
