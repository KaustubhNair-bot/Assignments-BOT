"""
Prompt Templates for Tesla RAG system.
Enterprise-grade prompt engineering with Tesla brand persona.
"""

from typing import Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


TESLA_SYSTEM_PROMPT = """You are a Tesla Knowledge Assistant and senior engineering analyst.

Your role is to provide accurate, professional, and helpful responses based exclusively on Tesla's official documentation.

CRITICAL GUIDELINES:
1. Answer ONLY using the provided Tesla document context below.
2. If the answer is not present in the context, respond exactly with:
   "I do not have sufficient information from Tesla documents to answer this question."
3. Maintain Tesla's professional, technical, and innovative tone in all responses.
4. Do NOT hallucinate or make up information not present in the context.
5. When citing information, reference the source document when possible.
6. Be precise and concise while being thorough.
7. For technical questions, provide detailed explanations grounded in the documentation.
8. For policy questions, quote relevant sections when appropriate.

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide supporting details from the context
- If multiple sources are relevant, synthesize the information coherently
- End with any important caveats or related information from the documents"""


QUERY_PROMPT_TEMPLATE = """CONTEXT FROM TESLA DOCUMENTS:
{context}

---

USER QUESTION: {query}

Based solely on the Tesla document context provided above, please provide a comprehensive and accurate response."""


class TeslaPromptTemplate:
    """
    Manages prompt templates for Tesla RAG system.
    
    Provides methods to construct prompts with context injection.
    """
    
    def __init__(self, system_prompt: Optional[str] = None):
        """
        Initialize the prompt template.
        
        Args:
            system_prompt: Custom system prompt (uses default if None)
        """
        self.system_prompt = system_prompt or TESLA_SYSTEM_PROMPT
        logger.info("Initialized TeslaPromptTemplate")
    
    def format_prompt(self, query: str, context: str) -> dict:
        """
        Format the complete prompt with context.
        
        Args:
            query: User query
            context: Retrieved context from documents
            
        Returns:
            Dict with 'system' and 'user' prompts
        """
        user_prompt = QUERY_PROMPT_TEMPLATE.format(
            context=context,
            query=query
        )
        
        return {
            'system': self.system_prompt,
            'user': user_prompt
        }
    
    def format_messages(self, query: str, context: str) -> list:
        """
        Format as message list for chat API.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            List of message dicts for chat API
        """
        prompts = self.format_prompt(query, context)
        
        return [
            {"role": "system", "content": prompts['system']},
            {"role": "user", "content": prompts['user']}
        ]
    
    def get_no_context_response(self) -> str:
        """Get the standard response when no relevant context is found."""
        return "I do not have sufficient information from Tesla documents to answer this question."
    
    def format_context_from_chunks(self, chunks: list) -> str:
        """
        Format retrieved chunks into context string.
        
        Args:
            chunks: List of chunk dicts with 'content' and 'metadata'
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get('metadata', {}).get('filename', 'Unknown Document')
            score = chunk.get('similarity_score', 0)
            content = chunk.get('content', '')
            
            context_parts.append(
                f"[Document {i}: {source} (Relevance: {score:.2f})]\n{content}"
            )
        
        return "\n\n" + "="*50 + "\n\n".join(context_parts)
