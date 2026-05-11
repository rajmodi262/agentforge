"""StartupOS AI — SQLAlchemy ORM Models (All 6 Tables)"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    business_idea = Column(Text, nullable=False)
    target_market = Column(String(255))
    budget_range = Column(String(100))
    status = Column(String(50), default="draft")  # draft | running | completed | error
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    workflow_runs = relationship("WorkflowRun", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("ProjectReport", back_populates="project", cascade="all, delete-orphan")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), default="queued")  # queued | running | completed | failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    total_tokens = Column(Integer, default=0)
    total_cost = Column(String(20), default="$0.00")
    error_message = Column(Text)

    # Relationships
    project = relationship("Project", back_populates="workflow_runs")
    agent_tasks = relationship("AgentTask", back_populates="workflow_run", cascade="all, delete-orphan")
    agent_messages = relationship("AgentMessage", back_populates="workflow_run", cascade="all, delete-orphan")


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False)
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


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False)
    sender = Column(String(100), nullable=False)
    recipient = Column(String(100), nullable=False)
    message_type = Column(String(50))  # instruction | data | question | result
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="agent_messages")


class ProjectReport(Base):
    __tablename__ = "project_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    generated_at = Column(DateTime(timezone=True), default=utcnow)
    download_count = Column(Integer, default=0)

    # Relationships
    project = relationship("Project", back_populates="reports")
