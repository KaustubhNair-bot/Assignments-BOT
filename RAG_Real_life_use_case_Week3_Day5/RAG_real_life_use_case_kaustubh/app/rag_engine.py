"""
RAG Engine for Airtel Customer Support Chatbot.

Handles:
- PDF / Markdown document loading
- Text chunking (RecursiveCharacterTextSplitter)
- Embedding generation (sentence-transformers)
- FAISS vector store creation & persistence
- Similarity-based retrieval
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np

# PDF / text processing
from PyPDF2 import PdfReader

# LangChain text splitting
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

# FAISS
import faiss

# Sentence Transformers for embeddings
from sentence_transformers import SentenceTransformer

# ---------- Configuration ----------
DATA_DIR = Path(__file__).parent.parent / "data"
INDEX_DIR = Path(__file__).parent.parent / "faiss_index"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # lightweight, fast, 384-dim
CHUNK_SIZE = 500          # characters per chunk
CHUNK_OVERLAP = 100       # overlap between chunks


class RAGEngine:
    """End-to-end RAG pipeline: load → chunk → embed → store → retrieve."""

    def __init__(self, embedding_model_name: str = EMBEDDING_MODEL_NAME):
        self.embedding_model_name = embedding_model_name
        self.embedder: SentenceTransformer = None
        self.index: faiss.IndexFlatL2 = None
        self.chunks: List[str] = []
        self.chunk_metadata: List[dict] = []  # source, page, chunk_id
        self._load_embedder()

    # ------------------------------------------------------------------ #
    #  EMBEDDING MODEL                                                    #
    # ------------------------------------------------------------------ #
    def _load_embedder(self):
        """Load the sentence-transformer embedding model."""
        print(f"[RAG] Loading embedding model: {self.embedding_model_name}")
        self.embedder = SentenceTransformer(self.embedding_model_name)
        print(f"[RAG] Embedding model loaded. Dimension: {self.embedder.get_sentence_embedding_dimension()}")

    # ------------------------------------------------------------------ #
    #  DOCUMENT LOADING                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def load_pdf(pdf_path: str) -> str:
        """Extract text from a PDF file."""
        reader = PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text += f"\n\n--- PAGE {i+1} ---\n\n{page_text}"
        return text

    @staticmethod
    def load_markdown(md_path: str) -> str:
        """Read a Markdown file as plain text."""
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()

    def load_documents(self, data_dir: str = None) -> str:
        """Load all PDF and Markdown files from the data directory."""
        data_dir = Path(data_dir) if data_dir else DATA_DIR
        combined_text = ""
        files_loaded = []

        for file in sorted(data_dir.iterdir()):
            if file.suffix.lower() == ".pdf":
                print(f"[RAG] Loading PDF: {file.name}")
                combined_text += self.load_pdf(str(file))
                files_loaded.append(file.name)
            elif file.suffix.lower() in (".md", ".txt"):
                print(f"[RAG] Loading text: {file.name}")
                combined_text += "\n\n" + self.load_markdown(str(file))
                files_loaded.append(file.name)

        print(f"[RAG] Loaded {len(files_loaded)} file(s): {files_loaded}")
        print(f"[RAG] Total characters: {len(combined_text):,}")
        return combined_text

    # ------------------------------------------------------------------ #
    #  CHUNKING                                                           #
    # ------------------------------------------------------------------ #
    def chunk_text(
        self,
        text: str,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> List[str]:
        """Split text into overlapping chunks using RecursiveCharacterTextSplitter."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        chunks = splitter.split_text(text)
        self.chunks = chunks
        self.chunk_metadata = [
            {"chunk_id": i, "length": len(c), "preview": c[:80] + "..."}
            for i, c in enumerate(chunks)
        ]
        print(f"[RAG] Created {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
        return chunks

    # ------------------------------------------------------------------ #
    #  EMBEDDING & INDEXING                                               #
    # ------------------------------------------------------------------ #
    def build_index(self, chunks: List[str] = None) -> faiss.IndexFlatL2:
        """Embed chunks and build a FAISS index."""
        if chunks is not None:
            self.chunks = chunks

        if not self.chunks:
            raise ValueError("No chunks to embed. Call chunk_text() first.")

        print(f"[RAG] Embedding {len(self.chunks)} chunks ...")
        embeddings = self.embedder.encode(
            self.chunks, show_progress_bar=True, convert_to_numpy=True
        )
        embeddings = embeddings.astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        print(f"[RAG] FAISS index built: {self.index.ntotal} vectors, dim={dim}")
        return self.index

    def save_index(self, index_dir: str = None):
        """Persist the FAISS index and chunk data to disk."""
        index_dir = Path(index_dir) if index_dir else INDEX_DIR
        index_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_dir / "index.faiss"))
        with open(index_dir / "chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
        with open(index_dir / "metadata.json", "w") as f:
            json.dump(self.chunk_metadata, f, indent=2)

        print(f"[RAG] Index saved to {index_dir}")

    def load_index(self, index_dir: str = None) -> bool:
        """Load a previously saved FAISS index."""
        index_dir = Path(index_dir) if index_dir else INDEX_DIR
        index_path = index_dir / "index.faiss"
        chunks_path = index_dir / "chunks.pkl"

        if not index_path.exists() or not chunks_path.exists():
            print("[RAG] No saved index found.")
            return False

        self.index = faiss.read_index(str(index_path))
        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)
        if (index_dir / "metadata.json").exists():
            with open(index_dir / "metadata.json", "r") as f:
                self.chunk_metadata = json.load(f)

        print(f"[RAG] Loaded index: {self.index.ntotal} vectors, {len(self.chunks)} chunks")
        return True

    # ------------------------------------------------------------------ #
    #  RETRIEVAL                                                          #
    # ------------------------------------------------------------------ #
    def retrieve(
        self, query: str, top_k: int = 5
    ) -> List[Tuple[str, float, int]]:
        """
        Retrieve the top-k most similar chunks for a query.

        Returns:
            List of (chunk_text, distance_score, chunk_index) tuples.
        """
        if self.index is None or self.index.ntotal == 0:
            raise ValueError("Index is empty. Build or load an index first.")

        query_embedding = self.embedder.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(dist), int(idx)))

        return results

    # ------------------------------------------------------------------ #
    #  FULL PIPELINE                                                      #
    # ------------------------------------------------------------------ #
    def initialize(self, force_rebuild: bool = False, data_dir: str = None):
        """
        Full initialization pipeline:
        1) Try to load existing index.
        2) If not found or force_rebuild, load docs → chunk → embed → save.
        """
        if not force_rebuild and self.load_index():
            print("[RAG] Using cached FAISS index.")
            return

        print("[RAG] Building index from scratch ...")
        raw_text = self.load_documents(data_dir)
        self.chunk_text(raw_text)
        self.build_index()
        self.save_index()
        print("[RAG] Initialization complete.")

    # ------------------------------------------------------------------ #
    #  STATS / INTROSPECTION                                              #
    # ------------------------------------------------------------------ #
    def get_stats(self) -> dict:
        """Return summary statistics about the current index."""
        return {
            "total_chunks": len(self.chunks),
            "index_vectors": self.index.ntotal if self.index else 0,
            "embedding_model": self.embedding_model_name,
            "embedding_dim": self.embedder.get_sentence_embedding_dimension(),
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
        }
