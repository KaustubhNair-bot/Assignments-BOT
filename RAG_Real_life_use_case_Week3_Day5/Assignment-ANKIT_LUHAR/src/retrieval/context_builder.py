
from __future__ import annotations

from typing import Optional

import tiktoken

from config.constants import MAX_CONTEXT_TOKENS
from config.logging_config import get_logger
from src.retrieval.vector_search import SearchResult

logger = get_logger(__name__)


class ContextBuilder:
    """Build a context prompt section from retrieved search results."""

    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS) -> None:
        self.max_tokens = max_tokens
        try:
            self._encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._encoder = None

    def build_context(
        self,
        results: list[SearchResult],
        include_sources: bool = True,
    ) -> dict[str, str | list[str]]:
        """
        Build a context string and source references.

        Returns
        -------
        dict
            ``context``: formatted context string for the LLM prompt.
            ``sources``: list of source URLs used.
        """
        if not results:
            return {"context": "", "sources": []}

        context_parts: list[str] = []
        sources: list[str] = []
        token_count = 0

        for idx, result in enumerate(results, 1):

            title = result.metadata.get("title", "Untitled")
            source_url = result.metadata.get("source_url", "")

            passage = (
                f"[Source {idx}] {title}\n"
                f"{result.text}\n"
            )


            passage_tokens = self._count_tokens(passage)
            if token_count + passage_tokens > self.max_tokens:

                remaining = self.max_tokens - token_count
                if remaining > 100:
                    passage = self._truncate_to_tokens(passage, remaining)
                    context_parts.append(passage)
                    if source_url:
                        sources.append(source_url)
                break

            context_parts.append(passage)
            token_count += passage_tokens
            if source_url and source_url not in sources:
                sources.append(source_url)

        context = "\n---\n".join(context_parts)

        logger.info(
            "context_built",
            num_passages=len(context_parts),
            total_tokens=self._count_tokens(context),
            num_sources=len(sources),
        )

        return {"context": context, "sources": sources}

    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken (fallback to word estimate)."""
        if self._encoder:
            return len(self._encoder.encode(text))
        return len(text.split()) * 4 // 3  # rough estimate

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within max_tokens."""
        if self._encoder:
            tokens = self._encoder.encode(text)[:max_tokens]
            return self._encoder.decode(tokens)
        words = text.split()
        max_words = max_tokens * 3 // 4
        return " ".join(words[:max_words]) + "..."
