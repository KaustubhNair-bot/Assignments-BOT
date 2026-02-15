import streamlit as st
import os
from auth.login import login_page, logout
from rag.loader import load_documents
from rag.chunking import split_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import create_vector_store, load_vector_store
from rag.retriever import get_retriever
from rag.generator_llm import generate_answer_cot
from config.settings import FAISS_INDEX_PATH

# Page Configuration
st.set_page_config(page_title="Nike HR AI Consultant", page_icon="👟", layout="wide")

# --------------------------
# Initialization & Caching
# --------------------------
@st.cache_resource
def initialize_rag_pipeline():
    """
    Initializes the RAG pipeline. Checks if vector store exists, else creates it.
    """
    embed_model = get_embedding_model()
    
    if not os.path.exists(FAISS_INDEX_PATH):
        with st.spinner("Initializing Knowledge Base... (One-time setup)"):
            docs = load_documents()
            chunks = split_documents(docs)
            vector_store = create_vector_store(chunks, embed_model)
    else:
        vector_store = load_vector_store(embed_model)
        
    return vector_store

# --------------------------
# Main App Logic
# --------------------------
def main():
    # 1. Authentication Check
    if not login_page():
        return

    # 2. Sidebar Configuration
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/1200px-Logo_NIKE.svg.png", width=150)
        st.title("Settings")
        st.markdown("---")
        
        # Model Info (LLM-only with Chain-of-Thought)
        st.info("**Model**: Llama 3.3 70B Versatile\n\n✓ Chain-of-Thought Reasoning\n✓ Maximum Accuracy\n✓ Compliance-Focused")
        
        st.markdown("---")
        
        # Temperature and Top-P sliders
        temperature = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.0, 0.1,
                               help="0.0 = Strict/Factual, 1.0 = Creative")
        top_p = st.slider("Top-P (Nucleus Sampling)", 0.5, 1.0, 0.9, 0.05,
                         help="Controls diversity of word selection")
        
        st.markdown("---")
        
        # Why LLM-only explanation
        with st.expander("ℹ️ Why LLM-Only?"):
            st.markdown("""
            **We use only the 70B model because:**
            - ✅ <2% hallucination rate (vs 5-10% for smaller models)
            - ✅ Better Chain-of-Thought reasoning
            - ✅ Compliance-critical accuracy
            - ✅ Cost difference negligible for HR use case
            """)
        
        st.markdown("---")
        if st.button("Logout"):
            logout()
            
    # 3. Main Content
    st.title("👟 Nike HR AI Consultant")
    st.markdown("**Chain-of-Thought Reasoning** • Ask questions about Nike's HR policies and see the complete reasoning process.")

    # Initialize RAG
    try:
        vector_store = initialize_rag_pipeline()
        retriever = get_retriever(vector_store)
    except Exception as e:
        st.error(f"Failed to initialize RAG pipeline: {e}")
        return

    # 4. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Display Chain-of-Thought sections for assistant messages
                if "cot" in message:
                    display_cot_response(message["cot"])
                else:
                    st.markdown(message["content"])
            else:
                st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Ex: What is the policy on remote work?"):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Assistant Response with Chain-of-Thought
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking and analyzing policies..."):
                try:
                    # Generate CoT response using LLM (70B)
                    cot_result = generate_answer_cot(prompt, retriever, temperature, top_p)
                    
                    # Display Chain-of-Thought sections
                    display_cot_response(cot_result)
                    
                    # Save to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": cot_result['answer'],
                        "cot": cot_result
                    })
                    
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    error_msg = f"Error: {e}"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def display_cot_response(cot_result):
    """
    Display Chain-of-Thought response in 4 structured sections.
    
    This function shows the complete reasoning process:
    1. Thoughts Before Retrieval - What info the model thinks it needs
    2. Selected Chunks and Why - Which chunks were retrieved and their relevance
    3. Reasoning Based on Chunks - Step-by-step logic from context to answer
    4. Final Answer - Concise, professional response
    
    Args:
        cot_result: Dict with 'thoughts', 'chunks', 'reasoning', 'answer', 'source_documents'
    """
    # Section 1: Thoughts Before Retrieval
    with st.expander("💭 **Step 1: Thoughts Before Retrieval**", expanded=False):
        st.markdown(cot_result.get('thoughts', 'No thoughts section found'))
    
    # Section 2: Selected Chunks and Why
    with st.expander("📄 **Step 2: Selected Chunks and Why**", expanded=False):
        st.info(cot_result.get('chunks', 'No chunks section found'))
        
        # Also show actual retrieved documents
        if 'source_documents' in cot_result and cot_result['source_documents']:
            st.markdown("**Retrieved Documents:**")
            for i, doc in enumerate(cot_result['source_documents'], 1):
                source = os.path.basename(doc.metadata.get('source', 'Unknown'))
                with st.container():
                    st.markdown(f"**Chunk {i}** ({source})")
                    st.text(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                    if i < len(cot_result['source_documents']):
                        st.markdown("---")
    
    # Section 3: Reasoning Based on Chunks
    with st.expander("🔍 **Step 3: Reasoning Based on Chunks**", expanded=False):
        st.success(cot_result.get('reasoning', 'No reasoning section found'))
    
    # Section 4: Final Answer (always visible)
    st.markdown("### ✅ Final Answer")
    st.markdown(cot_result.get('answer', 'No answer generated'))


if __name__ == "__main__":
    main()
