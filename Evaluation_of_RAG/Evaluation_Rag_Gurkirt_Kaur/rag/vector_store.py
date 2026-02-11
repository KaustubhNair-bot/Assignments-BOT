"""
Vector Store Module using FAISS
Handles embedding generation and similarity search for medical documents
"""

import os
import pickle
import numpy as np
import faiss
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Tuple
from app.config import Config

class VectorStore:
    """Manages FAISS vector store for document similarity search"""
    
    def __init__(self):
        self.model_name = Config.EMBEDDING_MODEL
        self.vector_store_path = Config.VECTOR_STORE_PATH
        self.metadata_path = self.vector_store_path.replace('.faiss', '_metadata.pkl')
        
        # Initialize embedding model (BioBERT)
        print(f"Loading embedding model: {self.model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            print("Falling back to sentence-transformers/all-MiniLM-L6-v2 if BioBERT fails or valid replacement.")
            # Fallback or raise? Let's raise for now to ensure we use BioBERT
            raise e
            
        # Initialize FAISS index and metadata
        self.index = None
        self.documents = []
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts using BioBERT
        Mean pooling of last hidden state.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        all_embeddings = []
        batch_size = 32
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            
            # Tokenize
            inputs = self.tokenizer(
                batch_texts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling
                # attention_mask shape: (batch, seq_len)
                # last_hidden_state shape: (batch, seq_len, hidden_dim)
                
                token_embeddings = outputs.last_hidden_state
                input_mask_expanded = inputs['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
                
                # Sum of embeddings of valid tokens
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                # Count of valid tokens
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                
                batch_embeddings = sum_embeddings / sum_mask
                all_embeddings.append(batch_embeddings.numpy())
                
        if not all_embeddings:
            return np.array([])
            
        embeddings = np.concatenate(all_embeddings, axis=0)
        
        # Ensure embeddings are float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        return embeddings

    def create_index(self, embeddings: np.ndarray):
        """
        Create FAISS index for similarity search
        
        Args:
            embeddings: Numpy array of document embeddings
        """
        dimension = embeddings.shape[1]
        
        # Create IndexFlatIP for inner product (cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        print(f"Created FAISS index with {self.index.ntotal} vectors of dimension {dimension}")
    
    def add_documents(self, documents: List[Dict]):
        """
        Add documents to vector store
        
        Args:
            documents: List of document dictionaries with text and metadata
        """
        if not documents:
            print("No documents to add")
            return
        
        self.documents = documents
        
        # Extract text from documents
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.get_embeddings(texts)
        
        print(f"Generated embeddings with shape: {embeddings.shape}")
        
        # Create FAISS index
        self.create_index(embeddings)
        
        print(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, k: int = None) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents
        
        Args:
            query: Search query string
            k: Number of results to return (default from config)
            
        Returns:
            List of tuples containing (document, similarity_score)
        """
        if self.index is None:
            raise ValueError("Vector store is empty. Please add documents first.")
        
        if k is None:
            k = Config.TOP_K_RETRIEVAL
        
        # Generate query embedding
        query_embedding = self.get_embeddings([query])
        
        # Search in FAISS index
        similarities, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx != -1 and idx < len(self.documents):  # Valid index
                doc = self.documents[idx].copy()
                results.append((doc, float(similarity)))
        
        return results
    
    def save_vector_store(self):
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            print("No vector store to save")
            return
        
        # Save FAISS index
        faiss.write_index(self.index, self.vector_store_path)
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"Vector store saved to {self.vector_store_path}")
    
    def load_vector_store(self) -> bool:
        """
        Load FAISS index and metadata from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.vector_store_path):
            print(f"Vector store file not found: {self.vector_store_path}")
            return False
        
        if not os.path.exists(self.metadata_path):
            print(f"Metadata file not found: {self.metadata_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.vector_store_path)
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            print(f"Vector store loaded with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with vector store statistics
        """
        if self.index is None:
            return {'status': 'empty', 'total_documents': 0}
        
        return {
            'status': 'loaded',
            'total_documents': self.index.ntotal,
            'embedding_dimension': self.index.d,
            'model_name': self.model_name,
            'vector_store_path': self.vector_store_path
        }
