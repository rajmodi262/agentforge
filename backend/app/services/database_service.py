"""StartupOS AI — Database Service (CRUD Operations)"""

import logging
from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.db_models import (
    User, Project, WorkflowRun, AgentTask, AgentMessage, ProjectReport
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Centralized database CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    # --- Projects ---
    def get_project(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        return self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id,
        ).first()

    def list_projects(self, user_id: UUID) -> List[Project]:
        return self.db.query(Project).filter(
            Project.user_id == user_id
        ).order_by(Project.created_at.desc()).all()

    # --- Workflows ---
    def get_workflow(self, workflow_id: UUID) -> Optional[WorkflowRun]:
        return self.db.query(WorkflowRun).filter(
            WorkflowRun.id == workflow_id
        ).first()

    def get_latest_workflow(self, project_id: UUID) -> Optional[WorkflowRun]:
        return self.db.query(WorkflowRun).filter(
            WorkflowRun.project_id == project_id
        ).order_by(WorkflowRun.started_at.desc()).first()

    # --- Agent Tasks ---
    def get_agent_tasks(self, workflow_id: UUID) -> List[AgentTask]:
        return self.db.query(AgentTask).filter(
            AgentTask.workflow_id == workflow_id
        ).order_by(AgentTask.started_at).all()

    # --- Agent Messages ---
    def get_agent_messages(self, workflow_id: UUID) -> List[AgentMessage]:
        return self.db.query(AgentMessage).filter(
            AgentMessage.workflow_id == workflow_id
        ).order_by(AgentMessage.created_at).all()

    # --- Reports ---
    def get_report(self, project_id: UUID) -> Optional[ProjectReport]:
        return self.db.query(ProjectReport).filter(
            ProjectReport.project_id == project_id
        ).order_by(ProjectReport.generated_at.desc()).first()
