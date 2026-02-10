"""
LLM Engine - Groq API Integration
Handles LLM calls for generating natural language answers
Uses Groq's fast inference API with Llama models
"""
import os
import time
from typing import Optional, List, Dict
from groq import Groq

from app.config import settings


class LLMEngine:
    """
    LLM Engine for generating natural language answers using Groq API.
    
    Groq provides fast inference for open-source LLMs like Llama-3.
    This is used in two modes:
    1. RAG mode: Generates answers grounded in retrieved medical transcriptions
    2. Base LLM mode: Generates answers without any context (for comparison)
    """
    
    def __init__(self):
        self.client: Optional[Groq] = None
        self.model: str = settings.GROQ_MODEL
        self._initialized = False
    
    def initialize(self):
        """Initialize the Groq client"""
        if self._initialized:
            return
        
        api_key = settings.GROQ_API_KEY
        if not api_key:
            print("WARNING: GROQ_API_KEY not set. LLM features will be disabled.")
            return
        
        self.client = Groq(api_key=api_key)
        self.model = settings.GROQ_MODEL
        self._initialized = True
        print(f"LLM Engine initialized with model: {self.model}")
    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        return self._initialized and self.client is not None
    
    def generate_rag_answer(
        self,
        query: str,
        retrieved_contexts: List[Dict],
        max_tokens: int = 1024
    ) -> Dict:
        """
        Generate an answer using retrieved context (RAG mode).
        
        The LLM is given the retrieved medical transcriptions as context
        and generates a grounded answer based on them.
        
        Args:
            query: The user's medical query
            retrieved_contexts: List of retrieved documents from FAISS search
            max_tokens: Maximum tokens in the response
            
        Returns:
            Dict with answer, model info, and timing
        """
        if not self.is_available():
            return {"error": "LLM not available. Set GROQ_API_KEY in .env"}
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_contexts, 1):
            specialty = doc.get("specialty", "Unknown")
            sample_name = doc.get("sample_name", "Unknown")
            transcription = doc.get("transcription", "")
            # Truncate very long transcriptions to fit context window
            if len(transcription) > 2000:
                transcription = transcription[:2000] + "..."
            
            context_parts.append(
                f"--- Case {i} ---\n"
                f"Specialty: {specialty}\n"
                f"Case Name: {sample_name}\n"
                f"Transcription: {transcription}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        system_prompt = (
            "You are a medical AI assistant helping doctors search through patient records. "
            "You are provided with relevant medical transcription cases retrieved from a database. "
            "Based ONLY on the provided cases, answer the doctor's query. "
            "Be specific, cite case numbers when referencing information, and highlight "
            "relevant findings, diagnoses, and treatments from the cases. "
            "If the provided cases do not contain enough information to answer the query, "
            "clearly state that. Do NOT make up medical information not found in the cases."
        )
        
        user_prompt = (
            f"Query: {query}\n\n"
            f"Retrieved Medical Cases:\n{context_text}\n\n"
            f"Based on the above retrieved cases, provide a comprehensive answer to the query. "
            f"Reference specific cases and highlight key medical findings."
        )
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # Low temperature for factual responses
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            answer = response.choices[0].message.content
            usage = response.usage
            
            return {
                "answer": answer,
                "model": self.model,
                "mode": "rag",
                "llm_time_ms": round(elapsed_ms, 2),
                "tokens_used": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0
                },
                "num_contexts": len(retrieved_contexts)
            }
        except Exception as e:
            return {"error": f"LLM generation failed: {str(e)}"}
    
    def generate_base_answer(
        self,
        query: str,
        max_tokens: int = 1024
    ) -> Dict:
        """
        Generate an answer using only the base LLM (no context).
        
        This is used for comparison against the RAG-augmented answers
        to demonstrate the value of retrieval augmentation.
        
        Args:
            query: The user's medical query
            max_tokens: Maximum tokens in the response
            
        Returns:
            Dict with answer, model info, and timing
        """
        if not self.is_available():
            return {"error": "LLM not available. Set GROQ_API_KEY in .env"}
        
        system_prompt = (
            "You are a medical AI assistant. Answer the doctor's query based on your "
            "general medical knowledge. Provide specific and detailed information "
            "about the medical conditions, procedures, or symptoms mentioned."
        )
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            answer = response.choices[0].message.content
            usage = response.usage
            
            return {
                "answer": answer,
                "model": self.model,
                "mode": "base_llm",
                "llm_time_ms": round(elapsed_ms, 2),
                "tokens_used": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0
                },
                "num_contexts": 0
            }
        except Exception as e:
            return {"error": f"LLM generation failed: {str(e)}"}


# Global LLM engine instance
llm_engine = LLMEngine()
