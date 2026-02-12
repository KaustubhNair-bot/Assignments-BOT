

from __future__ import annotations

import hashlib
import json
from typing import Optional

from config.constants import CACHE_PREFIX_QUERY, DEFAULT_TOP_K
from config.logging_config import get_logger
from config.settings import get_settings
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.reranker import Reranker
from src.retrieval.vector_search import SearchResult, VectorSearch

logger = get_logger(__name__)


class QueryEngine:
    """Orchestrate the retrieval pipeline for a user query."""

    def __init__(
        self,
        vector_search: Optional[VectorSearch] = None,
        reranker: Optional[Reranker] = None,
        context_builder: Optional[ContextBuilder] = None,
        redis_client: Optional[object] = None,
        use_reranker: bool = True,
    ) -> None:
        self.vector_search = vector_search or VectorSearch()
        self.reranker = reranker or Reranker() if use_reranker else None
        self.context_builder = context_builder or ContextBuilder()
        self._redis = redis_client
        settings = get_settings()
        self._cache_ttl = settings.redis_ttl

    async def process_query(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        use_cache: bool = True,
    ) -> dict:
        """
        Process a user query through the full retrieval pipeline.

        Returns
        -------
        dict
            ``context``: context string for the LLM.
            ``sources``: source URLs.
            ``results``: raw search results (dicts).
        """

        if use_cache and self._redis:
            cached = self._get_cached(query)
            if cached:
                logger.info("query_cache_hit", query=query[:60])
                return cached

        # 1. Vector search
        results = self.vector_search.search(query, top_k=top_k)

        # 2. Rerank (optional)
        if self.reranker and results:
            results = self.reranker.rerank(query, results, top_n=top_k)

        # 3. Build context
        context_data = self.context_builder.build_context(results)

        output = {
            "context": context_data["context"],
            "sources": context_data["sources"],
            "results": [
                {"id": r.id, "score": r.score, "text": r.text[:500]}
                for r in results
            ],
        }

        # Cache the result
        if use_cache and self._redis:
            self._set_cached(query, output)

        return output


    def _cache_key(self, query: str) -> str:
        h = hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]
        return f"{CACHE_PREFIX_QUERY}{h}"

    def _get_cached(self, query: str) -> Optional[dict]:
        try:
            data = self._redis.get(self._cache_key(query))  
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def _set_cached(self, query: str, value: dict) -> None:
        try:
            self._redis.setex(  
                self._cache_key(query),
                self._cache_ttl,
                json.dumps(value),
            )
        except Exception:
            pass
