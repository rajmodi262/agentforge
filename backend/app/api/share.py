"""AgentForge AI — Shareable Links API

Allows generating secure, public share links for generated project reports.
"""

import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.db_models import Project, ProjectReport

router = APIRouter()

def generate_share_token() -> str:
    """Generate a secure, random 32-character hex string."""
    return secrets.token_hex(16)


@router.post("/projects/{project_id}/share", response_model=dict)
def generate_share_link(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Generate or retrieve a public share link for a project."""
    stmt = select(Project).where(Project.id == project_id)
    project = db.execute(stmt).scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.share_token:
        project.share_token = generate_share_token()
        db.commit()
        db.refresh(project)

    return {
        "share_token": project.share_token,
        "share_url": f"/shared/{project.share_token}"
    }


@router.get("/shared/{share_token}")
def get_shared_project(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Retrieve basic project details for a shared link (unauthenticated)."""
    stmt = select(Project).where(Project.share_token == share_token)
    project = db.execute(stmt).scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Shared link not found or expired")

    # Get the latest report
    report_stmt = select(ProjectReport).where(
        ProjectReport.project_id == project.id
    ).order_by(ProjectReport.generated_at.desc())
    report = db.execute(report_stmt).scalar_first()

    return {
        "title": project.title,
        "business_idea": project.business_idea,
        "target_market": project.target_market,
        "budget_range": project.budget_range,
        "status": project.status,
        "has_report": report is not None,
        "report_id": report.id if report else None,
    }


@router.get("/shared/{share_token}/report/download")
def download_shared_report(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Download the PDF report using a share token (unauthenticated)."""
    stmt = select(Project).where(Project.share_token == share_token)
    project = db.execute(stmt).scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Shared link not found")

    report_stmt = select(ProjectReport).where(
        ProjectReport.project_id == project.id
    ).order_by(ProjectReport.generated_at.desc())
    report = db.execute(report_stmt).scalar_first()

    if not report or not report.file_path:
        raise HTTPException(status_code=404, detail="Report not available")

    # Construct absolute path to report
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    report_path = os.path.normpath(os.path.join(base_dir, report.file_path))

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    return FileResponse(
        path=report_path,
        filename=f"AgentForge_Blueprint_{project.title.replace(' ', '_')}.pdf",
        media_type="application/pdf"
    )
