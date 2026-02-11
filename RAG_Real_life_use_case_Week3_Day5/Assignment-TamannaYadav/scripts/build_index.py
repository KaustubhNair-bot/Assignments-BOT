#!/usr/bin/env python3
"""Script to build the FAISS index from Tesla documents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
from ingestion.pdf_loader import PDFLoader
from preprocessing.text_cleaner import TextCleaner
from chunking.text_splitter import RecursiveTextSplitter
from embeddings.embedding_generator import EmbeddingGenerator
from vector_db.faiss_store import FAISSVectorStore


def main():
    """Build the FAISS index from Tesla PDF documents."""
    print("=" * 60)
    print("Tesla RAG - Building FAISS Index")
    print("=" * 60)
    
    print("\n[1/5] Loading PDF documents...")
    loader = PDFLoader(str(DATA_DIR))
    documents = loader.load()
    print(f"  - Loaded {len(documents)} documents from {DATA_DIR}")
    
    print("\n[2/5] Preprocessing documents...")
    cleaner = TextCleaner()
    cleaned_docs = cleaner.clean_batch(documents)
    print(f"  - Cleaned {len(cleaned_docs)} documents")
    
    print("\n[3/5] Chunking documents...")
    print(f"  - Chunk size: {CHUNK_SIZE} chars, Overlap: {CHUNK_OVERLAP} chars")
    splitter = RecursiveTextSplitter()
    chunks = splitter.split_documents(cleaned_docs)
    print(f"  - Created {len(chunks)} chunks")
    
    print("\n[4/5] Generating embeddings...")
    print(f"  - Using model: {EMBEDDING_MODEL}")
    embedding_generator = EmbeddingGenerator()
    embedded_chunks = embedding_generator.embed_chunks(chunks)
    print(f"  - Generated embeddings for {len(embedded_chunks)} chunks")
    
    print("\n[5/5] Building and saving FAISS index...")
    vector_store = FAISSVectorStore()
    vector_store.create_index()
    vector_store.add_embedded_chunks(embedded_chunks)
    vector_store.save()
    
    stats = vector_store.get_stats()
    print(f"  - Index stats: {stats}")
    
    print("\n" + "=" * 60)
    print("Index building complete!")
    print(f"Total chunks indexed: {len(embedded_chunks)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
