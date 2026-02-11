"""
DP World RAG Chatbot — Text Utilities.

Common text processing functions used across modules.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalise and clean a text string."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max_length, trying to break at a word boundary."""
    if len(text) <= max_length:
        return text
    truncated = text[: max_length - len(suffix)]
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.5:
        truncated = truncated[:last_space]
    return truncated + suffix


def hash_text(text: str) -> str:
    """Return a short SHA-256 hash of the text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def count_words(text: str) -> int:
    """Count words in the text."""
    return len(text.split())


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    return re.sub(r"https?://\S+", "", text).strip()


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-_")
