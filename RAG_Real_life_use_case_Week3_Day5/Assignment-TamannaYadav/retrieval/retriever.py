"""
Retriever for Tesla RAG system.
Handles query embedding and similarity-based retrieval.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from config.settings import TOP_K, SIMILARITY_THRESHOLD
from embeddings.embedding_generator import EmbeddingGenerator
from vector_db.faiss_store import FAISSVectorStore

logger = get_logger(__name__)


class Retriever:
    """
    Retrieves relevant chunks for user queries.
    
    Converts queries to embeddings and performs similarity search.
    """
    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        vector_store: FAISSVectorStore,
        top_k: int = TOP_K,
        similarity_threshold: float = SIMILARITY_THRESHOLD
    ):
        """
        Initialize the retriever.
        
        Args:
            embedding_generator: EmbeddingGenerator instance
            vector_store: FAISSVectorStore instance
            top_k: Number of results to retrieve
            similarity_threshold: Minimum similarity score threshold
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"Initialized Retriever with top_k={top_k}, threshold={similarity_threshold}")
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_threshold: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query string
            top_k: Override default top_k
            filter_threshold: Whether to filter by similarity threshold
            
        Returns:
            List of retrieved chunks with scores and metadata
        """
        k = top_k or self.top_k
        
        logger.info(f"Retrieving top-{k} chunks for query: '{query[:50]}...'")
        
        query_embedding = self.embedding_generator.generate(query)
        
        results = self.vector_store.search(query_embedding, top_k=k)
        
        if filter_threshold:
            results = [
                r for r in results 
                if r['similarity_score'] >= self.similarity_threshold
            ]
        
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        logger.info(f"Retrieved {len(results)} chunks above threshold")
        return results
    
    def retrieve_with_context(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve chunks and format as context for LLM.
        
        Args:
            query: User query string
            top_k: Override default top_k
            
        Returns:
            Dict with 'context' string and 'chunks' list
        """
        chunks = self.retrieve(query, top_k)
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk['metadata'].get('filename', 'Unknown')
            context_parts.append(
                f"[Source {i}: {source}]\n{chunk['content']}"
            )
        
        context = "\n\n---\n\n".join(context_parts)
        
        return {
            'context': context,
            'chunks': chunks,
            'num_chunks': len(chunks)
        }
    
    def get_retrieval_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about retrieval results.
        
        Args:
            results: List of retrieval results
            
        Returns:
            Statistics dict
        """
        if not results:
            return {'count': 0}
        
        scores = [r['similarity_score'] for r in results]
        sources = set(r['metadata'].get('filename', 'Unknown') for r in results)
        
        return {
            'count': len(results),
            'avg_score': np.mean(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'unique_sources': len(sources),
            'sources': list(sources)
        }
