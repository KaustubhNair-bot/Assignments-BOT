"""
DP World RAG Chatbot — Admin Routes.

Endpoints for system administration: reindex, stats, etc.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from config.logging_config import get_logger
from src.api.schemas.common_schemas import APIResponse
from src.ingestion.pinecone_indexer import PineconeIndexer
from src.utils.metrics import MetricsCollector

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def system_stats() -> APIResponse:
    """Get system statistics including vector DB stats and metrics."""
    try:
        indexer = PineconeIndexer()
        pinecone_stats = indexer.get_stats()
    except Exception as exc:
        logger.error("pinecone_stats_error", error=str(exc))
        pinecone_stats = {"error": str(exc)}

    metrics = MetricsCollector()

    return APIResponse(
        success=True,
        data={
            "pinecone": pinecone_stats,
            "application": metrics.get_stats(),
        },
    )


@router.post("/reindex")
async def trigger_reindex(background_tasks: BackgroundTasks) -> APIResponse:
    """Trigger a full re-ingestion pipeline in the background."""

    async def _run_reindex() -> None:
        try:
            from src.ingestion.document_loader import DocumentLoader
            from src.ingestion.embedding_service import EmbeddingService
            from src.ingestion.text_splitter import TextSplitter

            logger.info("reindex_started")
            loader = DocumentLoader()
            splitter = TextSplitter()
            embedder = EmbeddingService()
            indexer = PineconeIndexer()

            docs = loader.load()
            chunks = splitter.split_documents(docs)
            vectors = embedder.embed_chunks(chunks)
            indexer.upsert_vectors(vectors)
            logger.info("reindex_complete", vectors=len(vectors))
        except Exception as exc:
            logger.error("reindex_error", error=str(exc))

    background_tasks.add_task(_run_reindex)

    return APIResponse(
        success=True,
        message="Re-indexing started in background",
    )


@router.post("/clear-index")
async def clear_index(namespace: str = "") -> APIResponse:
    """Clear all vectors in the Pinecone index."""
    try:
        indexer = PineconeIndexer()
        indexer.delete_all(namespace=namespace)
        return APIResponse(success=True, message="Index cleared")
    except Exception as exc:
        logger.error("clear_index_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/metrics/reset")
async def reset_metrics() -> APIResponse:
    """Reset application metrics."""
    MetricsCollector().reset()
    return APIResponse(success=True, message="Metrics reset")
