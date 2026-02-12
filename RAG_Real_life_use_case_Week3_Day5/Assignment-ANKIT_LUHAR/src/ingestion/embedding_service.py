

from __future__ import annotations

import hashlib
import json
import time
from typing import Optional

import cohere

from config.constants import CACHE_PREFIX_EMBEDDING, COHERE_EMBED_DIMENSION
from config.logging_config import get_logger
from config.settings import get_settings
from src.ingestion.text_splitter import TextChunk

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings for text chunks using Cohere embed-english-v3.0."""

    def __init__(self, redis_client: Optional[object] = None) -> None:
        settings = get_settings()
        self.client = cohere.Client(api_key=settings.cohere_api_key)
        self.model = settings.cohere_embed_model
        self.dimension = COHERE_EMBED_DIMENSION
        self._redis = redis_client
        self._batch_size = 96  # Cohere recommended batch size

    def embed_texts(
        self,
        texts: list[str],
        input_type: str = "search_document",
    ) -> list[list[float]]:
        """
        Embed a list of texts.

        Parameters
        ----------
        texts : list[str]
            The texts to embed.
        input_type : str
            One of ``search_document`` or ``search_query``.
        """
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    response = self.client.embed(
                        texts=batch,
                        model=self.model,
                        input_type=input_type,
                        truncate="END",
                    )
                    all_embeddings.extend(response.embeddings)
                    logger.debug(
                        "batch_embedded",
                        batch_index=i // self._batch_size,
                        batch_size=len(batch),
                    )
                    break  
                except Exception as exc:
                    error_str = str(exc)
                    if "429" in error_str or "rate" in error_str.lower():
                        wait_time = 2 ** attempt * 15  
                        logger.warning(
                            "rate_limited",
                            batch_start=i,
                            attempt=attempt,
                            wait_seconds=wait_time,
                        )
                        time.sleep(wait_time)
                        if attempt == max_retries:
                            logger.error("embedding_error_final", batch_start=i, error=error_str)
                            all_embeddings.extend(
                                [[0.0] * self.dimension for _ in batch]
                            )
                    else:
                        logger.error("embedding_error", batch_start=i, error=error_str)
                        all_embeddings.extend(
                            [[0.0] * self.dimension for _ in batch]
                        )
                        break


            if i + self._batch_size < len(texts):
                time.sleep(2)

        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string (uses ``search_query`` input type)."""

        cache_key = self._cache_key(query)
        if self._redis:
            cached = self._get_cached(cache_key)
            if cached is not None:
                logger.debug("embedding_cache_hit", query=query[:50])
                return cached

        embeddings = self.embed_texts([query], input_type="search_query")
        result = embeddings[0]


        if self._redis:
            self._set_cached(cache_key, result)

        return result

    def embed_chunks(self, chunks: list[TextChunk]) -> list[dict]:
        """Embed chunks and return a list of dicts ready for Pinecone upsert."""
        texts = [c.text for c in chunks]
        embeddings = self.embed_texts(texts, input_type="search_document")

        vectors = []
        for chunk, embedding in zip(chunks, embeddings):

            clean_meta = {}
            for k, v in chunk.metadata.items():
                if v is None:
                    clean_meta[k] = ""
                elif isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                elif isinstance(v, list):
                    clean_meta[k] = [str(item) for item in v]
                else:
                    clean_meta[k] = str(v)
            clean_meta["text"] = chunk.text[:1000]  

            vectors.append({
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": clean_meta,
            })

        logger.info("chunks_embedded", count=len(vectors))
        return vectors


    @staticmethod
    def _cache_key(text: str) -> str:
        h = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"{CACHE_PREFIX_EMBEDDING}{h}"

    def _get_cached(self, key: str) -> Optional[list[float]]:
        try:
            data = self._redis.get(key)  
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def _set_cached(self, key: str, value: list[float]) -> None:
        try:
            settings = get_settings()
            self._redis.setex(key, settings.redis_ttl, json.dumps(value))  
        except Exception:
            pass
