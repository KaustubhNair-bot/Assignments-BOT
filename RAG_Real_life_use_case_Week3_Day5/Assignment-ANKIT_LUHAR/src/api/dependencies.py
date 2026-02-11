"""
DP World RAG Chatbot — FastAPI Dependency Injection.

Provides singleton instances of services for FastAPI route handlers.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

import redis

from config.logging_config import get_logger
from config.settings import get_settings
from src.chat.chat_manager import ChatManager
from src.chat.feedback_handler import FeedbackHandler
from src.chat.history_manager import HistoryManager
from src.chat.session_manager import SessionManager
from src.generation.groq_client import GroqClient
from src.generation.guardrails import Guardrails
from src.generation.response_formatter import ResponseFormatter
from src.ingestion.embedding_service import EmbeddingService
from src.ingestion.pinecone_indexer import PineconeIndexer
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.query_engine import QueryEngine
from src.retrieval.reranker import Reranker
from src.retrieval.vector_search import VectorSearch

logger = get_logger(__name__)


@lru_cache()
def get_redis_client() -> Optional[redis.Redis]:
    """Create a Redis client (returns None if unavailable)."""
    settings = get_settings()
    try:
        client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password or None,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        client.ping()
        logger.info("redis_connected")
        return client
    except Exception as exc:
        logger.warning("redis_unavailable", error=str(exc))
        return None


@lru_cache()
def get_chat_manager() -> ChatManager:
    """Build and return the ChatManager with all dependencies wired up."""
    redis_client = get_redis_client()

    embedding_service = EmbeddingService(redis_client=redis_client)
    pinecone_indexer = PineconeIndexer()

    vector_search = VectorSearch(
        embedding_service=embedding_service,
        pinecone_indexer=pinecone_indexer,
    )
    reranker = Reranker()
    context_builder = ContextBuilder()

    query_engine = QueryEngine(
        vector_search=vector_search,
        reranker=reranker,
        context_builder=context_builder,
        redis_client=redis_client,
    )

    groq_client = GroqClient()
    session_manager = SessionManager(redis_client=redis_client)
    history_manager = HistoryManager(redis_client=redis_client)
    guardrails = Guardrails()
    formatter = ResponseFormatter()

    return ChatManager(
        query_engine=query_engine,
        groq_client=groq_client,
        session_manager=session_manager,
        history_manager=history_manager,
        guardrails=guardrails,
        formatter=formatter,
    )


@lru_cache()
def get_feedback_handler() -> FeedbackHandler:
    """Return the FeedbackHandler singleton."""
    return FeedbackHandler()
