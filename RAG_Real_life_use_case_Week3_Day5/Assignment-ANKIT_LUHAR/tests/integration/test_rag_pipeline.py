"""
Tests — RAG Pipeline (Integration).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.retrieval.query_engine import QueryEngine


@pytest.mark.integration
class TestRAGPipeline:
    """Integration tests for the full RAG pipeline."""

    @patch("src.retrieval.query_engine.VectorSearch")
    @patch("src.retrieval.query_engine.Reranker")
    @patch("src.retrieval.query_engine.ContextBuilder")
    @pytest.mark.asyncio
    async def test_process_query(self, mock_ctx_cls, mock_rr_cls, mock_vs_cls):
        """process_query should return context, sources, and results."""
        from src.retrieval.vector_search import SearchResult

        # Mock vector search
        mock_vs = MagicMock()
        mock_vs.search.return_value = [
            SearchResult(
                id="c1", score=0.9, text="DP World ports",
                metadata={"source_url": "https://dpworld.com/ports", "title": "Ports"},
            )
        ]
        mock_vs_cls.return_value = mock_vs

        # Mock reranker (pass through)
        mock_rr = MagicMock()
        mock_rr.rerank.return_value = mock_vs.search.return_value
        mock_rr_cls.return_value = mock_rr

        # Mock context builder
        mock_ctx = MagicMock()
        mock_ctx.build_context.return_value = {
            "context": "DP World ports info",
            "sources": ["https://dpworld.com/ports"],
        }
        mock_ctx_cls.return_value = mock_ctx

        engine = QueryEngine(use_reranker=True)
        result = await engine.process_query("tell me about ports")

        assert "context" in result
        assert "sources" in result
        assert "results" in result
        assert len(result["sources"]) > 0
