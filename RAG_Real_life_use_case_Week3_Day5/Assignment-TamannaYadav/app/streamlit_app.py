"""
Tesla RAG System - Streamlit Frontend
Main application file for the Tesla Knowledge Assistant.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import (
    init_session_state,
    is_authenticated,
    get_current_user,
    render_login_page,
    render_logout_button
)
from app.ui_components import (
    apply_tesla_theme,
    render_header,
    render_sidebar_controls,
    render_chunks_panel,
    render_stats,
    render_error,
    init_chat_history,
    add_to_chat_history,
    clear_chat_history
)

from config.settings import DATA_DIR
from utils.logger import get_logger
from ingestion.pdf_loader import PDFLoader
from preprocessing.text_cleaner import TextCleaner
from chunking.text_splitter import RecursiveTextSplitter
from embeddings.embedding_generator import EmbeddingGenerator
from vector_db.faiss_store import FAISSVectorStore
from retrieval.retriever import Retriever
from prompts.templates import TeslaPromptTemplate
from rag.orchestrator import RAGOrchestrator

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Tesla Knowledge Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_rag_system():
    """
    Initialize the RAG system (cached for performance).
    
    Returns:
        RAGOrchestrator instance
    """
    try:
        vector_store = FAISSVectorStore()
        
        if not vector_store.load():
            st.info("Building index from Tesla documents... This may take a few minutes.")
            
            loader = PDFLoader(str(DATA_DIR))
            documents = loader.load()
            
            cleaner = TextCleaner()
            cleaned_docs = cleaner.clean_batch(documents)
            
            splitter = RecursiveTextSplitter()
            chunks = splitter.split_documents(cleaned_docs)
            
            embedding_generator = EmbeddingGenerator()
            embedded_chunks = embedding_generator.embed_chunks(chunks)
            
            vector_store.create_index()
            vector_store.add_embedded_chunks(embedded_chunks)
            vector_store.save()
        
        embedding_generator = EmbeddingGenerator()
        retriever = Retriever(embedding_generator, vector_store)
        prompt_template = TeslaPromptTemplate()
        orchestrator = RAGOrchestrator(retriever, prompt_template)
        
        return orchestrator
    
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return None


def process_query(orchestrator: RAGOrchestrator, query: str, settings: dict):
    """
    Process a user query through the RAG pipeline.
    
    Args:
        orchestrator: RAGOrchestrator instance
        query: User query string
        settings: Dict with temperature, top_p, top_k
        
    Returns:
        RAG result dict
    """
    try:
        result = orchestrator.query(
            query=query,
            top_k=settings["top_k"],
            temperature=settings["temperature"],
            top_p=settings["top_p"]
        )
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise


def render_main_app():
    """Render the main application interface."""
    # Apply theme
    apply_tesla_theme()
    
    # Render header
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {get_current_user()}")
        render_logout_button()
        st.markdown("---")
        
        # Generation controls
        settings = render_sidebar_controls()
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            clear_chat_history()
            st.rerun()
        
        # System info
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This assistant answers questions using 
        Tesla's official documents including:
        - Privacy Policies
        - Owner's Manual
        - Service Terms
        - Impact Reports
        """)
    
    # Initialize RAG system
    orchestrator = initialize_rag_system()
    
    if orchestrator is None:
        render_error("Failed to initialize the RAG system. Please check your configuration.")
        return
    
    # Initialize chat history
    init_chat_history()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat")
        
        # Chat container
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🚗"):
                        st.write(msg["content"])
                        if msg.get("metadata", {}).get("chunks"):
                            with st.expander("View Sources"):
                                for i, chunk in enumerate(msg["metadata"]["chunks"][:3]):
                                    source = chunk.get('metadata', {}).get('filename', 'Unknown')
                                    score = chunk.get('similarity_score', 0)
                                    st.caption(f"**{source}** (Score: {score:.3f})")
                                    st.text(chunk.get('content', '')[:200] + "...")
        
        # Query input
        query = st.chat_input("Ask a question about Tesla policies, products, or services...")
        
        if query:
            # Add user message to history
            add_to_chat_history("user", query)
            
            # Display user message
            with st.chat_message("user"):
                st.write(query)
            
            # Process query
            with st.chat_message("assistant", avatar="🚗"):
                with st.spinner("🔍 Searching Tesla documents..."):
                    try:
                        result = process_query(orchestrator, query, settings)
                        
                        # Display answer
                        st.write(result["answer"])
                        
                        # Add to history
                        add_to_chat_history("assistant", result["answer"], {
                            "chunks": result.get("chunks", []),
                            "metadata": result.get("metadata", {})
                        })
                        
                        # Store latest result for right panel
                        st.session_state.latest_result = result
                        
                    except Exception as e:
                        error_msg = f"Error processing your query: {str(e)}"
                        st.error(error_msg)
                        add_to_chat_history("assistant", error_msg)
    
    with col2:
        st.markdown("### 📚 Retrieved Context")
        
        if 'latest_result' in st.session_state and st.session_state.latest_result:
            result = st.session_state.latest_result
            chunks = result.get("chunks", [])
            metadata = result.get("metadata", {})
            
            # Stats
            st.markdown("#### 📊 Query Stats")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Time", f"{metadata.get('total_time', 0):.2f}s")
            with col_b:
                st.metric("Chunks", len(chunks))
            
            st.markdown("---")
            
            # Chunks
            if chunks:
                st.markdown("#### 📄 Source Documents")
                for i, chunk in enumerate(chunks):
                    source = chunk.get('metadata', {}).get('filename', 'Unknown')
                    score = chunk.get('similarity_score', 0)
                    content = chunk.get('content', '')
                    
                    with st.expander(f"**{i+1}. {source[:25]}...** (Score: {score:.3f})", expanded=(i == 0)):
                        st.markdown(f"**Similarity Score:** `{score:.4f}`")
                        st.markdown("**Content:**")
                        st.text_area(
                            label=f"chunk_{i}",
                            value=content,
                            height=150,
                            disabled=True,
                            label_visibility="collapsed"
                        )
            else:
                st.info("No context retrieved yet. Ask a question to see relevant documents.")
        else:
            st.info("Ask a question to see retrieved context and sources.")
            
            # Show sample questions
            st.markdown("#### 💡 Sample Questions")
            sample_questions = [
                "What is Tesla's privacy policy?",
                "How do I use the touchscreen?",
                "What safety features does Tesla have?",
                "What are the service terms?",
            ]
            for q in sample_questions:
                st.markdown(f"- {q}")


def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    init_chat_history()
    
    # Check authentication
    if not is_authenticated():
        render_login_page()
    else:
        render_main_app()


if __name__ == "__main__":
    main()
