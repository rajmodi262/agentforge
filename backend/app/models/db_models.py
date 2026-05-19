"""StartupOS AI — SQLAlchemy ORM Models

Production-grade with enterprise features:
- SoftDeleteMixin for safe logical deletes
- Comprehensive indexes on FK columns and common query patterns
- Check constraints for status fields
- Relative file paths for portability
- RBAC roles on User
- AgentLog for LLM observability
- PromptVersion for prompt management
- AuditLog for enterprise compliance
- WorkflowTemplate for graph editor
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, Boolean,
    ForeignKey, JSON, TypeDecorator, CHAR, Index, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return uuid.uuid4()


class GUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type when available, otherwise CHAR(32).
    """
    impl = CHAR(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return value.hex
            return uuid.UUID(str(value)).hex
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value


# ─────────────────────────────── Mixins ───────────────────────────────


class TimestampMixin:
    """Adds created_at and updated_at to any model."""
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class SoftDeleteMixin:
    """Adds soft-delete capability to any model.
    
    Instead of physically removing rows, we set is_deleted=True
    and record deleted_at. All queries should filter on is_deleted=False.
    """
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


# ─────────────────────────────── Core Models ───────────────────────────────


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    role = Column(String(50), default="editor")  # viewer | editor | admin | owner

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    __table_args__ = (
        # Composite index: quickly find a user's active projects
        Index("ix_projects_user_status", "user_id", "status"),
        # Check constraint: status must be one of the valid values
        CheckConstraint(
            "status IN ('draft', 'running', 'completed', 'error')",
            name="ck_projects_status",
        ),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    business_idea = Column(Text, nullable=False)
    target_market = Column(String(255))
    budget_range = Column(String(100))
    status = Column(String(50), default="draft")  # draft | running | completed | error
    share_token = Column(String(64), unique=True, index=True, nullable=True)

    # Relationships
    user = relationship("User", back_populates="projects")
    workflow_runs = relationship("WorkflowRun", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("ProjectReport", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.title[:30]} [{self.status}]>"


class WorkflowRun(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflow_runs"
    __table_args__ = (
        # Composite index: find workflows for a project by status
        Index("ix_workflow_runs_project_status", "project_id", "status"),
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_workflow_runs_status",
        ),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False, index=True)
    status = Column(String(50), default="queued")  # queued | running | completed | failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)  # Store raw dollars, format on display
    error_message = Column(Text)

    # Relationships
    project = relationship("Project", back_populates="workflow_runs")
    agent_tasks = relationship("AgentTask", back_populates="workflow_run", cascade="all, delete-orphan")
    agent_messages = relationship("AgentMessage", back_populates="workflow_run", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="workflow_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkflowRun {str(self.id)[:8]} [{self.status}]>"


class AgentTask(Base, TimestampMixin):
    __tablename__ = "agent_tasks"
    __table_args__ = (
        # Composite index: find tasks for a workflow by status
        Index("ix_agent_tasks_workflow_status", "workflow_id", "status"),
        # Index for ordering by started_at within a workflow
        Index("ix_agent_tasks_workflow_started", "workflow_id", "started_at"),
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="ck_agent_tasks_status",
        ),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    workflow_id = Column(GUID, ForeignKey("workflow_runs.id"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")  # pending | running | completed | failed
    input_context = Column(JSON)
    output_data = Column(JSON)
    tokens_used = Column(Integer, default=0)
    execution_time = Column(Integer, default=0)  # seconds
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="agent_tasks")

    def __repr__(self):
        return f"<AgentTask {self.agent_name} [{self.status}]>"


class AgentMessage(Base, TimestampMixin):
    __tablename__ = "agent_messages"
    __table_args__ = (
        # Index: find messages for a workflow ordered by creation
        Index("ix_agent_messages_workflow_created", "workflow_id", "created_at"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    workflow_id = Column(GUID, ForeignKey("workflow_runs.id"), nullable=False, index=True)
    sender = Column(String(100), nullable=False)
    recipient = Column(String(100), nullable=False)
    message_type = Column(String(50))  # instruction | data | question | result
    content = Column(Text, nullable=False)

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="agent_messages")

    def __repr__(self):
        return f"<AgentMessage {self.sender} → {self.recipient}>"


class ProjectReport(Base):
    __tablename__ = "project_reports"
    __table_args__ = (
        # Index: find reports for a project ordered by generation time
        Index("ix_project_reports_project_generated", "project_id", "generated_at"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False, index=True)
    # Relative path from REPORTS_DIR — portable across deployments
    file_path = Column(String(500))
    file_size = Column(Integer)
    generated_at = Column(DateTime(timezone=True), default=utcnow)
    download_count = Column(Integer, default=0)

    # Relationships
    project = relationship("Project", back_populates="reports")

    def __repr__(self):
        return f"<ProjectReport project={str(self.project_id)[:8]}>"


# ─────────────────────────── Phase 1: Observability ───────────────────────────


class AgentLog(Base, TimestampMixin):
    """Tracks every LLM call with full observability.
    
    Provides token tracking, cost calculation, latency monitoring,
    and error rate analysis — matching/exceeding Dify's LLMOps.
    """
    __tablename__ = "agent_logs"
    __table_args__ = (
        Index("ix_agent_logs_workflow", "workflow_id"),
        Index("ix_agent_logs_agent_status", "agent_name", "status"),
        Index("ix_agent_logs_created", "created_at"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    workflow_id = Column(GUID, ForeignKey("workflow_runs.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    model_provider = Column(String(50))   # "claude", "gemini", "mock"
    model_name = Column(String(100))      # "claude-3-haiku", "gemini-1.5-flash"
    cost_usd = Column(Float, default=0.0)
    status = Column(String(50))           # "success", "error", "fallback"
    error_message = Column(Text, nullable=True)
    input_preview = Column(Text)          # First 500 chars of prompt
    output_preview = Column(Text)         # First 500 chars of response
    request_id = Column(String(100), nullable=True)
    feedback_score = Column(Integer, nullable=True)  # 1=thumbs up, -1=thumbs down

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="agent_logs")

    def __repr__(self):
        return f"<AgentLog {self.agent_name} [{self.status}] {self.total_tokens}tok>"


# ─────────────────────────── Phase 4: Prompt IDE ───────────────────────────


class PromptVersion(Base, TimestampMixin):
    """Tracks prompt versions for A/B testing and rollback.
    
    Each agent can have multiple prompt versions. Only one is active at a time.
    Performance scores are computed from user feedback.
    """
    __tablename__ = "prompt_versions"
    __table_args__ = (
        Index("ix_prompt_versions_agent", "agent_name"),
        Index("ix_prompt_versions_active", "agent_name", "is_active"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    agent_name = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False)
    system_prompt = Column(Text, nullable=False)
    output_schema = Column(JSON, nullable=True)
    notes = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False)
    performance_score = Column(Float, nullable=True)  # Avg feedback score
    total_runs = Column(Integer, default=0)
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)

    def __repr__(self):
        return f"<PromptVersion {self.agent_name} v{self.version} {'[ACTIVE]' if self.is_active else ''}>"


# ─────────────────────────── Phase 5: Enterprise ───────────────────────────


class AuditLog(Base, TimestampMixin):
    """Enterprise audit trail for compliance and security.
    
    Automatically captures all mutating API calls with
    user context, IP address, and resource details.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created", "created_at"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    user_id = Column(String(100), nullable=True, index=True)
    action = Column(String(100), nullable=False)     # "create_project", "run_workflow", etc.
    resource_type = Column(String(50))               # "project", "workflow", "user"
    resource_id = Column(String(100))
    ip_address = Column(String(45))                  # IPv4/IPv6
    user_agent = Column(String(500))
    details = Column(JSON, nullable=True)            # Extra context
    status_code = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} by={self.user_id}>"


class WorkflowTemplate(Base, TimestampMixin):
    """Reusable workflow graph templates.
    
    Users can save custom agent topologies and share them.
    System templates provide pre-built workflows (full-planning, quick-mvp, etc.).
    """
    __tablename__ = "workflow_templates"
    __table_args__ = (
        Index("ix_workflow_templates_system", "is_system"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    graph_json = Column(JSON, nullable=False)        # Node/edge topology
    is_system = Column(Boolean, default=False)       # Built-in vs user-created
    created_by = Column(String(100), nullable=True)  # User ID for custom templates
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<WorkflowTemplate {self.name} {'[SYSTEM]' if self.is_system else ''}>"


class KnowledgeDocument(Base, TimestampMixin):
    """Uploaded documents for RAG knowledge base.
    
    Persists document metadata so it survives server restarts.
    Actual files stored on disk; embeddings in ChromaDB.
    """
    __tablename__ = "knowledge_documents"
    __table_args__ = (
        Index("ix_knowledge_docs_project", "project_id"),
    )

    id = Column(GUID, primary_key=True, default=new_uuid)
    filename = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    extension = Column(String(20))
    chunks = Column(Integer, default=0)
    stored_in_rag = Column(Integer, default=0)
    project_id = Column(String(100), nullable=True)
    file_path = Column(String(1000), nullable=True)  # Path on disk

    def __repr__(self):
        return f"<KnowledgeDocument {self.filename}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_size": self.file_size,
            "extension": self.extension,
            "chunks": self.chunks,
            "stored_in_rag": self.stored_in_rag,
            "project_id": self.project_id,
            "uploaded_at": self.created_at.isoformat() if self.created_at else None,
        }


class N8nWebhook(Base, TimestampMixin):
    """Registered n8n webhook URLs for event routing.
    
    Persists webhook registrations so they survive server restarts.
    """
    __tablename__ = "n8n_webhooks"

    id = Column(GUID, primary_key=True, default=new_uuid)
    event_type = Column(String(100), nullable=False, unique=True)
    webhook_url = Column(String(2000), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<N8nWebhook {self.event_type}>"


