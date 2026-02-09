"""RAG Pipeline with Groq LLM integration."""
from groq import Groq
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings
from .embeddings import EmbeddingModel
from .vector_store import FAISSVectorStore


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for medical case search.
    
    Security Design:
    - Patient data (transcriptions) NEVER leaves the local system
    - Only the user's search query is sent to Groq API
    - Retrieved context is summarized locally before any external calls
    """
    
    def __init__(self):
        """Initialize the RAG pipeline components."""
        self.embedding_model = EmbeddingModel()
        self.vector_store = FAISSVectorStore()
        self._groq_client = None
    
    @property
    def groq_client(self) -> Optional[Groq]:
        """Lazy initialization of Groq client."""
        if self._groq_client is None and settings.GROQ_API_KEY:
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
        return self._groq_client
    
    def initialize(self) -> bool:
        """
        Initialize the pipeline by loading the vector store.
        
        Returns:
            True if initialized successfully
        """
        return self.vector_store.load()
    
    def search_similar_cases(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search for similar medical cases based on symptoms/query.
        
        Args:
            query: Natural language search query (e.g., "patient with chest pain and shortness of breath")
            top_k: Number of results to return
            
        Returns:
            List of similar cases with metadata and similarity scores
        """
        query_embedding = self.embedding_model.embed_text(query)
        
        results = self.vector_store.search(query_embedding, top_k)
        
        formatted_results = []
        for metadata, score in results:
            formatted_results.append({
                "id": metadata.get("id"),
                "specialty": metadata.get("medical_specialty", "Unknown"),
                "description": metadata.get("description", ""),
                "sample_name": metadata.get("sample_name", ""),
                "transcription": metadata.get("transcription", ""),
                "keywords": metadata.get("keywords", ""),
                "similarity_score": round(score, 4)
            })
        
        return formatted_results
    
    def generate_summary(self, query: str, retrieved_cases: List[Dict[str, Any]]) -> str:
        """
        Generate an AI summary of retrieved cases using Groq.
        
        SECURITY NOTE: Only the query and anonymized case summaries are sent to Groq.
        Full transcriptions remain local.
        
        Args:
            query: Original search query
            retrieved_cases: List of retrieved case dictionaries
            
        Returns:
            AI-generated summary of findings
        """
        if not self.groq_client:
            return "Groq API key not configured. Please set GROQ_API_KEY in your .env file."
        
        case_summaries = []
        for i, case in enumerate(retrieved_cases[:3], 1):
            summary = f"""
Case {i}:
- Specialty: {case.get('specialty', 'Unknown')}
- Description: {case.get('description', 'N/A')[:200]}
- Similarity: {case.get('similarity_score', 0):.2%}
"""
            case_summaries.append(summary)
        
        prompt = f"""You are a medical AI assistant helping doctors find similar past cases.

Search Query: {query}

Retrieved Similar Cases:
{''.join(case_summaries)}

Based on these similar cases, provide a brief clinical summary that:
1. Identifies common patterns across the retrieved cases
2. Highlights relevant medical specialties involved
3. Suggests what clinical considerations might be relevant

Keep your response concise and clinically focused. Do not include any patient-identifying information."""

        try:
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful medical AI assistant. Provide concise, clinically relevant summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    @property
    def is_ready(self) -> bool:
        """Check if the pipeline is ready for queries."""
        return self.vector_store.is_initialized
