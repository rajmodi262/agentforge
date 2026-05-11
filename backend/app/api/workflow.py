"""StartupOS AI — Workflow API (Status + Results)"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User, WorkflowRun, AgentTask, AgentMessage
from app.models.response_schemas import WorkflowDetailResponse, WorkflowResponse, AgentTaskResponse, AgentMessageResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
def get_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get workflow status with all agent tasks and messages."""
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Verify ownership
    if workflow.project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    agent_tasks = db.query(AgentTask).filter(
        AgentTask.workflow_id == workflow_id
    ).order_by(AgentTask.started_at).all()

    agent_messages = db.query(AgentMessage).filter(
        AgentMessage.workflow_id == workflow_id
    ).order_by(AgentMessage.created_at).all()

    return WorkflowDetailResponse(
        workflow=workflow,
        agent_tasks=agent_tasks,
        agent_messages=agent_messages,
    )
