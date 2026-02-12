

from __future__ import annotations

from typing import AsyncIterator, Optional

from groq import Groq

from config.logging_config import get_logger
from config.settings import get_settings

logger = get_logger(__name__)


class GroqClient:
    """Wrapper for the Groq chat completion API."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model_name
        self.max_tokens = settings.groq_max_tokens
        self.temperature = settings.groq_temperature

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate a chat completion.

        Parameters
        ----------
        messages : list[dict]
            OpenAI-style messages (``role`` + ``content``).
        temperature : float, optional
            Override default temperature (0.0=deterministic, 1.0=creative).
        max_tokens : int, optional
            Override default max tokens.
        top_p : float, optional
            Nucleus sampling parameter (0.0-1.0).
        stream : bool
            If True, use streaming (returns full text after stream completes).

        Returns
        -------
        str
            The assistant's response text.
        """
        try:
            kwargs = dict(
                model=self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=stream,
            )
            if top_p is not None:
                kwargs["top_p"] = top_p

            response = self.client.chat.completions.create(**kwargs)

            if stream:

                chunks = []
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        chunks.append(delta.content)
                result = "".join(chunks)
            else:
                result = response.choices[0].message.content or ""

            logger.info(
                "llm_completion",
                model=self.model,
                input_messages=len(messages),
                output_length=len(result),
            )
            return result

        except Exception as exc:
            logger.error("llm_completion_error", error=str(exc))
            raise

    def stream_completion(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
    ):
        """
        Return a streaming generator of response chunks.

        Yields
        ------
        str
            Individual text chunks from the stream.
        """
        try:
            kwargs = dict(
                model=self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
            )
            if top_p is not None:
                kwargs["top_p"] = top_p

            response = self.client.chat.completions.create(**kwargs)

            for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content

        except Exception as exc:
            logger.error("llm_stream_error", error=str(exc))
            raise
