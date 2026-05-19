"""StartupOS AI — Audit Middleware (Phase 5)

Auto-logs all mutating API calls (POST, PUT, DELETE) with user context."""

import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.database import SessionLocal
from app.models.db_models import AuditLog

logger = logging.getLogger(__name__)

AUDITED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
SKIP_PATHS = {"/api/v1/auth/login", "/api/v1/auth/register", "/health", "/docs", "/openapi.json"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.method not in AUDITED_METHODS:
            return response
        if any(request.url.path.startswith(p) for p in SKIP_PATHS):
            return response

        try:
            path_parts = request.url.path.strip("/").split("/")
            # Extract resource type and ID from path
            resource_type = path_parts[2] if len(path_parts) > 2 else "unknown"
            resource_id = path_parts[3] if len(path_parts) > 3 else None

            action = f"{request.method.lower()}_{resource_type}"

            # Get user ID from request state if available
            user_id = None
            if hasattr(request.state, "user_id"):
                user_id = str(request.state.user_id)

            db = SessionLocal()
            try:
                log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent", "")[:500],
                    status_code=response.status_code,
                )
                db.add(log)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Audit log failed: {e}")

        return response
