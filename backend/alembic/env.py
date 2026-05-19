"""Alembic Environment — StartupOS AI

Reads the DB URL from app.config (not alembic.ini) to keep
credentials in a single source of truth (.env).
Supports both online (live DB) and offline (SQL script) migrations.
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

# Ensure the backend root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings
from app.database import Base, engine as app_engine

# Import ALL models so Alembic sees them for autogenerate
from app.models.db_models import (  # noqa: F401
    User, Project, WorkflowRun, AgentTask, AgentMessage, ProjectReport,
    AgentLog, PromptVersion, AuditLog, WorkflowTemplate,
    KnowledgeDocument, N8nWebhook,
)

# Alembic Config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL scripts."""
    settings = get_settings()
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using app's engine (with SQLite fallback)."""
    connectable = app_engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
