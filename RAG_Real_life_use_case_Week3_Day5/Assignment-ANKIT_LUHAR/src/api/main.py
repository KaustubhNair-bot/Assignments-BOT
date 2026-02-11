"""
DP World RAG Chatbot — FastAPI Application Entry Point.

Initialises the FastAPI app with all routes, middleware, and lifecycle hooks.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config.constants import API_DESCRIPTION, API_TITLE, API_V1_PREFIX, API_VERSION
from config.logging_config import get_logger, setup_logging
from src.api.middleware.cors import setup_cors
from src.api.middleware.error_handler import setup_error_handlers
from src.api.middleware.rate_limiter import limiter
from src.api.middleware.request_logger import RequestLoggerMiddleware
from src.api.routes import admin, chat, feedback, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan: startup and shutdown hooks."""
    # ── Startup ────────────────────────────────────────────
    setup_logging()
    logger = get_logger(__name__)
    logger.info("application_starting", version=API_VERSION)

    yield

    # ── Shutdown ───────────────────────────────────────────
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Rate Limiter ────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Middleware (order matters: last added = first executed) ─
    app.add_middleware(RequestLoggerMiddleware)
    setup_cors(app)

    # ── Error Handlers ──────────────────────────────────────
    setup_error_handlers(app)

    # ── Routes ──────────────────────────────────────────────
    app.include_router(health.router, prefix=API_V1_PREFIX)
    app.include_router(chat.router, prefix=API_V1_PREFIX)
    app.include_router(feedback.router, prefix=API_V1_PREFIX)
    app.include_router(admin.router, prefix=API_V1_PREFIX)

    # ── Root redirect ───────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": API_TITLE,
            "version": API_VERSION,
            "docs": "/docs",
            "health": f"{API_V1_PREFIX}/health",
        }

    return app


# Uvicorn entry point
app = create_app()
