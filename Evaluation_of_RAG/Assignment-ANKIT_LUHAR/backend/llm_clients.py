"""LLM client wrappers for the Medical RAG system.

Hierarchy
---------
BaseLLM   – plain generation (no retrieval context). Used for the "base LLM"
            comparison in evaluation.
RAGLLM    – extends BaseLLM with *generate_with_context* which injects
            retrieved documents into the prompt before calling the LLM.

Provider priority: Groq ➜ Cohere ➜ local heuristic fallback.
"""

from __future__ import annotations

import os
from typing import List, Optional

from .config import get_settings

# ---------------------------------------------------------------------------
# Optional imports — graceful degradation
# ---------------------------------------------------------------------------
try:
    from langchain_groq import ChatGroq

    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False

try:
    from langchain_community.llms import Cohere

    COHERE_AVAILABLE = True
except Exception:
    COHERE_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helper: extract plain text from LLM response objects
# ---------------------------------------------------------------------------
def _to_str(resp) -> str:
    """Convert any LangChain response object to a plain string."""
    if isinstance(resp, str):
        return resp.strip()
    # ChatGroq / ChatCohere return AIMessage with .content
    if hasattr(resp, "content"):
        return str(resp.content).strip()
    # Legacy LLMs may return raw text
    return str(resp).strip()


# ---------------------------------------------------------------------------
# BaseLLM — "no context" generation
# ---------------------------------------------------------------------------
class BaseLLM:
    """Wrapper that picks the best available LLM provider."""

    def __init__(self, provider: Optional[str] = None):
        settings = get_settings()
        self.provider = provider or os.getenv("PREFERRED_LLM", "auto")
        self.kind: str = "local"
        self.client = None

        # 1️⃣  Try Groq first
        if GROQ_AVAILABLE and self.provider in ("groq", "auto") and settings.GROQ_API_KEY:
            try:
                self.client = ChatGroq(
                    api_key=settings.GROQ_API_KEY,
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.3,
                    max_tokens=1024,
                )
                # quick validation — if the key is bogus this will fail later,
                # but at least the object was constructed
                self.kind = "groq"
            except Exception as exc:
                print(f"[LLM] Groq init failed: {exc}")
                self.client = None

        # 2️⃣  Cohere fallback
        if self.client is None and COHERE_AVAILABLE and settings.COHERE_API_KEY:
            try:
                self.client = Cohere(cohere_api_key=settings.COHERE_API_KEY)
                self.kind = "cohere"
            except Exception as exc:
                print(f"[LLM] Cohere init failed: {exc}")
                self.client = None

        # 3️⃣  Local heuristic (last resort)
        if self.client is None:
            self.kind = "local"

        print(f"[LLM] Initialized — provider={self.kind}")

    # ----- public API -----
    def generate(self, prompt: str) -> str:
        """Generate a response from a plain prompt (no retrieval context)."""
        if self.kind in ("groq", "cohere"):
            try:
                raw = self.client.invoke(prompt)
                return _to_str(raw)
            except Exception as exc:
                print(f"[LLM] {self.kind} generation error: {exc}")
                # fall through to local
                self.kind = "local"

        # local heuristic
        lines = [ln.strip() for ln in prompt.splitlines() if ln.strip()]
        q = lines[-1] if lines else prompt
        return f"(local-llm) I don't have enough specific information to answer: {q[:240]}"


# ---------------------------------------------------------------------------
# RAGLLM — context-aware generation
# ---------------------------------------------------------------------------
class RAGLLM(BaseLLM):
    """LLM with a generate_with_context method for RAG answers."""

    SYSTEM_PROMPT = (
        "You are a knowledgeable medical assistant. "
        "Use ONLY the provided context documents to answer the user's question. "
        "If the context does not contain enough information, say so explicitly. "
        "Cite relevant details from the context. Be concise and accurate."
    )

    def generate_with_context(self, query: str, context_docs: List[str]) -> str:
        """Build a RAG prompt from context docs and generate an answer."""
        context = "\n\n---\n\n".join(context_docs)
        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"### Retrieved Context\n{context}\n\n"
            f"### Question\n{query}\n\n"
            f"### Answer\n"
        )

        if self.kind == "local":
            snippet = (context[:300] + "…") if len(context) > 300 else context
            return (
                f"(local-llm RAG) Context snippet: {snippet}\n\n"
                f"Answer: Based on the provided cases, {query}"
            )

        return self.generate(prompt)
