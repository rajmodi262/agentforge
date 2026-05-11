"""StartupOS AI — Pydantic Response Schemas"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


# --- Auth ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Projects ---
class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    business_idea: str
    target_market: Optional[str]
    budget_range: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int


# --- Workflow ---
class WorkflowResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_tokens: int
    total_cost: str
    error_message: Optional[str]

    class Config:
        from_attributes = True


class AgentTaskResponse(BaseModel):
    id: UUID
    agent_name: str
    status: str
    output_data: Optional[Any]
    tokens_used: int
    execution_time: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AgentMessageResponse(BaseModel):
    id: UUID
    sender: str
    recipient: str
    message_type: Optional[str]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowDetailResponse(BaseModel):
    workflow: WorkflowResponse
    agent_tasks: List[AgentTaskResponse]
    agent_messages: List[AgentMessageResponse]
