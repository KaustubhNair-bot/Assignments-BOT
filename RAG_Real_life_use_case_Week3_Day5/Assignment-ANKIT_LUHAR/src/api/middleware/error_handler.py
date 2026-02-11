"""
DP World RAG Chatbot — Global Error Handler.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from config.logging_config import get_logger
from src.api.schemas.common_schemas import ErrorResponse
from src.utils.validators import ValidationError

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning("validation_error", field=exc.field, error=str(exc))
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="Validation Error",
                detail=str(exc),
                status_code=422,
            ).model_dump(),
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        logger.warning("rate_limit_exceeded", client=request.client.host if request.client else "unknown")
        return JSONResponse(
            status_code=429,
            content=ErrorResponse(
                error="Rate Limit Exceeded",
                detail="Too many requests. Please slow down.",
                status_code=429,
            ).model_dump(),
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="Not Found",
                detail="The requested resource was not found.",
                status_code=404,
            ).model_dump(),
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("internal_error", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal Server Error",
                detail="An unexpected error occurred. Please try again later.",
                status_code=500,
            ).model_dump(),
        )
