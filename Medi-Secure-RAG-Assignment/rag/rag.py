"""
RAG (Retrieval-Augmented Generation) Pipeline
Handles document retrieval and AI-powered response generation
"""

import os
from typing import List, Dict, Tuple
from groq import Groq
from app.config import Config
from rag.data_loader import DataLoader
from rag.vector_store import VectorStore

class RAGPipeline:
    """Main RAG pipeline for medical case search and response generation"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.vector_store = VectorStore()
        self.groq_client = None
        
        # Initialize Groq client if API key is available
        if Config.GROQ_API_KEY:
            self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        else:
            print("Warning: Groq API key not found. Response generation will be disabled.")
    
    def initialize_vector_store(self, force_rebuild: bool = False) -> bool:
        """
        Initialize or load the vector store
        
        Args:
            force_rebuild: If True, rebuild vector store even if it exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to load existing vector store
            if not force_rebuild and self.vector_store.load_vector_store():
                print("Loaded existing vector store")
                return True
            
            # Load and process documents
            print("Processing documents and creating new vector store...")
            documents = self.data_loader.prepare_documents()
            
            if not documents:
                print("No documents found to process")
                return False
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            
            # Save vector store
            self.vector_store.save_vector_store()
            
            print("Vector store created and saved successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            return False
    
    def retrieve_relevant_documents(self, query: str, k: int = None) -> List[Tuple[Dict, float]]:
        """
        Retrieve relevant documents for a given query
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if self.vector_store.index is None:
            raise ValueError("Vector store not initialized. Call initialize_vector_store() first.")
        
        return self.vector_store.search(query, k)
    
    def generate_response(self, query: str, retrieved_docs: List[Tuple[Dict, float]]) -> str:
        """
        Generate AI response using retrieved documents as context
        
        Args:
            query: User's question
            retrieved_docs: List of retrieved documents with similarity scores
            
        Returns:
            Generated response string
        """
        if not self.groq_client:
            return "AI response generation is not available. Please configure Groq API key."
        
        if not retrieved_docs:
            return "No relevant medical cases found for your query."
        
        # Prepare context from retrieved documents
        context_parts = []
        for i, (doc, similarity) in enumerate(retrieved_docs):
            context_parts.append(f"""
Case {i+1} (Similarity: {similarity:.3f}):
Medical Specialty: {doc['metadata']['medical_specialty']}
Sample: {doc['metadata']['sample_name']}
Content: {doc['text']}
""")
        
        context = "\n".join(context_parts)
        
        # Create prompt for the LLM
        prompt = f"""
You are a medical AI assistant helping doctors search for similar patient cases. 
Based on the provided medical case transcripts, answer the doctor's question accurately and professionally.

CONTEXT FROM SIMILAR MEDICAL CASES:
{context}

DOCTOR'S QUESTION: {query}

Please provide a comprehensive answer based on the similar cases above. Focus on:
1. Relevant patterns or findings from the cases
2. Similar symptoms or conditions
3. Treatment approaches mentioned
4. Any important medical insights

If the context doesn't contain enough information to answer the question, please indicate that clearly.

RESPONSE:
"""
        
        try:
            # Generate response using Groq
            response = self.groq_client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful medical AI assistant providing insights based on similar patient cases."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def search_and_respond(self, query: str) -> Dict:
        """
        Complete RAG pipeline: retrieve documents and generate response
        
        Args:
            query: User's search query
            
        Returns:
            Dictionary with retrieved documents and generated response
        """
        try:
            # Retrieve relevant documents
            retrieved_docs = self.retrieve_relevant_documents(query)
            
            # Generate response
            response = self.generate_response(query, retrieved_docs)
            
            return {
                'query': query,
                'retrieved_documents': retrieved_docs,
                'response': response,
                'success': True
            }
            
        except Exception as e:
            return {
                'query': query,
                'retrieved_documents': [],
                'response': f"Error processing search: {str(e)}",
                'success': False
            }
    
    def get_system_stats(self) -> Dict:
        """
        Get system statistics and information
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            'vector_store': self.vector_store.get_stats(),
            'data_info': self.data_loader.get_sample_data_info(),
            'groq_configured': self.groq_client is not None,
            'config': {
                'chunk_size': Config.CHUNK_SIZE,
                'chunk_overlap': Config.CHUNK_OVERLAP,
                'top_k_retrieval': Config.TOP_K_RETRIEVAL,
                'embedding_model': Config.EMBEDDING_MODEL,
                'groq_model': Config.GROQ_MODEL
            }
        }
        
        return stats
