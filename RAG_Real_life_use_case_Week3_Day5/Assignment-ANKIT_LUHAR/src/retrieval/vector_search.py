"""
DP World RAG Chatbot — Vector Search.

Performs similarity search against the Pinecone vector index.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from config.constants import DEFAULT_TOP_K, SIMILARITY_THRESHOLD
from config.logging_config import get_logger
from config.settings import get_settings
from src.ingestion.embedding_service import EmbeddingService
from src.ingestion.pinecone_indexer import PineconeIndexer

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """A single search result from the vector store."""

    id: str
    score: float
    text: str
    metadata: dict = field(default_factory=dict)


class VectorSearch:
    """Perform similarity searches against Pinecone."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        pinecone_indexer: Optional[PineconeIndexer] = None,
    ) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.indexer = pinecone_indexer or PineconeIndexer()

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        namespace: str = "",
        filter_dict: Optional[dict] = None,
        score_threshold: float = SIMILARITY_THRESHOLD,
    ) -> list[SearchResult]:
        """
        Embed the query and search for similar vectors.

        Parameters
        ----------
        query : str
            User's search query.
        top_k : int
            Number of results to retrieve.
        namespace : str
            Pinecone namespace.
        filter_dict : dict, optional
            Metadata filters for the search.
        score_threshold : float
            Minimum similarity score.

        Returns
        -------
        list[SearchResult]
        """
        # 1. Embed the query
        query_embedding = self.embedding_service.embed_query(query)

        # 2. Query Pinecone
        index = self.indexer.get_index()
        query_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True,
            "namespace": namespace,
        }
        if filter_dict:
            query_params["filter"] = filter_dict

        response = index.query(**query_params)

        # 3. Parse results
        results: list[SearchResult] = []
        for match in response.matches:
            if match.score < score_threshold:
                continue
            results.append(
                SearchResult(
                    id=match.id,
                    score=match.score,
                    text=match.metadata.get("text", ""),
                    metadata=dict(match.metadata),
                )
            )

        logger.info(
            "vector_search_complete",
            query=query[:80],
            results_found=len(results),
            top_score=results[0].score if results else 0.0,
        )
        return results
