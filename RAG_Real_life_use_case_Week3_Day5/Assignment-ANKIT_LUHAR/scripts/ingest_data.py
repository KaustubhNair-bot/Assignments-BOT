#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logging_config import setup_logging
from src.ingestion.document_loader import DocumentLoader
from src.ingestion.embedding_service import EmbeddingService
from src.ingestion.pinecone_indexer import PineconeIndexer
from src.ingestion.text_splitter import TextSplitter


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest scraped data into Pinecone")
    parser.add_argument("--data-dir", type=str, default="data/raw", help="Scraped data directory")
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=64, help="Overlap between chunks")
    parser.add_argument("--batch-size", type=int, default=100, help="Pinecone upsert batch size")
    args = parser.parse_args()

    setup_logging()

    print("=" * 60)
    print("📦 DP World Data Ingestion Pipeline")
    print("=" * 60)

    start = time.time()

    # Step 1: Load documents
    print("\n[1/4] Loading documents...")
    loader = DocumentLoader(data_dir=args.data_dir)
    documents = loader.load()
    print(f"  ✅ Loaded {len(documents)} documents")

    if not documents:
        print("  ❌ No documents found. Run the scraper first!")
        print("     python scripts/scrape_dpworld.py")
        sys.exit(1)

    # Step 2: Split into chunks
    print("\n[2/4] Splitting documents into chunks...")
    splitter = TextSplitter(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    chunks = splitter.split_documents(documents)
    print(f"  ✅ Created {len(chunks)} chunks")

    # Step 3: Generate embeddings
    print("\n[3/4] Generating embeddings (this may take a while)...")
    embedder = EmbeddingService()
    vectors = embedder.embed_chunks(chunks)
    print(f"  ✅ Generated {len(vectors)} embeddings")

    # Step 4: Upsert to Pinecone
    print("\n[4/4] Upserting vectors to Pinecone...")
    indexer = PineconeIndexer()
    indexer.create_index()
    total = indexer.upsert_vectors(vectors, batch_size=args.batch_size)
    print(f"  ✅ Upserted {total} vectors")

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"✅ Ingestion complete in {elapsed:.1f}s")
    print(f"   Documents: {len(documents)}")
    print(f"   Chunks:    {len(chunks)}")
    print(f"   Vectors:   {total}")

    # Print index stats
    stats = indexer.get_stats()
    print(f"\n📊 Pinecone Index Stats:")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Dimension:     {stats['dimension']}")


if __name__ == "__main__":
    main()
