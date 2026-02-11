"""
DP World RAG Chatbot — Chat Manager.

Main orchestrator that ties retrieval, generation, guardrails, 
and session management together into a single chat flow.

Supports:
- Chain-of-Thought (CoT) prompting
- Configurable temperature & top_p (generation parameters)
- Returning retrieved chunks for UI transparency
"""

from __future__ import annotations

import uuid
from typing import Optional

from config.constants import ASSISTANT_ROLE, SYSTEM_ROLE, USER_ROLE
from config.logging_config import get_logger
from src.chat.history_manager import HistoryManager
from src.chat.session_manager import Session, SessionManager
from src.generation.groq_client import GroqClient
from src.generation.guardrails import Guardrails
from src.generation.prompt_templates import (
    CONVERSATION_RAG_TEMPLATE,
    NO_CONTEXT_RESPONSE,
    RAG_QUERY_TEMPLATE,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)
from src.generation.response_formatter import ResponseFormatter
from src.retrieval.query_engine import QueryEngine

logger = get_logger(__name__)


class ChatManager:
    """Orchestrate the full chat pipeline: validate → retrieve → generate → guard."""

    def __init__(
        self,
        query_engine: Optional[QueryEngine] = None,
        groq_client: Optional[GroqClient] = None,
        session_manager: Optional[SessionManager] = None,
        history_manager: Optional[HistoryManager] = None,
        guardrails: Optional[Guardrails] = None,
        formatter: Optional[ResponseFormatter] = None,
    ) -> None:
        self.query_engine = query_engine or QueryEngine()
        self.llm = groq_client or GroqClient()
        self.session_manager = session_manager or SessionManager()
        self.history_manager = history_manager or HistoryManager()
        self.guardrails = guardrails or Guardrails()
        self.formatter = formatter or ResponseFormatter()

    async def start_session(self) -> dict:
        """Create a new chat session and return session info + welcome message."""
        session = self.session_manager.create_session()
        return {
            "session_id": session.session_id,
            "message": WELCOME_MESSAGE,
        }

    async def chat(
        self,
        session_id: str,
        user_message: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> dict:
        """
        Process a chat message end-to-end.

        Parameters
        ----------
        session_id : str
            Active session identifier.
        user_message : str
            The user's query.
        temperature : float, optional
            Override generation temperature (0.0=factual, 0.8=creative).
        top_p : float, optional
            Override nucleus sampling parameter.

        Returns
        -------
        dict
            ``message_id``, ``response``, ``sources``, ``session_id``,
            ``retrieved_chunks``, ``generation_params``
        """
        message_id = str(uuid.uuid4())

        # 1. Input guardrails
        input_check = self.guardrails.check_input(user_message)
        if not input_check.is_safe:
            return {
                "message_id": message_id,
                "response": input_check.reason,
                "sources": [],
                "session_id": session_id,
                "retrieved_chunks": [],
                "generation_params": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "blocked": True,
                },
            }

        # 2. Validate / create session
        session = self.session_manager.get_session(session_id)
        if session is None:
            session = self.session_manager.create_session()
            session_id = session.session_id

        # 3. Save user message to history
        self.history_manager.add_message(session_id, USER_ROLE, user_message)

        # 4. Retrieve context + raw chunks for UI display
        retrieved_chunks = []
        try:
            retrieval_result = await self.query_engine.process_query(user_message)
            context = retrieval_result.get("context", "")
            sources = retrieval_result.get("sources", [])
            # Extract raw retrieved chunks for transparency
            for r in retrieval_result.get("results", []):
                retrieved_chunks.append({
                    "text": r.get("text", r.get("metadata", {}).get("text", ""))[:500],
                    "score": round(r.get("score", 0), 4),
                    "source": r.get("metadata", {}).get("source_url", r.get("source", "")),
                    "title": r.get("metadata", {}).get("title", ""),
                })
        except Exception as exc:
            logger.error("retrieval_error", error=str(exc))
            context = ""
            sources = []

        # 5. Build LLM messages (with CoT-enhanced prompts)
        messages = self._build_messages(session_id, user_message, context)

        # 6. Generate response with configurable parameters
        effective_temp = temperature if temperature is not None else self.llm.temperature
        effective_top_p = top_p

        try:
            if context:
                raw_response = self.llm.chat_completion(
                    messages,
                    temperature=effective_temp,
                    top_p=effective_top_p,
                )
            else:
                raw_response = NO_CONTEXT_RESPONSE
        except Exception as exc:
            logger.error("generation_error", error=str(exc))
            raw_response = (
                "I'm sorry, I'm experiencing a temporary issue. "
                "Please try again in a moment."
            )
            sources = []

        # 7. Output guardrails
        output_check = self.guardrails.check_output(raw_response, context)
        if not output_check.is_safe:
            raw_response = (
                "I apologize, but I couldn't generate a proper response. "
                "Please try rephrasing your question."
            )
        elif output_check.modified_text:
            raw_response = output_check.modified_text

        # 8. Format response
        formatted = self.formatter.format_response(raw_response, sources)

        # 9. Save assistant response to history
        self.history_manager.add_message(session_id, ASSISTANT_ROLE, formatted)

        # 10. Update session
        self.session_manager.update_session(session)

        logger.info(
            "chat_complete",
            session_id=session_id,
            message_id=message_id,
            has_context=bool(context),
            num_sources=len(sources),
            num_chunks=len(retrieved_chunks),
            temperature=effective_temp,
            top_p=effective_top_p,
        )

        return {
            "message_id": message_id,
            "response": formatted,
            "sources": sources,
            "session_id": session_id,
            "retrieved_chunks": retrieved_chunks,
            "generation_params": {
                "temperature": effective_temp,
                "top_p": effective_top_p,
                "model": self.llm.model,
            },
        }

    def _build_messages(
        self,
        session_id: str,
        user_message: str,
        context: str,
    ) -> list[dict[str, str]]:
        """Build the LLM messages list with system prompt, history, and context."""
        messages = [{"role": SYSTEM_ROLE, "content": SYSTEM_PROMPT}]

        # Add conversation history (excluding the current message)
        history = self.history_manager.get_messages_for_llm(session_id)
        # Exclude the last message as we'll add it in the user prompt
        if history and history[-1]["role"] == USER_ROLE:
            history = history[:-1]
        messages.extend(history)

        # Build user prompt with context (CoT-enhanced templates)
        if context:
            formatted_history = self.history_manager.get_formatted_history(
                session_id, last_n=3
            )
            if formatted_history:
                user_prompt = CONVERSATION_RAG_TEMPLATE.format(
                    context=context,
                    history=formatted_history,
                    question=user_message,
                )
            else:
                user_prompt = RAG_QUERY_TEMPLATE.format(
                    context=context,
                    question=user_message,
                )
        else:
            user_prompt = user_message

        messages.append({"role": USER_ROLE, "content": user_prompt})
        return messages

    async def get_history(self, session_id: str) -> list[dict]:
        """Get chat history for a session."""
        history = self.history_manager.get_history(session_id)
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
            }
            for m in history
        ]

    async def clear_session(self, session_id: str) -> bool:
        """Clear a session and its history."""
        self.history_manager.clear_history(session_id)
        return self.session_manager.delete_session(session_id)
