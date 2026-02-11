"""
RAG Orchestrator for Tesla RAG system.
Combines retrieval and generation into a unified pipeline.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import time

from groq import Groq

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from config.settings import (
    GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, TOP_P, MAX_TOKENS, TOP_K
)
from retrieval.retriever import Retriever
from prompts.templates import TeslaPromptTemplate

logger = get_logger(__name__)


class RAGOrchestrator:
    """
    Orchestrates the RAG pipeline.
    
    Combines retrieval, prompt construction, and LLM generation.
    """
    
    def __init__(
        self,
        retriever: Retriever,
        prompt_template: Optional[TeslaPromptTemplate] = None,
        api_key: Optional[str] = None,
        model: str = GROQ_MODEL,
        temperature: float = TEMPERATURE,
        top_p: float = TOP_P,
        max_tokens: int = MAX_TOKENS
    ):
        """
        Initialize the RAG orchestrator.
        
        Args:
            retriever: Retriever instance
            prompt_template: TeslaPromptTemplate instance
            api_key: Groq API key
            model: LLM model name
            temperature: Generation temperature
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
        """
        self.retriever = retriever
        self.prompt_template = prompt_template or TeslaPromptTemplate()
        
        self.api_key = api_key or GROQ_API_KEY
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        
        self.client = None
        
        logger.info(f"Initialized RAGOrchestrator with model={model}")
    
    def _init_client(self):
        """Initialize the Groq client."""
        if self.client is None:
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not set. Please set the environment variable.")
            self.client = Groq(api_key=self.api_key)
            logger.info("Initialized Groq client")
    
    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline.
        
        Args:
            query: User query string
            top_k: Override default top_k for retrieval
            temperature: Override default temperature
            top_p: Override default top_p
            
        Returns:
            Dict with answer, retrieved chunks, and metadata
        """
        start_time = time.time()
        
        logger.info(f"Processing query: '{query[:100]}...'")
        
        retrieval_result = self.retriever.retrieve_with_context(
            query, 
            top_k=top_k or TOP_K
        )
        
        retrieval_time = time.time() - start_time
        
        if not retrieval_result['chunks']:
            return {
                'answer': self.prompt_template.get_no_context_response(),
                'chunks': [],
                'metadata': {
                    'retrieval_time': retrieval_time,
                    'generation_time': 0,
                    'total_time': retrieval_time,
                    'num_chunks': 0,
                    'model': self.model
                }
            }
        
        gen_start = time.time()
        
        messages = self.prompt_template.format_messages(
            query=query,
            context=retrieval_result['context']
        )
        
        self._init_client()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            top_p=top_p or self.top_p,
            max_tokens=self.max_tokens
        )
        
        answer = response.choices[0].message.content
        generation_time = time.time() - gen_start
        total_time = time.time() - start_time
        
        logger.info(f"Query processed in {total_time:.2f}s")
        
        return {
            'answer': answer,
            'chunks': retrieval_result['chunks'],
            'metadata': {
                'retrieval_time': retrieval_time,
                'generation_time': generation_time,
                'total_time': total_time,
                'num_chunks': retrieval_result['num_chunks'],
                'model': self.model,
                'temperature': temperature or self.temperature,
                'top_p': top_p or self.top_p,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        }
    
    def query_with_sources(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query with formatted source citations.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            Dict with answer, sources, and metadata
        """
        result = self.query(query, top_k)
        
        sources = []
        for chunk in result['chunks']:
            sources.append({
                'filename': chunk['metadata'].get('filename', 'Unknown'),
                'score': chunk['similarity_score'],
                'excerpt': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content']
            })
        
        return {
            'answer': result['answer'],
            'sources': sources,
            'metadata': result['metadata']
        }
    
    def update_parameters(
        self,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Update generation parameters.
        
        Args:
            temperature: New temperature value
            top_p: New top_p value
            max_tokens: New max_tokens value
        """
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p
        if max_tokens is not None:
            self.max_tokens = max_tokens
        
        logger.info(
            f"Updated parameters: temperature={self.temperature}, "
            f"top_p={self.top_p}, max_tokens={self.max_tokens}"
        )
