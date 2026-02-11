"""
Tests — Embedding Service.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.embedding_service import EmbeddingService
from src.ingestion.text_splitter import TextChunk


class TestEmbeddingService:
    """Tests for the EmbeddingService class."""

    @patch("src.ingestion.embedding_service.cohere.Client")
    def test_embed_texts(self, mock_cohere_cls):
        """embed_texts should return a list of embeddings."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.embeddings = [[0.1] * 1024, [0.2] * 1024]
        mock_client.embed.return_value = mock_response
        mock_cohere_cls.return_value = mock_client

        service = EmbeddingService()
        result = service.embed_texts(["hello", "world"])

        assert len(result) == 2
        assert len(result[0]) == 1024
        mock_client.embed.assert_called_once()

    @patch("src.ingestion.embedding_service.cohere.Client")
    def test_embed_query(self, mock_cohere_cls):
        """embed_query should use search_query input_type."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.embeddings = [[0.5] * 1024]
        mock_client.embed.return_value = mock_response
        mock_cohere_cls.return_value = mock_client

        service = EmbeddingService()
        result = service.embed_query("what is DP World?")

        assert len(result) == 1024
        call_kwargs = mock_client.embed.call_args
        assert call_kwargs.kwargs.get("input_type") == "search_query"

    @patch("src.ingestion.embedding_service.cohere.Client")
    def test_embed_chunks(self, mock_cohere_cls):
        """embed_chunks should return Pinecone-ready vector dicts."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.embeddings = [[0.1] * 1024]
        mock_client.embed.return_value = mock_response
        mock_cohere_cls.return_value = mock_client

        service = EmbeddingService()
        chunks = [TextChunk(chunk_id="c1", text="test text", metadata={"title": "Test"})]
        vectors = service.embed_chunks(chunks)

        assert len(vectors) == 1
        assert vectors[0]["id"] == "c1"
        assert "values" in vectors[0]
        assert "metadata" in vectors[0]
        assert vectors[0]["metadata"]["text"] == "test text"

    @patch("src.ingestion.embedding_service.cohere.Client")
    def test_embed_error_returns_zeros(self, mock_cohere_cls):
        """On API error, should return zero vectors."""
        mock_client = MagicMock()
        mock_client.embed.side_effect = Exception("API Error")
        mock_cohere_cls.return_value = mock_client

        service = EmbeddingService()
        result = service.embed_texts(["test"])

        assert len(result) == 1
        assert all(v == 0.0 for v in result[0])
