"""StartupOS AI — API Router (aggregates all route modules)"""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.workflow import router as workflow_router
from app.api.websocket import router as websocket_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(workflow_router, prefix="/workflow", tags=["Workflow"])
api_router.include_router(websocket_router, tags=["WebSocket"])
