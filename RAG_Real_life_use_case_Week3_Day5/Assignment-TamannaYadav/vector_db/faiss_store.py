"""
FAISS Vector Store for Tesla RAG system.
Handles vector storage, indexing, and similarity search.
"""

import os
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import numpy as np
import faiss

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from config.settings import VECTOR_DB_DIR, EMBEDDING_DIMENSION

logger = get_logger(__name__)


class FAISSVectorStore:
    """
    FAISS-based vector store with cosine similarity.
    
    Supports adding, saving, loading, and querying vectors.
    """
    
    def __init__(
        self,
        dimension: int = EMBEDDING_DIMENSION,
        index_path: Optional[str] = None
    ):
        """
        Initialize the FAISS vector store.
        
        Args:
            dimension: Dimension of embedding vectors
            index_path: Path to save/load the index
        """
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else VECTOR_DB_DIR
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.index = None
        self.metadata_store: List[Dict[str, Any]] = []
        self.chunk_contents: List[str] = []
        
        logger.info(f"Initialized FAISSVectorStore with dimension={dimension}")
    
    def create_index(self):
        """Create a new FAISS index with cosine similarity."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata_store = []
        self.chunk_contents = []
        
        logger.info("Created new FAISS index with Inner Product (cosine) similarity")
    
    def add_vectors(
        self,
        embeddings: np.ndarray,
        contents: List[str],
        metadata: List[Dict[str, Any]]
    ):
        """
        Add vectors to the index.
        
        Args:
            embeddings: Numpy array of shape (n, dimension)
            contents: List of chunk contents
            metadata: List of metadata dicts for each vector
        """
        if self.index is None:
            self.create_index()
        
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        self.index.add(embeddings)
        self.chunk_contents.extend(contents)
        self.metadata_store.extend(metadata)
        
        logger.info(f"Added {len(embeddings)} vectors to index. Total: {self.index.ntotal}")
    
    def add_embedded_chunks(self, embedded_chunks: List[Dict[str, Any]]):
        """
        Add embedded chunks to the index.
        
        Args:
            embedded_chunks: List of dicts with 'embedding', 'content', 'metadata'
        """
        embeddings = np.array([c['embedding'] for c in embedded_chunks])
        contents = [c['content'] for c in embedded_chunks]
        metadata = [c['metadata'] for c in embedded_chunks]
        
        self.add_vectors(embeddings, contents, metadata)
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of results with content, metadata, and similarity score
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append({
                    'content': self.chunk_contents[idx],
                    'metadata': self.metadata_store[idx],
                    'similarity_score': float(score)
                })
        
        logger.debug(f"Search returned {len(results)} results")
        return results
    
    def save(self, name: str = "tesla_index"):
        """
        Save the index and metadata to disk.
        
        Args:
            name: Name for the saved files
        """
        if self.index is None:
            logger.warning("No index to save")
            return
        
        index_file = self.index_path / f"{name}.faiss"
        faiss.write_index(self.index, str(index_file))
        
        metadata_file = self.index_path / f"{name}_metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'metadata_store': self.metadata_store,
                'chunk_contents': self.chunk_contents,
                'dimension': self.dimension
            }, f)
        
        logger.info(f"Saved index to {index_file}")
    
    def load(self, name: str = "tesla_index") -> bool:
        """
        Load the index and metadata from disk.
        
        Args:
            name: Name of the saved files
            
        Returns:
            True if loaded successfully, False otherwise
        """
        index_file = self.index_path / f"{name}.faiss"
        metadata_file = self.index_path / f"{name}_metadata.pkl"
        
        if not index_file.exists() or not metadata_file.exists():
            logger.warning(f"Index files not found at {self.index_path}")
            return False
        
        self.index = faiss.read_index(str(index_file))
        
        with open(metadata_file, 'rb') as f:
            data = pickle.load(f)
            self.metadata_store = data['metadata_store']
            self.chunk_contents = data['chunk_contents']
            self.dimension = data['dimension']
        
        logger.info(f"Loaded index with {self.index.ntotal} vectors")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_path': str(self.index_path)
        }
