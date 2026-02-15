"""
LLM Generator Module with Chain-of-Thought Reasoning
Uses Llama 3.3 70B for high-quality, explainable HR policy responses
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from config.settings import GROQ_API_KEY
from dotenv import load_dotenv
from rag.prompting import get_cot_prompt_template, parse_cot_response, format_cot_for_display

# LLM Model Configuration
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

def get_llm(temperature=0.0, top_p=1.0):
    """
    Initialize the Groq LLM (70B) with specified parameters.
    """
    load_dotenv()
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment.")
        
    # Be very explicit about parameters to ensure UI changes take effect
    llm = ChatGroq(
        model=LLM_MODEL_NAME,
        temperature=float(temperature),
        groq_api_key=GROQ_API_KEY,
        top_p=float(top_p),
        max_retries=2,
    )
    return llm


def generate_answer_cot(query, retriever, temperature=0.0, top_p=1.0):
    """
    Generates an answer using Chain-of-Thought reasoning with the LLM (70B).
    
    This function implements a 4-step reasoning process:
    1. Thoughts Before Retrieval - What info is needed
    2. Selected Chunks and Why - Which chunks were retrieved and why
    3. Reasoning Based on Chunks - Step-by-step logic
    4. Final Answer - Concise, professional response
    
    Args:
        query: User's question
        retriever: FAISS retriever instance
        temperature: LLM temperature setting (0.0 = strict, 1.0 = creative)
        top_p: Top-p sampling parameter
        
    Returns:
        dict: Contains 'thoughts', 'chunks', 'reasoning', 'answer', 'source_documents'
    """
    load_dotenv()
    print(f"DEBUG: Generating answer with temperature={temperature}, top_p={top_p}")
    
    # Get Chain-of-Thought prompt template
    cot_template = get_cot_prompt_template()
    
    # Retrieve relevant documents using invoke() method (LangChain v0.2+)
    retrieved_docs = retriever.invoke(query)
    
    # Format retrieved context
    context = "\n\n---\n\n".join([
        f"Document: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
        for doc in retrieved_docs
    ])
    
    # Create prompt with context and query
    prompt = PromptTemplate(
        template=cot_template,
        input_variables=["context", "question"]
    )
    
    formatted_prompt = prompt.format(context=context, question=query)
    
    # Get LLM instance
    llm = get_llm(temperature, top_p)
    
    # Generate response
    response = llm.invoke(formatted_prompt)
    
    # Extract text from response
    if hasattr(response, 'content'):
        response_text = response.content
    else:
        response_text = str(response)
    
    # Parse Chain-of-Thought sections
    cot_sections = parse_cot_response(response_text)
    
    # Format for display
    formatted_sections = format_cot_for_display(cot_sections)
    
    # Return structured result
    return {
        'thoughts': formatted_sections['thoughts'],
        'chunks': formatted_sections['chunks'],
        'reasoning': formatted_sections['reasoning'],
        'answer': formatted_sections['answer'],
        'source_documents': retrieved_docs,
        'raw_response': response_text  # For debugging
    }


# Backward compatibility: alias for existing code
def generate_answer_llm(query, retriever, temperature=0.0, top_p=1.0):
    """
    Backward compatibility wrapper for generate_answer_cot.
    
    Returns result in old format for compatibility with existing code.
    """
    cot_result = generate_answer_cot(query, retriever, temperature, top_p)
    
    # Return in old RetrievalQA format
    return {
        'result': cot_result['answer'],
        'source_documents': cot_result['source_documents'],
        'cot_sections': {
            'thoughts': cot_result['thoughts'],
            'chunks': cot_result['chunks'],
            'reasoning': cot_result['reasoning']
        }
    }


if __name__ == "__main__":
    print(f"LLM Generator with Chain-of-Thought ready. Model: {LLM_MODEL_NAME}")
    print("\nChain-of-Thought Structure:")
    print("1. [THOUGHTS BEFORE RETRIEVAL]")
    print("2. [SELECTED CHUNKS AND WHY]")
    print("3. [REASONING BASED ON CHUNKS]")
    print("4. [FINAL ANSWER]")
