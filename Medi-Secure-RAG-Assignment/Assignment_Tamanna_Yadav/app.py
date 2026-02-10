"""
MediSecure RAG - Streamlit Application
A secure medical case retrieval system for healthcare professionals.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from auth import Authenticator
from rag import RAGPipeline
from config import settings

st.set_page_config(
    page_title="MediSecure RAG",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .security-badge {
        background-color: #E8F5E9;
        border: 1px solid #4CAF50;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #2E7D32;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #F8F9FA;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .score-badge {
        background-color: #1E88E5;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.85rem;
    }
    .specialty-tag {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .user-info-box {
        background-color: #F5F5F5;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF3E0;
        border: 1px solid #FF9800;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None


def login_page():
    """Render the login page."""
    st.markdown('<h1 class="main-header">🏥 MediSecure RAG</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Medical Case Retrieval System</p>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="security-badge">🔒 HIPAA-Compliant | On-Premise Data Processing | JWT Authentication</div>',
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Doctor Login")
        st.markdown("Please enter your credentials to access the system.")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g., dr.smith")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    authenticator = Authenticator()
                    success, token, user_data = authenticator.authenticate(username, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.token = token
                        st.session_state.user_info = user_data
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.warning("Please enter both username and password.")
        
        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        st.code("Username: dr.smith\nPassword: doctor123")


def sidebar_user_info():
    """Display user information in sidebar."""
    user = st.session_state.user_info
    
    st.sidebar.markdown("### 👨‍⚕️ Logged In")
    st.sidebar.markdown(f"**{user.get('name', 'Doctor')}**")
    st.sidebar.markdown(f"*{user.get('specialty', 'N/A')}*")
    st.sidebar.markdown(f"License: `{user.get('license_id', 'N/A')}`")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.user_info = None
        st.session_state.search_results = None
        st.rerun()


def init_rag_pipeline():
    """Initialize the RAG pipeline."""
    if st.session_state.rag_pipeline is None:
        pipeline = RAGPipeline()
        if pipeline.initialize():
            st.session_state.rag_pipeline = pipeline
            return True
        return False
    return True


def display_search_result(result: dict, index: int):
    """Display a single search result."""
    score = result.get('similarity_score', 0)
    specialty = result.get('specialty', 'Unknown')
    description = result.get('description', 'No description available')
    transcription = result.get('transcription', '')
    keywords = result.get('keywords', '')
    
    with st.expander(f"**Case #{index + 1}** - {specialty} (Similarity: {score:.1%})", expanded=(index == 0)):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Description:** {description}")
        
        with col2:
            st.markdown(f"<span class='score-badge'>{score:.1%} Match</span>", unsafe_allow_html=True)
        
        if keywords:
            st.markdown(f"**Keywords:** `{keywords[:200]}...`" if len(keywords) > 200 else f"**Keywords:** `{keywords}`")
        
        st.markdown("---")
        st.markdown("**Clinical Transcription:**")
        
        display_text = transcription[:1500] + "..." if len(transcription) > 1500 else transcription
        st.text_area(
            "Transcription",
            value=display_text,
            height=200,
            disabled=True,
            label_visibility="collapsed",
            key=f"trans_{index}"
        )


def main_app():
    """Render the main application."""
    sidebar_user_info()
    
    st.sidebar.markdown("### ⚙️ Settings")
    top_k = st.sidebar.slider("Number of results", min_value=1, max_value=10, value=5)
    show_ai_summary = st.sidebar.checkbox("Generate AI Summary", value=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔒 Security Info")
    st.sidebar.info(
        "All patient data remains on-premise. "
        "Only search queries are processed by the AI model. "
        "No raw transcriptions are transmitted externally."
    )
    
    st.markdown('<h1 class="main-header">🔍 Medical Case Search</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Search for clinically similar past cases using natural language</p>',
        unsafe_allow_html=True
    )
    
    if not init_rag_pipeline():
        st.error(
            "⚠️ Vector index not found. Please run the indexing script first:\n\n"
            "```bash\npython scripts/build_index.py\n```"
        )
        return
    
    st.markdown("### Enter Your Search Query")
    query = st.text_area(
        "Describe the symptoms or clinical presentation",
        placeholder="e.g., Patient presenting with persistent cough, fever, and shortness of breath...",
        height=100,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        search_button = st.button("🔍 Search Cases", use_container_width=True, type="primary")
    with col2:
        clear_button = st.button("🗑️ Clear Results", use_container_width=True)
    
    if clear_button:
        st.session_state.search_results = None
        st.rerun()
    
    if search_button and query:
        with st.spinner("Searching for similar cases..."):
            pipeline = st.session_state.rag_pipeline
            results = pipeline.search_similar_cases(query, top_k=top_k)
            st.session_state.search_results = {
                'query': query,
                'results': results,
                'show_summary': show_ai_summary
            }
    
    if st.session_state.search_results:
        results_data = st.session_state.search_results
        results = results_data['results']
        
        st.markdown("---")
        st.markdown(f"### 📋 Search Results ({len(results)} cases found)")
        st.markdown(f"*Query: \"{results_data['query']}\"*")
        
        if results_data.get('show_summary') and results:
            with st.spinner("Generating AI summary..."):
                pipeline = st.session_state.rag_pipeline
                summary = pipeline.generate_summary(results_data['query'], results)
                
                st.markdown("#### 🤖 AI Clinical Summary")
                st.info(summary)
        
        st.markdown("#### 📄 Retrieved Cases")
        
        for i, result in enumerate(results):
            display_search_result(result, i)


def main():
    """Main application entry point."""
    init_session_state()
    
    if st.session_state.authenticated:
        authenticator = Authenticator()
        is_valid, _ = authenticator.validate_session(st.session_state.token)
        
        if is_valid:
            main_app()
        else:
            st.session_state.authenticated = False
            st.session_state.token = None
            st.warning("Session expired. Please login again.")
            login_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
