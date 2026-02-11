"""
DP World RAG Chatbot — Response Formatter.

Cleans, sanitises, and enriches LLM responses before sending to the user.
"""

from __future__ import annotations

import re
from typing import Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


class ResponseFormatter:
    """Format and sanitize LLM responses."""

    def format_response(
        self,
        response: str,
        sources: Optional[list[str]] = None,
        include_sources: bool = True,
    ) -> str:
        """
        Clean up and format the LLM response.

        Parameters
        ----------
        response : str
            Raw LLM output.
        sources : list[str], optional
            Source URLs to append.
        include_sources : bool
            Whether to append source references.

        Returns
        -------
        str
            Formatted response.
        """
        # Clean up the response
        cleaned = self._clean_response(response)

        # Append sources if available
        if include_sources and sources:
            source_section = self._format_sources(sources)
            cleaned = f"{cleaned}\n\n{source_section}"

        return cleaned

    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove artifacts and normalise formatting."""
        # Remove potential system prompt leakage
        patterns_to_remove = [
            r"(?i)^(as an ai|as a language model|i am an ai).*?\n",
            r"(?i)^(system|instructions?|context):.*?\n",
        ]
        for pattern in patterns_to_remove:
            text = re.sub(pattern, "", text)

        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        return text

    @staticmethod
    def _format_sources(sources: list[str]) -> str:
        """Format source URLs into a markdown section."""
        if not sources:
            return ""

        lines = ["---", "📚 **Sources:**"]
        for i, url in enumerate(sources[:5], 1):  # Limit to 5 sources
            # Extract a readable label from the URL
            label = url.rstrip("/").split("/")[-1].replace("-", " ").title()
            if not label or label == "Www.Dpworld.Com":
                label = "DP World"
            lines.append(f"  {i}. [{label}]({url})")

        return "\n".join(lines)

    @staticmethod
    def truncate(text: str, max_length: int = 2000) -> str:
        """Truncate text to max_length, ending at a sentence boundary."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]
        # Try to end at a sentence boundary
        last_period = truncated.rfind(".")
        last_newline = truncated.rfind("\n")
        cut_point = max(last_period, last_newline)

        if cut_point > max_length * 0.7:
            return truncated[: cut_point + 1]
        return truncated + "..."
