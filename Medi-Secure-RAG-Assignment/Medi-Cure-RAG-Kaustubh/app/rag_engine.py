"""
RAG (Retrieval Augmented Generation) Engine
Handles vector embeddings using FAISS and semantic search for medical transcriptions
All processing happens locally - no patient data leaves the system
"""
import os
import time
import pickle
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
import faiss

from app.config import settings
from app.database import mongodb
from app.models import SearchResult, SearchResponse


class RAGEngine:
    """
    RAG Engine for medical transcription search
    Uses FAISS for vector indexing and sentence-transformers for embeddings
    MongoDB stores the document metadata
    All processing is done locally to ensure patient data security
    """
    
    def __init__(self):
        self.faiss_index = None
        self.embedding_model = None
        self.id_mapping: List[str] = []  # Maps FAISS index to case_id
        self.documents_cache: Dict[str, Dict[str, Any]] = {}  # Cache for quick lookup
        self._initialized = False
    
    def initialize(self, force_rebuild: bool = False):
        """
        Initialize the RAG engine with FAISS index and embedding model
        
        Args:
            force_rebuild: If True, rebuild the index from scratch
        """
        if self._initialized and not force_rebuild:
            return
        
        print("Initializing RAG Engine...")
        
        # Initialize embedding model (runs locally)
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Get paths
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_dir = os.path.join(project_root, settings.FAISS_INDEX_PATH.lstrip("./"))
        index_path = os.path.join(index_dir, "index.faiss")
        mapping_path = os.path.join(index_dir, "id_mapping.pkl")
        cache_path = os.path.join(index_dir, "docs_cache.pkl")
        
        # Connect to MongoDB
        mongodb.connect()
        
        # Check if index exists and we don't need to rebuild
        if not force_rebuild and os.path.exists(index_path) and os.path.exists(mapping_path):
            print("Loading existing FAISS index...")
            self.faiss_index = faiss.read_index(index_path)
            with open(mapping_path, 'rb') as f:
                self.id_mapping = pickle.load(f)
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    self.documents_cache = pickle.load(f)
            print(f"Loaded FAISS index with {self.faiss_index.ntotal} vectors")
        else:
            print("Building new FAISS index...")
            self._build_index()
            
            # Save index
            os.makedirs(index_dir, exist_ok=True)
            faiss.write_index(self.faiss_index, index_path)
            with open(mapping_path, 'wb') as f:
                pickle.dump(self.id_mapping, f)
            with open(cache_path, 'wb') as f:
                pickle.dump(self.documents_cache, f)
            print("FAISS index saved to disk")
        
        self._initialized = True
        print("RAG Engine initialized successfully!")
    
    def _build_index(self):
        """Build FAISS index from medical transcription data"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(project_root, settings.DATA_PATH.lstrip("./"))
        
        print(f"Loading data from: {data_path}")
        
        # Load CSV data
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} records from CSV")
        
        # Clean and prepare data
        df = df.dropna(subset=['transcription'])
        df = df.fillna('')
        
        # Clear MongoDB transcriptions if rebuilding
        if mongodb.is_connected():
            mongodb.clear_transcriptions()
        
        all_embeddings = []
        self.id_mapping = []
        self.documents_cache = {}
        
        batch_size = 100
        total_batches = (len(df) + batch_size - 1) // batch_size
        mongo_docs = []
        
        print(f"Processing {len(df)} records...")
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            documents = []
            batch_ids = []
            
            for _, row in batch.iterrows():
                transcription = str(row.get('transcription', '')).strip()
                if not transcription or transcription == 'nan':
                    continue
                
                case_id = str(row.get('Unnamed: 0', len(self.id_mapping)))
                specialty = str(row.get('medical_specialty', ''))
                sample_name = str(row.get('sample_name', ''))
                keywords = str(row.get('keywords', ''))
                description = str(row.get('description', ''))
                
                # Create searchable text
                doc_text = f"{specialty} - {sample_name}: {transcription}"
                documents.append(doc_text)
                batch_ids.append(case_id)
                
                # Store in cache
                doc_data = {
                    "case_id": case_id,
                    "specialty": specialty,
                    "sample_name": sample_name,
                    "transcription": transcription,
                    "keywords": keywords,
                    "description": description
                }
                self.documents_cache[case_id] = doc_data
                
                # Prepare for MongoDB
                if mongodb.is_connected():
                    mongo_docs.append(doc_data)
            
            if documents:
                # Generate embeddings
                embeddings = self.embedding_model.encode(documents)
                all_embeddings.extend(embeddings)
                self.id_mapping.extend(batch_ids)
            
            # Batch insert to MongoDB every 500 docs
            if len(mongo_docs) >= 500:
                mongodb.insert_many_transcriptions(mongo_docs)
                mongo_docs = []
            
            print(f"Processed batch {batch_num}/{total_batches}")
        
        # Insert remaining MongoDB docs
        if mongo_docs and mongodb.is_connected():
            mongodb.insert_many_transcriptions(mongo_docs)
        
        # Create FAISS index
        embeddings_matrix = np.array(all_embeddings).astype('float32')
        dimension = embeddings_matrix.shape[1]
        
        # Use L2 distance index (can also use IndexFlatIP for inner product)
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(embeddings_matrix)
        
        print(f"Created FAISS index with {self.faiss_index.ntotal} vectors (dimension: {dimension})")
    
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        specialty_filter: Optional[str] = None
    ) -> SearchResponse:
        """
        Search for similar medical cases using semantic search
        
        Args:
            query: Search query describing symptoms or medical conditions
            top_k: Number of results to return
            specialty_filter: Optional filter by medical specialty
        
        Returns:
            SearchResponse with ranked results
        """
        if not self._initialized:
            raise RuntimeError("RAG Engine not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).astype('float32')
        
        # Search more results if filtering
        search_k = top_k * 5 if specialty_filter else top_k
        
        # FAISS search
        distances, indices = self.faiss_index.search(query_embedding, search_k)
        
        # Process results
        search_results = []
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            case_id = self.id_mapping[idx]
            
            # Get document from cache or MongoDB
            doc = self.documents_cache.get(case_id)
            if not doc and mongodb.is_connected():
                doc = mongodb.get_transcription_by_case_id(case_id)
            
            if not doc:
                continue
            
            # Apply specialty filter
            if specialty_filter and doc.get("specialty") != specialty_filter:
                continue
            
            # Convert L2 distance to similarity score
            similarity_score = 1 / (1 + distance)
            
            search_results.append(SearchResult(
                case_id=doc["case_id"],
                specialty=doc.get("specialty", "Unknown"),
                sample_name=doc.get("sample_name", "Unknown"),
                transcription=doc.get("transcription", ""),
                similarity_score=round(float(similarity_score), 4),
                keywords=doc.get("keywords", None)
            ))
            
            if len(search_results) >= top_k:
                break
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time_ms, 2)
        )
    
    def get_specialties(self) -> List[str]:
        """Get list of unique medical specialties"""
        if not self._initialized:
            raise RuntimeError("RAG Engine not initialized. Call initialize() first.")
        
        # Try MongoDB first
        if mongodb.is_connected():
            return mongodb.get_all_specialties()
        
        # Fallback to cache
        specialties = set()
        for doc in self.documents_cache.values():
            specialty = doc.get('specialty', '')
            if specialty and specialty != 'nan':
                specialties.add(specialty)
        
        return sorted(list(specialties))
    
    def get_stats(self) -> dict:
        """Get statistics about the vector database"""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        specialties = self.get_specialties()
        
        return {
            "status": "initialized",
            "total_documents": self.faiss_index.ntotal if self.faiss_index else 0,
            "embedding_model": settings.EMBEDDING_MODEL,
            "num_specialties": len(specialties),
            "specialties": specialties[:10],
            "mongodb_connected": mongodb.is_connected()
        }


# Global RAG engine instance
rag_engine = RAGEngine()
