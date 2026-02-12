

from __future__ import annotations

import time
from typing import Optional

from pinecone import Pinecone, ServerlessSpec

from config.constants import COHERE_EMBED_DIMENSION
from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)


class PineconeIndexer:
    """Create, populate, and manage a Pinecone serverless vector index."""

    def __init__(self) -> None:
        settings = get_settings()
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.cloud = settings.pinecone_cloud
        self.region = settings.pinecone_region
        self.dimension = COHERE_EMBED_DIMENSION
        self._index = None


    def create_index(self, metric: str = "cosine") -> None:
        """Create the Pinecone index if it doesn't exist."""
        existing = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name in existing:
            logger.info("index_exists", name=self.index_name)
            return

        logger.info("creating_index", name=self.index_name, dimension=self.dimension)
        self.pc.create_index(
            name=self.index_name,
            dimension=self.dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=self.cloud, region=self.region),
        )


        while not self.pc.describe_index(self.index_name).status["ready"]:
            logger.info("waiting_for_index")
            time.sleep(2)

        logger.info("index_created", name=self.index_name)

    def get_index(self):
        """Return the Pinecone Index object."""
        if self._index is None:
            self._index = self.pc.Index(self.index_name)
        return self._index

    def upsert_vectors(
        self,
        vectors: list[dict],
        namespace: str = "",
        batch_size: int = 100,
    ) -> int:
        """
        Upsert vectors into Pinecone.

        Parameters
        ----------
        vectors : list[dict]
            Each dict must have ``id``, ``values``, and ``metadata``.
        namespace : str
            Optional Pinecone namespace.
        batch_size : int
            Number of vectors per upsert call.

        Returns
        -------
        int
            Total vectors upserted.
        """
        index = self.get_index()
        total = 0

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            upsert_data = [
                (v["id"], v["values"], v["metadata"]) for v in batch
            ]
            index.upsert(vectors=upsert_data, namespace=namespace)
            total += len(batch)
            logger.debug("batch_upserted", batch=i // batch_size + 1, count=len(batch))

        logger.info("upsert_complete", total_vectors=total)
        return total

    def get_stats(self) -> dict:
        """Return index statistics."""
        index = self.get_index()
        stats = index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": {
                ns: info.vector_count
                for ns, info in (stats.namespaces or {}).items()
            },
        }

    def delete_all(self, namespace: str = "") -> None:
        """Delete all vectors in the given namespace."""
        index = self.get_index()
        index.delete(delete_all=True, namespace=namespace)
        logger.warning("all_vectors_deleted", namespace=namespace or "(default)")
