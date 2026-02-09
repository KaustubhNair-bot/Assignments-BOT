import os
import pinecone
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.vectorstores import Pinecone as LangChainPinecone
from langchain_community.llms import Cohere
from langchain_community.vectorstores.utils import DistanceStrategy
from pinecone import Pinecone, ServerlessSpec
from typing import Any, Optional, List
from .config import get_settings

settings = get_settings()

class CustomPinecone(LangChainPinecone):
    def __init__(
        self,
        index: Any,
        embedding: Any,
        text_key: str,
        namespace: Optional[str] = None,
        distance_strategy: Optional[DistanceStrategy] = DistanceStrategy.COSINE,
    ):
        # Skip the isinstance(index, pinecone.Index) check
        self._index = index
        self._embedding = embedding
        self._text_key = text_key
        self._namespace = namespace
        self.distance_strategy = distance_strategy
        
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        batch_size: int = 32,
        **kwargs: Any,
    ) -> List[str]:
        return super().add_texts(texts, metadatas, ids, namespace, batch_size, **kwargs)

class RAGSystem:
    def __init__(self):
        self.embeddings = CohereEmbeddings(
            cohere_api_key=settings.COHERE_API_KEY,
            model="embed-english-v3.0",
            user_agent="medical-rag-app"
        )
        
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        
        # Check if index exists
        existing_indexes = [i.name for i in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1024, # Cohere embed-english-v3.0
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENV
                    )
                )
            except Exception as e:
                print(f"Error creating index: {e}")

        # Use index() method for v3 client
        self.index = self.pc.Index(self.index_name)
        
        # Use CustomPinecone to verify compatibility
        self.vectorstore = CustomPinecone(
            index=self.index, 
            embedding=self.embeddings, 
            text_key="text"
        )
        self.llm = Cohere(cohere_api_key=settings.COHERE_API_KEY)

    def search(self, query: str, k: int = 5):
        docs = self.vectorstore.similarity_search(query, k=k)
        return docs
    
    def add_document(self, text: str, metadata: dict):
        try:
            self.vectorstore.add_texts(texts=[text], metadatas=[metadata])
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False

    def generate_answer(self, query: str, context_docs):
        context = "\n".join([doc.page_content for doc in context_docs])
        prompt = f"""
        You are a helpful medical assistant. Use the following patient cases to answer the doctor's question or find similar cases.
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:
        """
        return self.llm.invoke(prompt)

rag = RAGSystem()
