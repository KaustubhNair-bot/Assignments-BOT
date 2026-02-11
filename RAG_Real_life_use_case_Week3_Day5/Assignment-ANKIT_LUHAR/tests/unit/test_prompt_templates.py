"""
Tests — Prompt Templates.

Validates brand voice persona, Chain-of-Thought requirements,
and generation parameter presets.
"""

from __future__ import annotations

import pytest

from src.generation.prompt_templates import (
    CONVERSATION_RAG_TEMPLATE,
    GENERATION_PRESETS,
    NO_CONTEXT_RESPONSE,
    RAG_QUERY_TEMPLATE,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)


class TestPromptTemplates:
    """Tests for prompt templates."""

    # ── Brand Voice Tests ───────────────────────────────────
    def test_system_prompt_not_empty(self):
        """System prompt should have substantial content."""
        assert len(SYSTEM_PROMPT) > 200
        assert "DP World" in SYSTEM_PROMPT

    def test_system_prompt_has_brand_voice(self):
        """System prompt should define a strict brand voice persona."""
        assert "Senior Logistics Consultant" in SYSTEM_PROMPT
        assert "brand" in SYSTEM_PROMPT.lower()
        assert "persona" in SYSTEM_PROMPT.lower() or "voice" in SYSTEM_PROMPT.lower()

    def test_system_prompt_context_only(self):
        """System prompt should enforce context-only answers."""
        assert "ONLY" in SYSTEM_PROMPT
        assert "context" in SYSTEM_PROMPT.lower()
        assert "fabricate" in SYSTEM_PROMPT.lower() or "hallucin" in SYSTEM_PROMPT.lower()

    def test_system_prompt_competitor_policy(self):
        """System prompt should have competitor discussion policy."""
        assert "competitor" in SYSTEM_PROMPT.lower()

    # ── Chain-of-Thought Tests ──────────────────────────────
    def test_system_prompt_has_cot(self):
        """System prompt should require Chain-of-Thought reasoning."""
        assert "Chain-of-Thought" in SYSTEM_PROMPT
        assert "Retrieval Analysis" in SYSTEM_PROMPT
        assert "Relevance" in SYSTEM_PROMPT

    def test_rag_template_has_cot(self):
        """RAG template should enforce CoT reasoning steps."""
        assert "Chain-of-Thought" in RAG_QUERY_TEMPLATE
        assert "Retrieval Analysis" in RAG_QUERY_TEMPLATE
        assert "Relevance" in RAG_QUERY_TEMPLATE

    def test_conversation_template_has_cot(self):
        """Conversation template should also enforce CoT."""
        assert "Chain-of-Thought" in CONVERSATION_RAG_TEMPLATE
        assert "Retrieval Analysis" in CONVERSATION_RAG_TEMPLATE

    # ── Template Formatting Tests ───────────────────────────
    def test_rag_template_has_placeholders(self):
        """RAG template should have context and question placeholders."""
        assert "{context}" in RAG_QUERY_TEMPLATE
        assert "{question}" in RAG_QUERY_TEMPLATE

    def test_rag_template_formatting(self):
        """RAG template should format correctly."""
        formatted = RAG_QUERY_TEMPLATE.format(
            context="DP World operates 80+ terminals.",
            question="How many terminals?",
        )
        assert "DP World operates 80+ terminals" in formatted
        assert "How many terminals" in formatted

    def test_conversation_template_has_history(self):
        """Conversation template should include history placeholder."""
        assert "{history}" in CONVERSATION_RAG_TEMPLATE
        assert "{context}" in CONVERSATION_RAG_TEMPLATE
        assert "{question}" in CONVERSATION_RAG_TEMPLATE

    def test_no_context_response_has_cot(self):
        """No-context response should include CoT analysis."""
        assert "Retrieval Analysis" in NO_CONTEXT_RESPONSE
        assert "dpworld.com" in NO_CONTEXT_RESPONSE

    def test_welcome_message_has_topics(self):
        """Welcome message should list key topics."""
        assert "Port" in WELCOME_MESSAGE
        assert "Container" in WELCOME_MESSAGE
        assert "Tariff" in WELCOME_MESSAGE
        assert "Chain-of-Thought" in WELCOME_MESSAGE

    # ── Generation Presets Tests ────────────────────────────
    def test_presets_exist(self):
        """Generation presets should be defined."""
        assert "factual" in GENERATION_PRESETS
        assert "balanced" in GENERATION_PRESETS
        assert "creative" in GENERATION_PRESETS

    def test_factual_preset(self):
        """Factual preset should have low temperature."""
        preset = GENERATION_PRESETS["factual"]
        assert preset["temperature"] == 0.0
        assert preset["top_p"] <= 0.5
        assert "label" in preset
        assert "description" in preset

    def test_balanced_preset(self):
        """Balanced preset should be moderate."""
        preset = GENERATION_PRESETS["balanced"]
        assert 0.2 <= preset["temperature"] <= 0.5
        assert 0.5 <= preset["top_p"] <= 0.8

    def test_creative_preset(self):
        """Creative preset should have high temperature."""
        preset = GENERATION_PRESETS["creative"]
        assert preset["temperature"] >= 0.7
        assert preset["top_p"] >= 0.8

    def test_all_presets_have_required_keys(self):
        """All presets should have temperature, top_p, label, description."""
        for name, preset in GENERATION_PRESETS.items():
            assert "temperature" in preset, f"{name} missing temperature"
            assert "top_p" in preset, f"{name} missing top_p"
            assert "label" in preset, f"{name} missing label"
            assert "description" in preset, f"{name} missing description"
