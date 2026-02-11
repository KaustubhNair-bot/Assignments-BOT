"""
Embedding Generator for Tesla RAG system.
Generates dense vector representations for text chunks.
"""

from typing import List, Union
import numpy as np
from pathlib import Path

from sentence_transformers import SentenceTransformer

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from config.settings import EMBEDDING_MODEL, EMBEDDING_DIMENSION
from chunking.text_splitter import Chunk

logger = get_logger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings using sentence-transformers.
    
    Supports batch processing for efficiency.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.dimension = EMBEDDING_DIMENSION
        
        logger.info(f"Initialized EmbeddingGenerator with model: {model_name}")
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def generate(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embedding vector
        """
        self._load_model()
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of shape (n_texts, embedding_dim)
        """
        self._load_model()
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def embed_chunks(self, chunks: List[Chunk], batch_size: int = 32) -> List[dict]:
        """
        Generate embeddings for chunks and return with metadata.
        
        Args:
            chunks: List of Chunk objects
            batch_size: Batch size for processing
            
        Returns:
            List of dicts with chunk data and embeddings
        """
        texts = [chunk.content for chunk in chunks]
        embeddings = self.generate_batch(texts, batch_size)
        
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append({
                'chunk_id': chunk.chunk_id,
                'content': chunk.content,
                'embedding': embedding,
                'metadata': chunk.metadata
            })
        
        logger.info(f"Embedded {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        self._load_model()
        return self.dimension
