"""Local embedding model for secure text vectorization."""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings


class EmbeddingModel:
    """
    Local embedding model that runs entirely on-premise.
    No patient data is transmitted externally.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model to save memory."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array of embeddings
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype('float32')
    
    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings.astype('float32')
    
    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return settings.EMBEDDING_DIMENSION
