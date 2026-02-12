

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from config.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE
from config.logging_config import get_logger
from src.ingestion.document_loader import Document

logger = get_logger(__name__)


@dataclass
class TextChunk:
    """A chunk of text derived from a parent document."""

    chunk_id: str
    text: str
    metadata: dict = field(default_factory=dict)


class TextSplitter:
    """Split documents into overlapping, semantically-aware chunks."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        separators: Optional[list[str]] = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    def split_documents(self, documents: list[Document]) -> list[TextChunk]:
        """Split a list of Documents into TextChunks."""
        all_chunks: list[TextChunk] = []
        for doc in documents:
            chunks = self._split_text(doc.text)
            for idx, chunk_text in enumerate(chunks):
                chunk = TextChunk(
                    chunk_id=f"{doc.id}_chunk_{idx:04d}",
                    text=chunk_text,
                    metadata={
                        **doc.metadata,
                        "chunk_index": idx,
                        "parent_doc_id": doc.id,
                    },
                )
                all_chunks.append(chunk)

        logger.info(
            "documents_split",
            total_documents=len(documents),
            total_chunks=len(all_chunks),
            avg_chunk_len=round(
                sum(len(c.text) for c in all_chunks) / max(len(all_chunks), 1)
            ),
        )
        return all_chunks

    def _split_text(self, text: str) -> list[str]:
        """Recursively split text using a hierarchy of separators."""
        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Split at the first working separator; recurse for sub-parts."""
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        if not separators:

            return self._hard_split(text)

        sep = separators[0]
        remaining_seps = separators[1:]

        parts = text.split(sep)

        chunks: list[str] = []
        current = ""

        for part in parts:
            candidate = f"{current}{sep}{part}" if current else part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                if len(part) > self.chunk_size:

                    sub_chunks = self._recursive_split(part, remaining_seps)
                    chunks.extend(sub_chunks)
                    current = ""
                else:
                    current = part

        if current and current.strip():
            chunks.append(current.strip())


        return self._apply_overlap(chunks)

    def _hard_split(self, text: str) -> list[str]:
        """Character-level fallback split."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap between consecutive chunks."""
        if self.chunk_overlap == 0 or len(chunks) <= 1:
            return chunks

        result: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = chunks[i - 1]
            overlap_text = prev[-self.chunk_overlap :] if len(prev) > self.chunk_overlap else prev
            merged = f"{overlap_text} {chunks[i]}"

            if len(merged) <= self.chunk_size * 1.2:
                result.append(merged.strip())
            else:
                result.append(chunks[i])

        return [c for c in result if len(c) >= MIN_CHUNK_SIZE]
