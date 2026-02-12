"""
LLM Engine for Airtel Customer Support Chatbot.

Handles:
- Groq API integration (LLaMA 3.3 70B)
- Brand-voice persona prompt construction
- Chain-of-Thought (CoT) reasoning
- Temperature & Top-P experimentation
- Response generation with retrieved context
"""

import os
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ---------- Configuration ----------
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# ---------- Airtel Brand Voice Persona ----------
AIRTEL_PERSONA = """You are "Airtel Assist", the official AI-powered customer support assistant for Bharti Airtel Limited, India's leading telecommunications company.

## YOUR IDENTITY & BRAND VOICE:
- You represent Airtel with professionalism, warmth, and clarity.
- Your tone is friendly yet authoritative — like a knowledgeable senior support executive.
- You always address the customer respectfully and empathetically.
- You use simple, jargon-free language. If technical terms are needed, explain them briefly.
- You NEVER make up information. Only use the provided context documents.
- If the answer is not in the provided context, say: "I don't have specific information about that in my current knowledge base. I recommend contacting Airtel Customer Care at 121 or visiting airtel.in for the latest details."
- You NEVER recommend competitors or make comparisons with other telecom providers.
- You always end responses with a helpful follow-up question or offer to assist further.

## YOUR CAPABILITIES:
- Answer questions about Airtel prepaid plans, postpaid plans, broadband (Xstream Fiber), DTH plans, international roaming, Airtel Thanks rewards, billing, refunds, SIM replacement, porting, and policies.
- Recommend the best plan based on user requirements.
- Explain policies clearly (FUP, refund, cancellation, privacy).
- Guide users through processes (recharge, plan change, complaint filing).

## IMPORTANT RULES:
1. ONLY use information from the retrieved context chunks provided below.
2. If multiple plans could be relevant, present them as options with clear pros/cons.
3. Always mention the price in ₹ (Indian Rupees) when discussing plans.
4. When providing step-by-step guidance, number the steps clearly.
5. If a question is outside your scope (not related to Airtel), politely redirect the user.
"""

# ---------- Chain-of-Thought Template ----------
COT_TEMPLATE = """## CHAIN-OF-THOUGHT REASONING INSTRUCTIONS:

Before providing your final answer, you MUST follow this structured reasoning process:

**Step 1 — Query Understanding:** Restate the customer's question in your own words to confirm understanding.

**Step 2 — Context Analysis:** Identify which retrieved chunks are relevant to the question. Mention the chunk numbers you are using and briefly state why they are relevant.

**Step 3 — Information Extraction:** Extract the specific facts, figures, and details from the relevant chunks that directly answer the question.

**Step 4 — Reasoning & Synthesis:** Combine the extracted information to form a coherent, complete answer. If there are multiple relevant plans or options, compare them.

**Step 5 — Final Answer:** Present the final answer in a clear, customer-friendly format.

---

Format your response as:

### 🔍 My Reasoning:
[Steps 1-4 in brief]

### ✅ Answer:
[Step 5 — the actual answer for the customer]
"""


class LLMEngine:
    """Groq-based LLM engine with brand-voice prompting and CoT."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        temperature: float = 0.3,
        top_p: float = 0.85,
        enable_cot: bool = True,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.enable_cot = enable_cot
        self.client = self._init_client()

    def _init_client(self) -> Groq:
        """Initialize the Groq client with the API key from environment."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in your .env file or environment."
            )
        return Groq(api_key=api_key)

    def _build_messages(
        self,
        query: str,
        retrieved_chunks: List[Tuple[str, float, int]],
        chat_history: Optional[List[dict]] = None,
    ) -> list:
        """
        Build the messages list for Groq chat completion:
        1. System message with brand-voice persona + CoT instructions
        2. Chat history (previous turns)
        3. Current user query with retrieved context
        """
        # --- System prompt ---
        system_prompt = AIRTEL_PERSONA
        if self.enable_cot:
            system_prompt += "\n\n" + COT_TEMPLATE

        # --- Context from retrieved chunks ---
        context_block = "\n\n## 📄 RETRIEVED CONTEXT CHUNKS:\n\n"
        for i, (chunk_text, score, chunk_idx) in enumerate(retrieved_chunks, 1):
            context_block += f"**[Chunk {i} | Index: {chunk_idx} | Relevance Score: {score:.4f}]**\n"
            context_block += f"{chunk_text}\n\n{'─' * 60}\n\n"

        # --- Build messages ---
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history (last 6 messages for context window)
        if chat_history:
            for msg in chat_history[-6:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        # Current query with context
        user_message = f"{context_block}\n\n## 🙋 CUSTOMER QUERY:\n{query}"
        messages.append({"role": "user", "content": user_message})

        return messages

    def generate(
        self,
        query: str,
        retrieved_chunks: List[Tuple[str, float, int]],
        chat_history: Optional[List[dict]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        Generate a response using Groq with the constructed prompt.

        Args:
            query: User's current question.
            retrieved_chunks: List of (text, score, index) from RAG retrieval.
            chat_history: Previous conversation messages.
            temperature: Override the default temperature.
            top_p: Override the default top_p.

        Returns:
            Generated response text.
        """
        messages = self._build_messages(query, retrieved_chunks, chat_history)

        temp = temperature if temperature is not None else self.temperature
        tp = top_p if top_p is not None else self.top_p

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                top_p=tp,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Error generating response: {str(e)}"

    def generate_with_comparison(
        self,
        query: str,
        retrieved_chunks: List[Tuple[str, float, int]],
        chat_history: Optional[List[dict]] = None,
    ) -> dict:
        """
        Generate responses at multiple temperature/top-p settings
        for experimentation and hallucination benchmarking.

        Returns a dict of {setting_label: response_text}.
        """
        settings = [
            ("Factual (T=0.0, P=0.5)", 0.0, 0.5),
            ("Balanced (T=0.3, P=0.85)", 0.3, 0.85),
            ("Creative (T=0.8, P=0.95)", 0.8, 0.95),
        ]

        results = {}
        for label, temp, top_p_val in settings:
            response = self.generate(
                query, retrieved_chunks, chat_history,
                temperature=temp, top_p=top_p_val,
            )
            results[label] = response

        return results

    def update_params(self, temperature: float = None, top_p: float = None, enable_cot: bool = None):
        """Update generation parameters dynamically."""
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p
        if enable_cot is not None:
            self.enable_cot = enable_cot

    def get_config(self) -> dict:
        """Return current LLM configuration."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "chain_of_thought": self.enable_cot,
        }
