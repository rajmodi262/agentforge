"""AgentForge AI — Global Exception Handlers

Catches unhandled exceptions and returns structured JSON errors
with request IDs for traceability. Safely skips errors that occur
after the response stream has already started (e.g., background tasks).
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors gracefully."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id[:8]}] Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database error occurred. Please try again.",
            "request_id": request_id,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — never leak stack traces.
    
    Note: If the response has already started streaming (e.g., during
    a background task), we cannot send a new response. In that case,
    we just log the error and re-raise to let the framework handle it.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id[:8]}] Unhandled error: {exc}", exc_info=True)

    # Check if this is a RuntimeError from response already started
    if isinstance(exc, RuntimeError) and "response" in str(exc).lower():
        raise exc

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again.",
            "request_id": request_id,
        },
    )
