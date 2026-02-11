"""
Tests — Text Splitter.
"""

from __future__ import annotations

import pytest

from src.ingestion.document_loader import Document
from src.ingestion.text_splitter import TextSplitter


class TestTextSplitter:
    """Tests for the TextSplitter class."""

    def test_short_text_no_split(self):
        """Short text should produce a single chunk."""
        splitter = TextSplitter(chunk_size=1000, chunk_overlap=0)
        doc = Document(id="test", text="This is a short document.")
        chunks = splitter.split_documents([doc])
        # May be filtered out if below MIN_CHUNK_SIZE
        assert len(chunks) <= 1

    def test_splits_long_text(self, sample_text):
        """Long text should be split into multiple chunks."""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
        doc = Document(id="test", text=sample_text)
        chunks = splitter.split_documents([doc])
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.chunk_id.startswith("test_chunk_")

    def test_chunk_metadata_preserved(self, sample_text):
        """Chunk metadata should include parent doc info."""
        splitter = TextSplitter(chunk_size=200, chunk_overlap=0)
        doc = Document(
            id="doc_00001",
            text=sample_text,
            metadata={"source_url": "https://example.com", "title": "Test"},
        )
        chunks = splitter.split_documents([doc])
        for chunk in chunks:
            assert chunk.metadata["source_url"] == "https://example.com"
            assert chunk.metadata["parent_doc_id"] == "doc_00001"
            assert "chunk_index" in chunk.metadata

    def test_empty_documents(self):
        """Empty document list should return empty chunks."""
        splitter = TextSplitter()
        chunks = splitter.split_documents([])
        assert chunks == []

    def test_custom_chunk_size(self, sample_text):
        """Custom chunk_size should be respected."""
        small = TextSplitter(chunk_size=50, chunk_overlap=0)
        large = TextSplitter(chunk_size=500, chunk_overlap=0)

        doc = Document(id="test", text=sample_text)
        small_chunks = small.split_documents([doc])
        large_chunks = large.split_documents([doc])

        assert len(small_chunks) >= len(large_chunks)
