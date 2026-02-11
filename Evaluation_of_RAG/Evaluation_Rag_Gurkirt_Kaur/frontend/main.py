import streamlit as st
import time
import sys
import os
import pandas as pd
import json
import plotly.express as px

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
    st.rerun()

def display_sidebar(user_info):
    """Display user information and navigation in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 User Profile")
        st.write(f"**Name:** {user_info['name']}")
        st.write(f"**Role:** {user_info['specialization']}")
        
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        view = st.radio("Go to:", ["💬 Chat Interface", "📊 Evaluation Dashboard"])
        
        st.markdown("---")
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
            
        return view

def evaluation_dashboard():
    """Display the Evaluation Dashboard"""
    st.markdown('<h1 class="main-header">📊 Medical RAG Evaluation Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Comparing **Base LLM** vs **Enhanced RAG Pipeline**")
    
    # Load Data
    try:
        results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evaluation", "evaluation_results.json")
        with open(results_path, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except FileNotFoundError:
        st.error("Evaluation results file not found. Please run `evaluate.py` first.")
        return

    # --- Aggregate Metrics ---
    st.subheader("📈 Overall Performance")

    # Calculate averages
    base_metrics = pd.DataFrame([d['Base_Metrics'] for d in data])
    rag_metrics = pd.DataFrame([d['RAG_Metrics'] for d in data])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Base LLM Metrics (Avg)")
        st.metric("Accuracy", f"{base_metrics['Accuracy'].mean():.2f}")
        st.metric("Completeness", f"{base_metrics['Completeness'].mean():.2f}")
        st.metric("Response Time", f"{base_metrics['Response Time'].mean():.2f}s")

    with col2:
        st.markdown("#### Enhanced RAG Metrics (Avg)")
        st.metric("Accuracy", f"{rag_metrics['Accuracy'].mean():.2f}", delta=f"{rag_metrics['Accuracy'].mean() - base_metrics['Accuracy'].mean():.2f}")
        st.metric("Faithfulness", f"{rag_metrics['Faithfulness'].mean():.2f}")
        st.metric("Completeness", f"{rag_metrics['Completeness'].mean():.2f}", delta=f"{rag_metrics['Completeness'].mean() - base_metrics['Completeness'].mean():.2f}")
        st.metric("Response Time", f"{rag_metrics['Response Time'].mean():.2f}s", delta=f"{rag_metrics['Response Time'].mean() - base_metrics['Response Time'].mean():.2f}", delta_color="inverse")

    st.info("""
    **ℹ️ Note on Performance:** 
    The **Enhanced RAG** system may show lower *Accuracy* on general queries compared to the Base LLM because it is strictly grounded in the provided medical dataset. 
    However, its higher **Faithfulness** ensures it correctly identifies when information is missing rather than hallucinating an answer. This "conservative" behavior is a critical safety feature for medical applications.
    """)

    # --- Visualizations ---
    st.subheader("📊 Comparative Analysis")

    # Prepare data for plotting
    metrics_to_plot = ['Accuracy', 'Completeness', 'Response Time']
    plot_data = []

    for metric in metrics_to_plot:
        plot_data.append({'System': 'Base LLM', 'Metric': metric, 'Value': base_metrics[metric].mean()})
        plot_data.append({'System': 'Enhanced RAG', 'Metric': metric, 'Value': rag_metrics[metric].mean()})

    plot_df = pd.DataFrame(plot_data)

    fig = px.bar(plot_df, x='Metric', y='Value', color='System', barmode='group', title="Average Metrics Comparison")
    st.plotly_chart(fig, use_container_width=True)

    # --- Detailed Analysis ---
    st.subheader("📝 Query Analysis")

    for i, row in df.iterrows():
        with st.expander(f"Query {i+1}: {row['Query']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Base LLM")
                st.info(row['Base_Answer'])
                st.caption(f"Accuracy: {row['Base_Metrics']['Accuracy']}, Time: {row['Base_Metrics']['Response Time']:.2f}s")
                
            with col2:
                st.markdown("### Enhanced RAG")
                st.success(row['RAG_Answer'])
                st.caption(f"Accuracy: {row['RAG_Metrics']['Accuracy']}, Faithfulness: {row['RAG_Metrics']['Faithfulness']}, Time: {row['RAG_Metrics']['Response Time']:.2f}s")
                
            st.markdown("**Ground Truth:**")
            st.warning(row['Ground_Truth'])
            
            if 'Retrieved_Context' in row and row['Retrieved_Context']:
                st.markdown("**Retrieved Context (Snippet):**")
                st.text(row['Retrieved_Context'][:500] + "...")

def search_interface():
    """Main search interface for authenticated users"""
    # Initialize system if not done
    if not initialize_system():
        st.stop()
    
    # Display header
    st.markdown('<h1 class="main-header">🏥 Medi-Secure : The Private Hospital Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Search for similar patient cases using AI-powered retrieval")
    
    # Additional Sidebar Info
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 System Stats")
        # Get system stats
        stats = st.session_state.rag_pipeline.get_system_stats()
        st.metric("Docs Indexed", stats['vector_store'].get('total_documents', 0))
        st.caption(f"Embedding: {stats['config']['embedding_model']}")
        
        # Rebuild button
        if st.button("🔄 Rebuild Index", help="Force rebuild the index"):
            with st.spinner("Rebuilding..."):
                success = st.session_state.rag_pipeline.initialize_vector_store(force_rebuild=True)
                if success:
                    st.success("Rebuilt!")
                    st.rerun()

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
                st.rerun()
    
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
                    
                    # Full transcription logic
                    full_text = doc.get('full_transcription', '')
                    if not full_text and hasattr(st.session_state.rag_pipeline, 'data_loader'):
                        try:
                            original_id = doc.get('original_id')
                            if original_id is not None:
                                df = st.session_state.rag_pipeline.data_loader.load_data()
                                if original_id < len(df):
                                    full_text = str(df.iloc[original_id]['transcription'])
                        except Exception as e:
                            pass
                    
                    if full_text:
                        st.markdown(f"""
                        <div style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; background-color: #f9f9f9; border-radius: 8px; white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 0.85em; line-height: 1.4;">
                        {full_text}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Full transcription not available.")
        else:
            st.error(f"Search failed: {result['response']}")

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
            # User authenticated, display sidebar and selected view
            view = display_sidebar(user_info)
            
            if view == "💬 Chat Interface":
                search_interface()
            elif view == "📊 Evaluation Dashboard":
                evaluation_dashboard()

if __name__ == "__main__":
    main()
