"""
DP World RAG Chatbot — Structured Logging Configuration.

Uses ``structlog`` for structured JSON logging in production and
pretty-printed coloured logs in development.
"""

from __future__ import annotations

import logging
import sys

import structlog

from config.settings import get_settings


def setup_logging() -> None:
    """Configure structured logging for the entire application."""
    settings = get_settings()
    log_level = getattr(logging, settings.app_log_level, logging.INFO)

    # Shared processors for both stdlib and structlog
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.is_production:
        # JSON output for production (parseable by log aggregation)
        renderer = structlog.processors.JSONRenderer()
    else:
        # Pretty colour output for development
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    # Root handler
    root_handler = logging.StreamHandler(sys.stdout)
    root_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(root_handler)
    root_logger.setLevel(log_level)

    # Quieten noisy third-party loggers
    for name in ("httpx", "httpcore", "urllib3", "uvicorn.access"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger with the given name."""
    return structlog.get_logger(name)
