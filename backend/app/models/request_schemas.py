"""StartupOS AI — Pydantic Request Schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# --- Auth ---
class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    name: Optional[str] = Field(None, max_length=255)


class LoginRequest(BaseModel):
    email: str
    password: str


# --- Projects ---
class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    business_idea: str = Field(..., min_length=10, max_length=5000)
    target_market: Optional[str] = Field(None, max_length=255)
    budget_range: Optional[str] = Field(None, max_length=100)


class StartWorkflowRequest(BaseModel):
    """Optional overrides when starting a workflow."""
    use_mock: Optional[bool] = None  # Override global mock setting
