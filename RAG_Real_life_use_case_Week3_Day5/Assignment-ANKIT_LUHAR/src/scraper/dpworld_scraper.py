

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

from config.constants import ALLOWED_CONTENT_TYPES, MAX_RETRIES, SKIP_EXTENSIONS
from config.logging_config import get_logger
from config.settings import get_settings
from src.scraper.content_cleaner import ContentCleaner
from src.scraper.sitemap_parser import SitemapParser

logger = get_logger(__name__)


@dataclass
class ScrapedDocument:
    """Represents a single scraped page."""

    url: str
    title: Optional[str] = None
    text: Optional[str] = None
    meta_description: Optional[str] = None
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    word_count: int = 0


class DPWorldScraper:
    """Scrape DP World website pages and produce structured documents."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        output_dir: str = "data/raw",
        max_pages: Optional[int] = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.scraper_base_url).rstrip("/")
        self.max_pages = max_pages or settings.scraper_max_pages
        self.delay = settings.scraper_delay_seconds
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.scraper_user_agent,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })

        self.cleaner = ContentCleaner()
        self.sitemap_parser = SitemapParser(self.base_url)

        self._visited: set[str] = set()
        self._documents: list[ScrapedDocument] = []


    def scrape(self) -> list[ScrapedDocument]:
        """Run the full scraping pipeline. Returns scraped documents."""
        logger.info("scraper_started", base_url=self.base_url, max_pages=self.max_pages)

        # 1. Discover URLs from sitemap
        urls = self.sitemap_parser.get_urls(max_urls=self.max_pages)

        if not urls:
            # Fallback: scrape known important pages
            urls = self._get_fallback_urls()

        # 2. Scrape each URL
        for i, url in enumerate(urls):
            if len(self._documents) >= self.max_pages:
                break
            if url in self._visited:
                continue

            logger.info("scraping_page", page=i + 1, total=len(urls), url=url)
            doc = self._scrape_page(url)
            if doc and doc.text:
                self._documents.append(doc)

            time.sleep(self.delay)

        # 3. Persist to disk
        self._save_documents()

        logger.info("scraper_finished", documents_scraped=len(self._documents))
        return self._documents

    def scrape_single(self, url: str) -> Optional[ScrapedDocument]:
        """Scrape a single URL."""
        return self._scrape_page(url)


    def _scrape_page(self, url: str) -> Optional[ScrapedDocument]:
        """Fetch and clean a single page."""
        self._visited.add(url)

        if self._should_skip(url):
            return None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=30)
                resp.raise_for_status()

                content_type = resp.headers.get("Content-Type", "")
                if not any(ct in content_type for ct in ALLOWED_CONTENT_TYPES):
                    logger.debug("skipped_non_html", url=url, content_type=content_type)
                    return None

                result = self.cleaner.clean_html(resp.text, source_url=url)
                if not result["text"]:
                    return None

                doc = ScrapedDocument(
                    url=url,
                    title=result["title"],
                    text=result["text"],
                    meta_description=result["meta_description"],
                    word_count=len(result["text"].split()),
                )
                return doc

            except requests.RequestException as exc:
                logger.warning(
                    "scrape_error",
                    url=url,
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt < MAX_RETRIES:
                    time.sleep(2**attempt)
        return None

    def _should_skip(self, url: str) -> bool:
        """Return True if the URL should be skipped."""
        parsed = urlparse(url)
        ext = os.path.splitext(parsed.path)[1].lower()
        if ext in SKIP_EXTENSIONS:
            return True

        base_domain = urlparse(self.base_url).netloc
        if parsed.netloc and parsed.netloc != base_domain:
            return True
        return False

    def _get_fallback_urls(self) -> list[str]:
        """Return a hand-curated list of important DP World pages."""
        paths = [
            "/",
            "/about-us",
            "/our-services",
            "/smart-trade",
            "/logistics",
            "/ports-and-terminals",
            "/container-tracking",
            "/shipping-schedules",
            "/tariffs",
            "/contact-us",
            "/careers",
            "/sustainability",
            "/technology-and-innovation",
            "/cargoes",
            "/marine-services",
            "/free-zones",
            "/trade-solutions",
        ]
        return [urljoin(self.base_url, p) for p in paths]

    def _save_documents(self) -> None:
        """Save scraped documents to JSON."""
        output_file = self.output_dir / "scraped_documents.json"
        data = [asdict(doc) for doc in self._documents]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("documents_saved", path=str(output_file), count=len(data))

    def close(self) -> None:
        """Clean up resources."""
        self.session.close()
        self.sitemap_parser.close()
