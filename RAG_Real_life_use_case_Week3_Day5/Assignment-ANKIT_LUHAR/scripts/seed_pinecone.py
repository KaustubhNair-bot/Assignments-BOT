#!/usr/bin/env python3

\
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logging_config import setup_logging
from config.settings import get_settings
from src.ingestion.pinecone_indexer import PineconeIndexer


def main() -> None:
    setup_logging()
    settings = get_settings()

    print("=" * 60)
    print("🌲 Pinecone Index Setup")
    print("=" * 60)
    print(f"  Index name : {settings.pinecone_index_name}")
    print(f"  Cloud      : {settings.pinecone_cloud}")
    print(f"  Region     : {settings.pinecone_region}")
    print()

    indexer = PineconeIndexer()
    indexer.create_index()

    stats = indexer.get_stats()
    print(f"\n📊 Index Stats:")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Dimension:     {stats['dimension']}")
    print("\n✅ Pinecone index is ready!")


if __name__ == "__main__":
    main()
