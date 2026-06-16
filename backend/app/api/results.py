"""AgentForge AI — Results API

Serves agent outputs for the Report viewer.
Uses soft-delete aware queries for data integrity.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, active_query
from app.models.db_models import Project, WorkflowRun, AgentTask
from app.api.auth import get_current_user, get_optional_user
from app.api.projects import _get_or_create_demo_user
from app.models.db_models import User

router = APIRouter()


@router.get("/{project_id}/results")
def get_project_results(
    project_id: UUID,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Get all agent outputs for a project's latest completed workflow.
    
    Returns a dict of {agent_key: output_data} for the Report viewer.
    """
    if current_user is None:
        current_user = _get_or_create_demo_user(db)

    project = active_query(db, Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get the latest workflow run
    workflow = db.query(WorkflowRun).filter(
        WorkflowRun.project_id == project_id,
    ).order_by(WorkflowRun.started_at.desc()).first()

    if not workflow:
        return {
            "status": "no_workflow",
            "message": "No workflow has been run yet",
            "agents": {},
        }

    # Get all agent tasks for this workflow
    agent_tasks = db.query(AgentTask).filter(
        AgentTask.workflow_id == workflow.id,
    ).order_by(AgentTask.started_at.asc()).all()

    # Build the results dict
    agents = {}
    for task in agent_tasks:
        # Derive key from agent name: "CEO Agent" → "ceo_output"
        key = task.agent_name.lower().replace(" agent", "").replace(" ", "_") + "_output"
        agents[key] = {
            "name": task.agent_name,
            "status": task.status,
            "output": task.output_data,
            "tokens_used": task.tokens_used,
            "execution_time": task.execution_time,
        }

    return {
        "status": workflow.status,
        "workflow_id": str(workflow.id),
        "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
        "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
        "total_tokens": workflow.total_tokens,
        "total_cost": workflow.total_cost,
        "agents": agents,
    }


@router.get("/{project_id}/status")
def get_workflow_status(
    project_id: UUID,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Get real-time workflow progress for a project."""
    if current_user is None:
        current_user = _get_or_create_demo_user(db)

    project = active_query(db, Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    workflow = db.query(WorkflowRun).filter(
        WorkflowRun.project_id == project_id,
    ).order_by(WorkflowRun.started_at.desc()).first()

    if not workflow:
        return {"status": "no_workflow", "progress": 0, "current_agent": None}

    # Count completed agents
    completed = db.query(AgentTask).filter(
        AgentTask.workflow_id == workflow.id,
        AgentTask.status == "completed",
    ).count()

    running = db.query(AgentTask).filter(
        AgentTask.workflow_id == workflow.id,
        AgentTask.status == "running",
    ).first()

    return {
        "status": workflow.status,
        "progress": completed,
        "total_agents": 7,
        "current_agent": running.agent_name if running else None,
        "percent": round((completed / 7) * 100),
    }
