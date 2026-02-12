import os
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import re

load_dotenv()


class TeslaRAGEngine:
    def __init__(self, chunks):
        # 1. SLM: Local Embedding Model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # 2. Vector DB: Direct ChromaDB (Native)
        self.client = chromadb.PersistentClient(path="./chromadb")
        # Delete old collection if it exists to avoid version conflict
        try:
            self.client.delete_collection(name="tesla_docs")
        except:
            pass

        self.collection = self.client.create_collection(name="tesla_docs")

        # 3. Add data to Vector DB
        # We generate embeddings manually here (The 3x way)
        embeddings = self.model.encode(chunks).tolist()
        ids = [f"id_{i}" for i in range(len(chunks))]
        self.collection.add(documents=chunks, embeddings=embeddings, ids=ids)

        # 4. Groq Client
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def get_response(self, query, temp=0.0, top_p=1.0):
        """
        Final Native RAG Engine: Cleaned, Deterministic, and Auditor-Ready.
        """
        # 1. RETRIEVAL: Find the top 3 most relevant segments using SLM Math
        query_vec = self.model.encode([query]).tolist()
        results = self.collection.query(query_embeddings=query_vec, n_results=3)
        context_chunks = results["documents"][0]

        # 2. DATA SANITIZATION: The "3x" Cleanup
        clean_sources = []
        for c in context_chunks:
            # A. Crunch multiple newlines into one to remove those big gaps
            text = re.sub(r"\n+", "\n", c)
            # B. Crunch multiple spaces into one single space
            text = re.sub(r" +", " ", text)
            # C. Remove common PDF header junk that confuses the user
            cleaned_text = (
                text.replace("Impact Report 2023", "")
                .replace("Master Plan Part 3", "")
                .strip()
            )

            clean_sources.append({"page_content": cleaned_text})

        # Prepare the context text for the Auditor
        context_text = "\n\n".join([s["page_content"] for s in clean_sources])

        # 3. GENERATION: The Chain-of-Thought Auditor Prompt
        prompt = f"""
        PERSONA: You are the Tesla Lead Logistics Auditor. 
        Tone: Analytical, precise, and first-principles based.
        
        INSTRUCTIONS:
        1. Read the Context carefully.
        2. Provide a 'LOGIC' section explaining how the retrieved facts answer the question.
        3. Provide the 'FINAL ANSWER'. 
        4. If the exact data is not present, say 'Data not present in Tesla internal documentation.'
        
        CONTEXT:
        {context_text}
        
        USER QUESTION: {query}
        """

        # 4. EXECUTION: Direct Groq Call with Experimentation Sliders
        chat_completion = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=temp,
            top_p=top_p,
        )

        # 5. DELIVERY: Return the high-reasoning response and the beautiful, clean sources
        return chat_completion.choices[0].message.content, clean_sources
