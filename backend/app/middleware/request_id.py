"""StartupOS AI — Request ID Middleware

Attaches a unique X-Request-ID to every request/response for
end-to-end tracing through logs, errors, and downstream services.
"""

import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Injects a unique request ID into every request.
    
    - If the client sends X-Request-ID, it is reused (for distributed tracing).
    - Otherwise, a new UUID4 is generated.
    - The ID is attached to request.state.request_id and returned in the response header.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Reuse client-provided ID or generate a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Inject into logging context
        logger.info(
            f"[{request_id[:8]}] {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
