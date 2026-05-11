"""StartupOS AI — Projects API (CRUD + Start Workflow)"""

import asyncio
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User, Project, WorkflowRun
from app.models.request_schemas import CreateProjectRequest
from app.models.response_schemas import ProjectResponse, ProjectListResponse
from app.api.auth import get_current_user
from app.agents.orchestrator import run_workflow

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new project with a startup idea."""
    project = Project(
        user_id=current_user.id,
        title=request.title,
        business_idea=request.business_idea,
        target_market=request.target_market,
        budget_range=request.budget_range,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=ProjectListResponse)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all projects for the current user."""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).all()
    return ProjectListResponse(projects=projects, total=len(projects))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/start")
async def start_workflow(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start the 7-agent workflow for a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status == "running":
        raise HTTPException(status_code=400, detail="Workflow already running")

    # Create workflow run
    workflow = WorkflowRun(project_id=project.id)
    db.add(workflow)
    project.status = "running"
    db.commit()
    db.refresh(workflow)

    # Run workflow in background
    background_tasks.add_task(
        run_workflow,
        workflow_id=str(workflow.id),
        project_id=str(project.id),
        business_idea=project.business_idea,
        target_market=project.target_market,
        budget_range=project.budget_range,
    )

    return {
        "message": "Workflow started",
        "workflow_id": str(workflow.id),
        "websocket_url": f"/api/v1/ws/{workflow.id}",
    }
