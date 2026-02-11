"""
DP World RAG Chatbot — Content Cleaner.

Cleans raw HTML content and extracts meaningful text for the RAG pipeline.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from bs4 import BeautifulSoup, Comment

from config.logging_config import get_logger

logger = get_logger(__name__)

# Tags whose entire content should be removed
REMOVE_TAGS = {
    "script", "style", "noscript", "iframe", "svg", "canvas",
    "nav", "footer", "header", "aside", "form", "button",
}

# Tags that contain meaningful content
CONTENT_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "blockquote", "span", "div", "article", "section", "main"}


class ContentCleaner:
    """Clean raw HTML and extract structured text."""

    def clean_html(self, html: str, source_url: str = "") -> dict[str, Optional[str]]:
        """
        Parse HTML and return a dict with ``title``, ``text``, and ``meta_description``.
        """
        soup = BeautifulSoup(html, "lxml")

        # Extract metadata
        title = self._extract_title(soup)
        meta_desc = self._extract_meta_description(soup)

        # Remove unwanted elements
        self._strip_unwanted(soup)

        # Extract main content (prefer <main> or <article>)
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        if main_content is None:
            main_content = soup

        raw_text = main_content.get_text(separator="\n", strip=True)
        cleaned = self._normalise_text(raw_text)

        if len(cleaned) < 50:
            logger.debug("content_too_short", url=source_url, length=len(cleaned))
            return {"title": title, "text": None, "meta_description": meta_desc}

        return {"title": title, "text": cleaned, "meta_description": meta_desc}

    # ── Helpers ─────────────────────────────────────────────
    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("title")
        if tag:
            return tag.get_text(strip=True)
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        return None

    @staticmethod
    def _extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return None

    @staticmethod
    def _strip_unwanted(soup: BeautifulSoup) -> None:
        """Remove tags, comments, and hidden elements."""
        # Remove comments
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

        # Remove unwanted tags
        for tag_name in REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove hidden elements
        for tag in soup.find_all(attrs={"aria-hidden": "true"}):
            tag.decompose()
        for tag in soup.find_all(attrs={"style": re.compile(r"display\s*:\s*none")}):
            tag.decompose()

    @staticmethod
    def _normalise_text(text: str) -> str:
        """Normalise unicode, collapse whitespace, and strip junk."""
        text = unicodedata.normalize("NFKC", text)
        # Collapse multiple newlines into double
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Collapse multiple spaces
        text = re.sub(r"[ \t]{2,}", " ", text)
        # Remove lines that are just symbols
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not re.fullmatch(r"[\W_]+", line.strip())
        ]
        return "\n".join(lines)
