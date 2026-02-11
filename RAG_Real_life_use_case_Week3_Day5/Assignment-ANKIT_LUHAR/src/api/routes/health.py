"""
DP World RAG Chatbot — Health Check Routes.
"""

from __future__ import annotations

import time

from fastapi import APIRouter

from config.logging_config import get_logger
from config.settings import get_settings
from src.api.schemas.common_schemas import HealthResponse
from src.utils.metrics import MetricsCollector

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])

_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health() -> HealthResponse:
    """Detailed health check with service statuses."""
    settings = get_settings()
    services: dict[str, str] = {}

    # Check Redis
    try:
        import redis

        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            socket_timeout=2,
        )
        r.ping()
        services["redis"] = "healthy"
        r.close()
    except Exception:
        services["redis"] = "unavailable"

    # Check Groq API key
    services["groq"] = "configured" if settings.groq_api_key else "not_configured"

    # Check Cohere API key
    services["cohere"] = "configured" if settings.cohere_api_key else "not_configured"

    # Check Pinecone API key
    services["pinecone"] = "configured" if settings.pinecone_api_key else "not_configured"

    overall = "healthy" if all(
        v in ("healthy", "configured") for v in services.values()
    ) else "degraded"

    return HealthResponse(
        status=overall,
        version="1.0.0",
        services=services,
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@router.get("/metrics")
async def get_metrics() -> dict:
    """Return application metrics."""
    collector = MetricsCollector()
    return collector.get_stats()
