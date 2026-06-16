"""End-to-end orchestrator test (mock mode).

Runs the FULL LangGraph pipeline — all 7 agents + board meeting + report —
against an isolated SQLite DB, and asserts the workflow + agent tasks are
persisted as completed. RAG (ChromaDB) is stubbed so the test stays fast and
offline. This is the coverage the suite previously lacked entirely.
"""

import os
import asyncio
import tempfile

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base
from app.models.db_models import User, Project, WorkflowRun, AgentTask


@pytest.fixture
def orch_factory():
    # The orchestrator's parallel fan-out commits from several threads at once.
    # Postgres handles that with one connection per session; to emulate that
    # here we use a FILE-based SQLite with NullPool (a fresh connection per
    # checkout) + WAL + a busy timeout. A shared in-memory StaticPool would
    # serialize onto one connection and raise "transaction within a transaction".
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    eng = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False, "timeout": 30},
        poolclass=NullPool,
    )

    @event.listens_for(eng, "connect")
    def _set_pragmas(dbapi_conn, _rec):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA busy_timeout=30000")
        cur.close()

    Base.metadata.create_all(bind=eng)
    try:
        yield sessionmaker(autocommit=False, autoflush=False, bind=eng)
    finally:
        eng.dispose()
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(path + suffix)
            except OSError:
                pass


def test_run_workflow_end_to_end_mock(orch_factory, monkeypatch):
    import app.agents.orchestrator as orch

    # Stub RAG so the graph doesn't touch ChromaDB / embedding models
    monkeypatch.setattr(orch, "_store_rag", lambda *a, **k: None)
    monkeypatch.setattr(orch, "_retrieve_rag", lambda *a, **k: "")

    Factory = orch_factory
    db = Factory()
    u = User(email="orch@test.com", password_hash="x"); db.add(u); db.commit()
    p = Project(user_id=u.id, title="T",
                business_idea="An AI tool for hostel food delivery"); db.add(p); db.commit()
    w = WorkflowRun(project_id=p.id, status="queued"); db.add(w); db.commit()
    wid, pid = str(w.id), str(p.id)
    db.close()

    asyncio.run(orch.run_workflow(
        workflow_id=wid, project_id=pid,
        business_idea="An AI tool for hostel food delivery",
        session_factory=Factory,
    ))

    db = Factory()
    wf = db.query(WorkflowRun).filter(WorkflowRun.id == wid).first()
    tasks = db.query(AgentTask).filter(AgentTask.workflow_id == wid).all()
    db.close()

    assert wf.status == "completed"
    assert len(tasks) == 7
    assert all(t.status == "completed" for t in tasks)
