"""
Tests — Pinecone Search (Integration).

These tests require a live Pinecone connection.
Mark with @pytest.mark.integration.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.retrieval.vector_search import SearchResult, VectorSearch


@pytest.mark.integration
class TestPineconeSearch:
    """Integration tests for vector search."""

    @patch("src.retrieval.vector_search.PineconeIndexer")
    @patch("src.retrieval.vector_search.EmbeddingService")
    def test_search_returns_results(self, mock_embed_cls, mock_indexer_cls):
        """Search should return SearchResult objects."""
        # Mock embedding
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1024
        mock_embed_cls.return_value = mock_embed

        # Mock Pinecone
        mock_indexer = MagicMock()
        mock_index = MagicMock()
        mock_match = MagicMock()
        mock_match.id = "chunk_001"
        mock_match.score = 0.85
        mock_match.metadata = {
            "text": "DP World services",
            "source_url": "https://dpworld.com",
            "title": "Services",
        }
        mock_index.query.return_value = MagicMock(matches=[mock_match])
        mock_indexer.get_index.return_value = mock_index
        mock_indexer_cls.return_value = mock_indexer

        vs = VectorSearch()
        results = vs.search("DP World services", top_k=5)

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].score == 0.85
        assert "DP World" in results[0].text

    @patch("src.retrieval.vector_search.PineconeIndexer")
    @patch("src.retrieval.vector_search.EmbeddingService")
    def test_search_filters_low_scores(self, mock_embed_cls, mock_indexer_cls):
        """Results below threshold should be filtered."""
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1024
        mock_embed_cls.return_value = mock_embed

        mock_indexer = MagicMock()
        mock_index = MagicMock()
        mock_match = MagicMock()
        mock_match.id = "chunk_002"
        mock_match.score = 0.1  # Below default threshold
        mock_match.metadata = {"text": "irrelevant"}
        mock_index.query.return_value = MagicMock(matches=[mock_match])
        mock_indexer.get_index.return_value = mock_index
        mock_indexer_cls.return_value = mock_indexer

        vs = VectorSearch()
        results = vs.search("unrelated query", top_k=5)

        assert len(results) == 0
