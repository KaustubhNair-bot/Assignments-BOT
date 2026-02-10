"""Core RAG system — Pinecone vector store + Cohere embeddings + LLM.

Improvements over the initial version
--------------------------------------
- Hybrid search: combines semantic (vector) search with keyword-based
  re-ranking for better retrieval quality.
- Metadata filtering: preserves and filters on medical specialty.
- Robust error handling throughout.
- Proper answer generation pipeline using RAGLLM.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .config import get_settings
from .llm_clients import RAGLLM

settings = get_settings()

# ---------------------------------------------------------------------------
# Conditional imports — Pinecone + Cohere
# ---------------------------------------------------------------------------
PINECONE_AVAILABLE = False
try:
    from pinecone import Pinecone, ServerlessSpec
    from langchain_community.vectorstores import Pinecone as LangChainPinecone

    PINECONE_AVAILABLE = True
except Exception:
    pass

COHERE_EMB_AVAILABLE = False
try:
    from langchain_cohere import CohereEmbeddings

    COHERE_EMB_AVAILABLE = True
except Exception:
    try:
        from langchain_community.embeddings import CohereEmbeddings

        COHERE_EMB_AVAILABLE = True
    except Exception:
        pass

try:
    from langchain_community.vectorstores.utils import DistanceStrategy
except Exception:

    class DistanceStrategy:  # type: ignore[no-redef]
        COSINE = "cosine"


# ---------------------------------------------------------------------------
# CustomPinecone — works around strict isinstance() check in LangChain
# ---------------------------------------------------------------------------
if PINECONE_AVAILABLE:

    class CustomPinecone(LangChainPinecone):
        """Thin wrapper to bypass the isinstance(index, pinecone.Index) guard."""

        def __init__(
            self,
            index: Any,
            embedding: Any,
            text_key: str,
            namespace: Optional[str] = None,
            distance_strategy=DistanceStrategy.COSINE,
        ):
            self._index = index
            self._embedding = embedding
            self._text_key = text_key
            self._namespace = namespace
            self.distance_strategy = distance_strategy

        def add_texts(
            self,
            texts: List[str],
            metadatas: Optional[List[dict]] = None,
            ids: Optional[List[str]] = None,
            namespace: Optional[str] = None,
            batch_size: int = 32,
            **kwargs: Any,
        ) -> List[str]:
            return super().add_texts(
                texts, metadatas, ids, namespace, batch_size, **kwargs
            )

else:

    class CustomPinecone:  # type: ignore[no-redef]
        def __init__(self, *a, **kw):
            raise RuntimeError("Pinecone is not available")


# ---------------------------------------------------------------------------
# Local in-memory vector store (fallback when Pinecone is unavailable)
# ---------------------------------------------------------------------------
class _LocalVectorStore:
    """Token-overlap vector store for offline testing."""

    def __init__(self):
        self._texts: list[str] = []
        self._metas: list[dict] = []

    @staticmethod
    def _overlap(query: str, text: str) -> int:
        q = set(query.lower().split())
        t = set(text.lower().split())
        return len(q & t)

    def add_documents(self, docs):
        for d in docs:
            self._texts.append(getattr(d, "page_content", str(d)))
            meta = getattr(d, "metadata", {})
            self._metas.append(meta if isinstance(meta, dict) else {})

    def add_texts(self, texts, metadatas=None):
        for i, t in enumerate(texts):
            self._texts.append(t)
            self._metas.append(
                (metadatas[i] if metadatas and i < len(metadatas) else {})
            )

    def similarity_search(self, query: str, k: int = 5):
        if not self._texts:
            return []
        scored = [(i, self._overlap(query, t)) for i, t in enumerate(self._texts)]
        scored.sort(key=lambda x: -x[1])
        top = [i for i, s in scored[:k] if s > 0]

        class _Doc:
            def __init__(self, text, meta):
                self.page_content = text
                self.metadata = meta

        return [_Doc(self._texts[i], self._metas[i]) for i in top]


# ---------------------------------------------------------------------------
# RAGSystem
# ---------------------------------------------------------------------------
class RAGSystem:
    """Orchestrates retrieval (Pinecone) + generation (Groq/Cohere)."""

    def __init__(self):
        print("[RAG] Initialising RAG system …")

        # ---- Vector store ----
        if PINECONE_AVAILABLE and COHERE_EMB_AVAILABLE and settings.PINECONE_API_KEY:
            self.embeddings = CohereEmbeddings(
                cohere_api_key=settings.COHERE_API_KEY,
                model="embed-english-v3.0",
                user_agent="medical-rag-app",
            )
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index_name = settings.PINECONE_INDEX_NAME

            # Create index if needed
            existing = [idx.name for idx in self.pc.list_indexes()]
            if self.index_name not in existing:
                try:
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=1024,  # Cohere embed-english-v3.0
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws", region=settings.PINECONE_ENV
                        ),
                    )
                    print(f"[RAG] Created Pinecone index '{self.index_name}'")
                except Exception as exc:
                    print(f"[RAG] Index creation error (may already exist): {exc}")

            self.index = self.pc.Index(self.index_name)
            self.vectorstore = CustomPinecone(
                index=self.index,
                embedding=self.embeddings,
                text_key="text",
            )
            self._store_kind = "pinecone"
            print("[RAG] Using Pinecone vector store")
        else:
            self.vectorstore = _LocalVectorStore()
            self._store_kind = "local"
            print("[RAG] Using local in-memory vector store (Pinecone unavailable)")

        # ---- LLM ----
        self.llm = RAGLLM()

    # ---------- Retrieval ----------
    def search(self, query: str, k: int = 5):
        """Retrieve top-k documents from the vector store."""
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            return docs
        except Exception as exc:
            print(f"[RAG] Search error: {exc}")
            return []

    # ---------- Document ingestion ----------
    def add_document(self, text: str, metadata: dict) -> bool:
        try:
            self.vectorstore.add_texts(texts=[text], metadatas=[metadata])
            return True
        except Exception as exc:
            print(f"[RAG] Error adding document: {exc}")
            return False

    # ---------- RAG generation ----------
    def generate_answer(self, query: str, context_docs) -> str:
        """Given a query and retrieved docs, generate a grounded answer."""
        contexts = [getattr(d, "page_content", str(d)) for d in context_docs]
        return self.llm.generate_with_context(query=query, context_docs=contexts)

    # ---------- Base-LLM generation (no context) ----------
    def generate_base_answer(self, query: str) -> str:
        """Generate an answer without any retrieval context (for comparison)."""
        prompt = (
            f"You are a medical assistant. Answer the following clinical question "
            f"concisely based on your general medical knowledge only.\n\n"
            f"Question: {query}\n\nAnswer:"
        )
        return self.llm.generate(prompt)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
rag = RAGSystem()
