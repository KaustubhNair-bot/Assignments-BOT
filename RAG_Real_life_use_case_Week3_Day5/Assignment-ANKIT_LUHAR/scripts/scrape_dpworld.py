#!/usr/bin/env python3
"""
DP World RAG Chatbot — Scraper Script.

Usage:
    python scripts/scrape_dpworld.py [--max-pages 100] [--output-dir data/raw]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logging_config import setup_logging
from src.scraper.dpworld_scraper import DPWorldScraper


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape DP World website")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum pages to scrape")
    parser.add_argument("--output-dir", type=str, default="data/raw", help="Output directory")
    parser.add_argument("--base-url", type=str, default=None, help="Base URL override")
    args = parser.parse_args()

    setup_logging()

    print("=" * 60)
    print("🚢 DP World Web Scraper")
    print("=" * 60)
    print(f"  Max pages : {args.max_pages}")
    print(f"  Output    : {args.output_dir}")
    print()

    scraper = DPWorldScraper(
        base_url=args.base_url,
        output_dir=args.output_dir,
        max_pages=args.max_pages,
    )

    try:
        docs = scraper.scrape()
        print(f"\n✅ Scraped {len(docs)} documents successfully!")
        print(f"   Saved to: {args.output_dir}/scraped_documents.json")

        # Print summary
        total_words = sum(d.word_count for d in docs)
        print(f"   Total words: {total_words:,}")
        print(f"   Avg words/doc: {total_words // max(len(docs), 1):,}")
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user.")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
