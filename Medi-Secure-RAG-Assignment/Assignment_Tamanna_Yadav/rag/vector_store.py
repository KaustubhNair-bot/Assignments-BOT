"""FAISS vector store for efficient similarity search."""
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings


class FAISSVectorStore:
    """
    FAISS-based vector store for medical transcription embeddings.
    All data remains on-premise for HIPAA compliance.
    """
    
    def __init__(self, dimension: int = None):
        """
        Initialize the FAISS vector store.
        
        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = settings.METADATA_PATH
    
    def create_index(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """
        Create a new FAISS index from embeddings.
        
        Args:
            embeddings: Numpy array of embeddings (n_samples, dimension)
            metadata: List of metadata dictionaries for each embedding
        """
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {embeddings.shape[1]}")
        
        self.index = faiss.IndexFlatL2(self.dimension)
        
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        self.index.add(embeddings)
        self.metadata = metadata
        
        print(f"Created FAISS index with {self.index.ntotal} vectors")
    
    def save(self) -> None:
        """Save the index and metadata to disk."""
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        index_file = self.index_path / "index.faiss"
        faiss.write_index(self.index, str(index_file))
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"Saved index to {index_file}")
        print(f"Saved metadata to {self.metadata_path}")
    
    def load(self) -> bool:
        """
        Load the index and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        index_file = self.index_path / "index.faiss"
        
        if not index_file.exists() or not self.metadata_path.exists():
            return False
        
        try:
            self.index = faiss.read_index(str(index_file))
            
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            print(f"Loaded FAISS index with {self.index.ntotal} vectors")
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, top_k: int = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (metadata, similarity_score) tuples
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call create_index() or load() first.")
        
        top_k = top_k or settings.TOP_K_RESULTS
        
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1 and idx < len(self.metadata):
                similarity = 1 - (distance / 2)
                results.append((self.metadata[idx], float(similarity)))
        
        return results
    
    @property
    def is_initialized(self) -> bool:
        """Check if the index is initialized."""
        return self.index is not None and len(self.metadata) > 0
