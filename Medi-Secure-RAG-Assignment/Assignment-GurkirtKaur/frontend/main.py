"""
Streamlit Main Application for Secure Medical RAG System
Provides web interface for doctors to search medical cases with AI assistance
"""

import streamlit as st
import time
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import AuthManager, login_page
from rag.rag import RAGPipeline
from app.config import Config

# Configure Streamlit page
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .search-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        margin-bottom: 1rem;
    }
    .similarity-score {
        background-color: #e8f4f8;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        color: #0066cc;
    }
    .ai-response {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'rag_pipeline_initialized' not in st.session_state:
        st.session_state.rag_pipeline_initialized = False

def initialize_system():
    """Initialize the RAG system"""
    if st.session_state.rag_pipeline_initialized:
        return True
    
    with st.spinner("Initializing Medical RAG System..."):
        try:
            # Create RAG pipeline
            st.session_state.rag_pipeline = RAGPipeline()
            
            # Initialize vector store
            success = st.session_state.rag_pipeline.initialize_vector_store()
            
            if success:
                st.session_state.system_initialized = True
                st.session_state.rag_pipeline_initialized = True
                st.success("✅ System initialized successfully!")
                return True
            else:
                st.error("❌ Failed to initialize system. Please check data files.")
                return False
                
        except Exception as e:
            st.error(f"❌ Error initializing system: {str(e)}")
            return False

def logout():
    """Handle user logout"""
    if 'token' in st.session_state:
        del st.session_state.token
    # Keep RAG pipeline initialized to prevent rebuilding on next login
    # st.session_state.system_initialized = False
    # st.session_state.rag_pipeline = None
    # st.session_state.rag_pipeline_initialized = False
    st.rerun()

def display_user_info(user_info):
    """Display user information in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 User Information")
        st.write(f"**Name:** {user_info['name']}")
        st.write(f"**Specialization:** {user_info['specialization']}")
        st.write(f"**Username:** {user_info['username']}")
        
        if st.button("🚪 Logout", type="secondary"):
            logout()

def search_interface():
    """Main search interface for authenticated users"""
    # Initialize system if not done
    if not initialize_system():
        st.stop()
    
    # Display header
    st.markdown('<h1 class="main-header">🏥 Medi-Secure : The Private Hospital Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Search for similar patient cases using AI-powered retrieval")
    
    # Sidebar with system info
    with st.sidebar:
        st.markdown("### 📊 System Information")
        
        # Get system stats
        stats = st.session_state.rag_pipeline.get_system_stats()
        
        st.metric("Documents Indexed", stats['vector_store'].get('total_documents', 0))
        st.metric("Embedding Dimension", stats['vector_store'].get('embedding_dimension', 0))
        
        st.markdown("### ⚙️ Configuration")
        st.write(f"**Embedding Model:** {stats['config']['embedding_model']}")
        st.write(f"**Top K Results:** {stats['config']['top_k_retrieval']}")
        st.write(f"**Chunk Size:** {stats['config']['chunk_size']} chars")
        
        # Rebuild button
        if st.button("🔄 Rebuild Vector Store", help="Force rebuild the document index with full transcriptions"):
            with st.spinner("Rebuilding vector store with full transcriptions..."):
                success = st.session_state.rag_pipeline.initialize_vector_store(force_rebuild=True)
                if success:
                    st.success("Vector store rebuilt successfully! Full transcriptions are now available.")
                    st.rerun()
                else:
                    st.error("Failed to rebuild vector store")
    
    # Main search interface
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "🔍 Enter your medical search query:",
            placeholder="e.g., patient with chest pain and shortness of breath",
            key="search_query"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search examples
    with st.expander("💡 Search Examples"):
        example_queries = [
            "65-year-old male with chest pain and hypertension",
            "patient complaining of headache and dizziness",
            "child with fever and rash",
            "diabetic patient with foot ulcer",
            "elderly patient with confusion and memory loss"
        ]
        
        for example in example_queries:
            if st.button(f"📋 {example}", key=f"example_{example[:20]}"):
                st.session_state.search_query = example
    
    # Perform search
    if search_button and query:
        if not query.strip():
            st.warning("Please enter a search query.")
            return
        
        with st.spinner("🔍 Searching medical cases..."):
            # Perform RAG search
            result = st.session_state.rag_pipeline.search_and_respond(query)
            
            # Add to search history
            st.session_state.search_history.append({
                'query': query,
                'timestamp': time.time(),
                'success': result['success']
            })
        
        # Display results
        if result['success']:
            # Display AI response
            st.markdown("### 🤖 Assistant Insights")
            st.markdown(f'<div class="ai-response">{result["response"]}</div>', unsafe_allow_html=True)
            
            # Display retrieved documents
            st.markdown("### 📋 Retrieved Medical Cases")
            
            for i, (doc, similarity) in enumerate(result['retrieved_documents']):
                with st.expander(f"Case {i+1}: {doc['metadata']['sample_name']} - {doc['metadata']['medical_specialty']}"):
                    # Similarity score
                    st.markdown(f'<span class="similarity-score">Similarity: {similarity:.3f}</span>', unsafe_allow_html=True)
                    
                    # Metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Medical Specialty:** {doc['metadata']['medical_specialty']}")
                        st.write(f"**Chunk ID:** {doc['chunk_id'] + 1}/{doc['metadata']['total_chunks']}")
                    
                    with col2:
                        st.write(f"**Document ID:** {doc['doc_id']}")
                        if doc['metadata']['keywords']:
                            st.write(f"**Keywords:** {doc['metadata']['keywords']}")
                    
                    # Document text
                    st.markdown("**Content:**")
                    st.write(doc['text'])
                    
                    # Full transcription in scrollable format
                    st.markdown("**Complete Transcription:**")
                    
                    # Try to get full transcription from current chunk or load from original data
                    full_text = doc.get('full_transcription', '')
                    
                    if not full_text and hasattr(st.session_state.rag_pipeline, 'data_loader'):
                        try:
                            # Load the original transcription
                            original_id = doc.get('original_id')
                            if original_id is not None:
                                df = st.session_state.rag_pipeline.data_loader.load_data()
                                if original_id < len(df):
                                    full_text = str(df.iloc[original_id]['transcription'])
                        except Exception as e:
                            st.warning(f"Could not load full transcription: {str(e)}")
                    
                    if full_text:
                        st.markdown(f"""
                        <div style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; background-color: #f9f9f9; border-radius: 8px; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 0.85em; line-height: 1.4;">
                        {full_text}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Full transcription not available. Only showing chunk content above.")
        else:
            st.error(f"Search failed: {result['response']}")
    
    # Search history
    if st.session_state.search_history:
        st.markdown("---")
        st.markdown("### 📜 Recent Search History")
        
        # Show last 5 searches
        recent_searches = st.session_state.search_history[-5:]
        
        for i, search in enumerate(reversed(recent_searches)):
            status = "✅" if search['success'] else "❌"
            st.write(f"{status} {search['query']}")

def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Check if user is authenticated
    if 'token' not in st.session_state:
        # Show login page
        login_page(auth_manager)
    else:
        # Verify token
        user_info = auth_manager.get_current_user()
        
        if user_info is None:
            # Token invalid, show login
            login_page(auth_manager)
        else:
            # User authenticated, show main app
            display_user_info(user_info)
            search_interface()

if __name__ == "__main__":
    main()
