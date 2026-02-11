"""
DP World RAG Chatbot — Sitemap Parser.

Parses sitemap.xml files to discover URLs for scraping.
"""

from __future__ import annotations

import re
from typing import Optional
from xml.etree import ElementTree

import requests

from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)

# XML namespace used in sitemaps
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class SitemapParser:
    """Parse sitemap.xml and sitemap index files to extract page URLs."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.scraper_base_url).rstrip("/")
        self.user_agent = settings.scraper_user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    # ── public API ──────────────────────────────────────────
    def get_urls(self, max_urls: Optional[int] = None) -> list[str]:
        """Return a deduplicated list of page URLs found in the sitemap."""
        sitemap_url = f"{self.base_url}/sitemap.xml"
        urls = self._parse_sitemap(sitemap_url)
        unique = list(dict.fromkeys(urls))  # preserve order, dedupe
        if max_urls:
            unique = unique[:max_urls]
        logger.info("sitemap_parsed", url_count=len(unique))
        return unique

    # ── internals ───────────────────────────────────────────
    def _fetch_xml(self, url: str) -> Optional[ElementTree.Element]:
        """Fetch and parse XML from a URL."""
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            # Strip namespaces for easier parsing
            content = re.sub(r'\sxmlns="[^"]+"', "", resp.text, count=1)
            return ElementTree.fromstring(content)
        except Exception as exc:
            logger.warning("sitemap_fetch_failed", url=url, error=str(exc))
            return None

    def _parse_sitemap(self, url: str) -> list[str]:
        """Recursively parse sitemaps (handles sitemap indexes)."""
        root = self._fetch_xml(url)
        if root is None:
            return []

        urls: list[str] = []

        # Check for sitemap index
        for sitemap in root.iter("sitemap"):
            loc = sitemap.find("loc")
            if loc is not None and loc.text:
                urls.extend(self._parse_sitemap(loc.text.strip()))

        # Collect URLs
        for url_el in root.iter("url"):
            loc = url_el.find("loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())

        return urls

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
