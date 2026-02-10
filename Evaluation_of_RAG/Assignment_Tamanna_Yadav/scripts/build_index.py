#!/usr/bin/env python3
"""Script to build the FAISS index from medical transcriptions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.data_processor import DataProcessor
from rag.embeddings import EmbeddingModel
from rag.vector_store import FAISSVectorStore
from config import settings


def main():
    """Build the FAISS index from the medical transcriptions dataset."""
    print("=" * 60)
    print("MediSecure RAG - Building FAISS Index")
    print("=" * 60)
    
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n[1/4] Loading and processing data...")
    print("  - Applying text chunking for better retrieval precision")
    print(f"  - Chunk size: {settings.CHUNK_SIZE} chars, Overlap: {settings.CHUNK_OVERLAP} chars")
    processor = DataProcessor()
    documents = processor.process_transcriptions(anonymize=True, apply_chunking=True)
    
    print(f"\n[2/4] Generating embeddings for {len(documents)} documents...")
    embedding_model = EmbeddingModel()
    
    texts = [processor.get_text_for_embedding(doc) for doc in documents]
    embeddings = embedding_model.embed_texts(texts, batch_size=32)
    
    print(f"\n[3/4] Creating FAISS index...")
    print(f"  - Using {settings.SIMILARITY_METRIC} similarity metric")
    print(f"  - Embedding model: {settings.EMBEDDING_MODEL} ({settings.EMBEDDING_DIMENSION} dimensions)")
    vector_store = FAISSVectorStore(dimension=embedding_model.dimension)
    vector_store.create_index(embeddings, documents)
    
    print(f"\n[4/4] Saving index to disk...")
    vector_store.save()
    
    print("\n" + "=" * 60)
    print("Index building complete!")
    print(f"Total documents indexed: {len(documents)}")
    print(f"Index location: {settings.FAISS_INDEX_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
