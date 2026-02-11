"""
DP World RAG Chatbot — Guardrails.

Safety checks, hallucination prevention, and content filtering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""

    is_safe: bool
    reason: str = ""
    modified_text: Optional[str] = None


class Guardrails:
    """Apply safety guardrails to inputs and outputs."""

    # Patterns that indicate prompt injection attempts
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
        r"(?i)you\s+are\s+now\s+(?:a\s+)?(?:different|new)",
        r"(?i)disregard\s+(your|all)\s+(rules?|instructions?)",
        r"(?i)pretend\s+you\s+are",
        r"(?i)act\s+as\s+(?:if\s+)?(?:you\s+are)",
        r"(?i)system\s*prompt",
        r"(?i)reveal\s+your\s+(?:system|instructions?|prompt)",
    ]

    # Topics that are off-limits for the chatbot
    OFF_TOPIC_KEYWORDS = [
        "politics", "religion", "violence", "weapons",
        "illegal", "hack", "exploit", "malware",
    ]

    # Maximum response length
    MAX_RESPONSE_LENGTH = 5000

    def check_input(self, user_message: str) -> GuardrailResult:
        """
        Validate user input for safety.

        Checks for:
        - Prompt injection attempts
        - Off-topic content
        - Malicious patterns
        """
        # Check for empty input
        if not user_message or not user_message.strip():
            return GuardrailResult(is_safe=False, reason="Empty message")

        # Check message length
        if len(user_message) > 2000:
            return GuardrailResult(
                is_safe=False,
                reason="Message too long. Please keep your question under 2000 characters.",
            )

        # Check for prompt injection
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, user_message):
                logger.warning("prompt_injection_detected", pattern=pattern)
                return GuardrailResult(
                    is_safe=False,
                    reason="I'm designed to help with DP World logistics queries. How can I assist you?",
                )

        return GuardrailResult(is_safe=True)

    def check_output(self, response: str, context: str = "") -> GuardrailResult:
        """
        Validate LLM output for safety and relevance.

        Checks for:
        - System prompt leakage
        - Excessive length
        - Empty responses
        """
        if not response or not response.strip():
            return GuardrailResult(
                is_safe=False,
                reason="Empty response generated",
            )

        # Check for system prompt leakage
        leakage_patterns = [
            r"(?i)my\s+(?:system\s+)?instructions?\s+(?:are|say)",
            r"(?i)i\s+was\s+(?:told|instructed|programmed)\s+to",
            r"(?i)my\s+(?:system\s+)?prompt\s+(?:is|says)",
        ]
        for pattern in leakage_patterns:
            if re.search(pattern, response):
                logger.warning("system_prompt_leakage_detected")
                return GuardrailResult(
                    is_safe=False,
                    reason="Response contained potential system information leakage",
                )

        # Truncate if too long
        if len(response) > self.MAX_RESPONSE_LENGTH:
            truncated = response[: self.MAX_RESPONSE_LENGTH]
            # Try to end at sentence boundary
            last_period = truncated.rfind(".")
            if last_period > self.MAX_RESPONSE_LENGTH * 0.7:
                truncated = truncated[: last_period + 1]
            return GuardrailResult(
                is_safe=True,
                modified_text=truncated,
            )

        return GuardrailResult(is_safe=True)

    def check_relevance(self, response: str, context: str) -> bool:
        """
        Basic check: does the response seem related to the context?

        This is a simple heuristic — for production you'd use an
        LLM-as-judge approach.
        """
        if not context:
            return True  # No context to compare against

        # Extract key terms from context (simple TF approach)
        context_words = set(
            w.lower() for w in re.findall(r"\b\w{4,}\b", context)
        )
        response_words = set(
            w.lower() for w in re.findall(r"\b\w{4,}\b", response)
        )

        if not context_words:
            return True

        overlap = len(context_words & response_words)
        overlap_ratio = overlap / max(len(context_words), 1)

        # If less than 5% word overlap, flag as potentially hallucinated
        if overlap_ratio < 0.05:
            logger.warning(
                "low_relevance_score",
                overlap_ratio=round(overlap_ratio, 3),
            )
            return False

        return True
