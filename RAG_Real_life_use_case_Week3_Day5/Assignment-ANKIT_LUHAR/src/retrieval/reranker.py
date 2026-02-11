"""
DP World RAG Chatbot — Reranker.

Uses Cohere Rerank to re-score and re-order retrieved documents
for improved relevance.
"""

from __future__ import annotations

from typing import Optional

import cohere

from config.logging_config import get_logger
from config.settings import get_settings
from src.retrieval.vector_search import SearchResult

logger = get_logger(__name__)


class Reranker:
    """Rerank search results using Cohere Rerank for improved relevance."""

    def __init__(self, model: str = "rerank-english-v3.0") -> None:
        settings = get_settings()
        self.client = cohere.Client(api_key=settings.cohere_api_key)
        self.model = model

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_n: Optional[int] = None,
    ) -> list[SearchResult]:
        """
        Rerank search results for the given query.

        Parameters
        ----------
        query : str
            The original user query.
        results : list[SearchResult]
            Initial search results from vector search.
        top_n : int, optional
            Number of results to return (default: all).

        Returns
        -------
        list[SearchResult]
            Reranked results ordered by relevance score.
        """
        if not results:
            return []

        documents = [r.text for r in results]
        top_n = top_n or len(results)

        try:
            response = self.client.rerank(
                query=query,
                documents=documents,
                model=self.model,
                top_n=top_n,
            )

            reranked: list[SearchResult] = []
            for item in response.results:
                original = results[item.index]
                reranked.append(
                    SearchResult(
                        id=original.id,
                        score=item.relevance_score,
                        text=original.text,
                        metadata=original.metadata,
                    )
                )

            logger.info(
                "reranking_complete",
                input_count=len(results),
                output_count=len(reranked),
            )
            return reranked

        except Exception as exc:
            logger.error("reranking_failed", error=str(exc))
            # Fall back to original ranking
            return results[:top_n]
