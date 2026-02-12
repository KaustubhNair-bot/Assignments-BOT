
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    """Internal document representation for the RAG pipeline."""

    id: str
    text: str
    metadata: dict = field(default_factory=dict)


class DocumentLoader:
    """Load scraped documents from disk and normalise them."""

    def __init__(self, data_dir: str = "data/raw") -> None:
        self.data_dir = Path(data_dir)

    def load(self, filename: str = "scraped_documents.json") -> list[Document]:
        """Load documents from a JSON file produced by the scraper."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.error("document_file_not_found", path=str(filepath))
            return []

        with open(filepath, encoding="utf-8") as f:
            raw_docs = json.load(f)

        documents: list[Document] = []
        for idx, raw in enumerate(raw_docs):
            text = raw.get("text")
            if not text or len(text.strip()) < 50:
                continue

            doc = Document(
                id=f"doc_{idx:05d}",
                text=text,
                metadata={
                    "source_url": raw.get("url", ""),
                    "title": raw.get("title", ""),
                    "meta_description": raw.get("meta_description", ""),
                    "word_count": raw.get("word_count", 0),
                    "scraped_at": raw.get("scraped_at", ""),
                },
            )
            documents.append(doc)

        logger.info("documents_loaded", count=len(documents))
        return documents

    def load_from_list(self, raw_docs: list[dict]) -> list[Document]:
        """Load documents from an in-memory list (e.g., directly from scraper)."""
        documents: list[Document] = []
        for idx, raw in enumerate(raw_docs):
            text = raw.get("text")
            if not text or len(text.strip()) < 50:
                continue

            doc = Document(
                id=f"doc_{idx:05d}",
                text=text,
                metadata={
                    "source_url": raw.get("url", ""),
                    "title": raw.get("title", ""),
                    "meta_description": raw.get("meta_description", ""),
                    "word_count": raw.get("word_count", 0),
                    "scraped_at": raw.get("scraped_at", ""),
                },
            )
            documents.append(doc)

        logger.info("documents_loaded_from_list", count=len(documents))
        return documents
