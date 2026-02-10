import ollama
import os
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:1b")


def get_base_llm_response(query):
    """
    MODE 1: STANDARD LLM (The 'Base' for comparison)
    The AI answers based on its general training, without any private data.
    """
    prompt = f"""
    You are a general medical assistant. 
    Answer the following doctor's query based ONLY on your general knowledge.
    
    Query: {query}
    
    Response:
    """
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"]


def get_rag_response(query, context_documents):
    context_text = ""
    for i, doc in enumerate(context_documents):
        context_text += f"### MEDICAL RECORD REFERENCE {i + 1} ###\n{doc}\n\n"

    prompt = f"""
    You are a Senior Clinical Analyst. Your goal is to provide a DETAILED and COMPREHENSIVE report.
    
    INSTRUCTIONS:
    1. Use ONLY the provided Medical Records.
    2. Start by summarizing the key patient demographics found in the records.
    3. Provide a step-by-step breakdown of findings or procedures mentioned.
    4. If the records show conflicting information, highlight it.
    5. CITE your sources clearly (e.g., "According to Reference 1...").
    
    MEDICAL RECORDS:
    {context_text}
    
    DOCTOR'S QUERY: {query}
    
    DETAILED CLINICAL ANALYSIS:
    """
    response = ollama.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"]
