"""
MediCure RAG - Streamlit UI
A secure medical case search interface with LLM-powered answers
Supports RAG mode and Base LLM comparison
"""
import streamlit as st
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="MediCure RAG - Medical Case Search",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
    }
    
    .main-header h1 { color: white; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .main-header p { color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; }
    
    .specialty-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        padding: 0.25rem 0.75rem;
        border-radius: 2rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .score-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        padding: 0.25rem 0.75rem;
        border-radius: 2rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .keyword-tag {
        display: inline-block;
        background: rgba(148, 163, 184, 0.2);
        color: #94a3b8;
        padding: 0.15rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        margin: 0.15rem;
    }
    
    .security-badge {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 2rem;
        padding: 0.5rem 1rem;
        color: #10b981;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .rag-answer-box {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .base-answer-box {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(234, 179, 8, 0.3);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .mode-tag-rag {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        padding: 0.2rem 0.6rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .mode-tag-base {
        display: inline-block;
        background: rgba(234, 179, 8, 0.2);
        color: #eab308;
        padding: 0.2rem 0.6rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'authenticated': False,
        'token': None,
        'user': None,
        'specialties': [],
        'llm_available': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {st.session_state.token}"}


def login(username: str, password: str) -> bool:
    """Authenticate user with the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            
            user_response = requests.get(
                f"{API_BASE_URL}/auth/me",
                headers=api_headers(),
                timeout=10
            )
            
            if user_response.status_code == 200:
                st.session_state.user = user_response.json()
                st.session_state.authenticated = True
                load_specialties()
                check_llm_status()
                return True
        
        return False
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API server. Please make sure the backend is running.")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False


def logout():
    """Clear session and logout"""
    for key in ['authenticated', 'token', 'user', 'specialties', 'llm_available']:
        st.session_state[key] = False if key in ['authenticated', 'llm_available'] else ([] if key == 'specialties' else None)


def load_specialties():
    """Load available medical specialties"""
    try:
        response = requests.get(f"{API_BASE_URL}/specialties", headers=api_headers(), timeout=10)
        if response.status_code == 200:
            st.session_state.specialties = response.json()
    except:
        st.session_state.specialties = []


def check_llm_status():
    """Check if LLM is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", headers=api_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.llm_available = data.get("llm_available", False)
    except:
        st.session_state.llm_available = False


def search_cases(query: str, top_k: int, specialty_filter: str = None):
    """Search for similar medical cases (retrieval only)"""
    try:
        body = {"query": query, "top_k": top_k}
        if specialty_filter:
            body["specialty_filter"] = specialty_filter
        
        response = requests.post(
            f"{API_BASE_URL}/search",
            headers={**api_headers(), "Content-Type": "application/json"},
            json=body, timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.session_state.authenticated = False
            st.error("Session expired. Please login again.")
        else:
            st.error(f"Search failed: {response.text}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API server.")
        return None
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return None


def ask_rag(query: str, top_k: int, specialty_filter: str = None):
    """Ask a question using RAG + LLM"""
    try:
        body = {"query": query, "top_k": top_k}
        if specialty_filter:
            body["specialty_filter"] = specialty_filter
        
        response = requests.post(
            f"{API_BASE_URL}/ask",
            headers={**api_headers(), "Content-Type": "application/json"},
            json=body, timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"RAG+LLM failed: {response.text}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def ask_base_llm(query: str):
    """Ask a question using base LLM only"""
    try:
        body = {"query": query, "top_k": 5}
        
        response = requests.post(
            f"{API_BASE_URL}/ask-base",
            headers={**api_headers(), "Content-Type": "application/json"},
            json=body, timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Base LLM failed: {response.text}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def get_system_stats():
    """Get system statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", headers=api_headers(), timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def render_login_page():
    """Render the login page"""
    st.markdown("""
    <div class="main-header">
        <h1>MediCure RAG</h1>
        <p>Secure AI-Powered Medical Case Search with LLM Integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Doctor Login")
        st.markdown("Access the secure medical case search system")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if username and password:
                    with st.spinner("Authenticating..."):
                        if login(username, password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.markdown("**Demo Accounts:**")
        st.code("dr.smith / doctor123\ndr.jones / doctor123\ndr.patel / doctor123")
        
        st.markdown("""
        <div class="security-badge">
            All embeddings processed locally - LLM queries sent to Groq API
        </div>
        """, unsafe_allow_html=True)


def render_result_cards(results):
    """Render search result cards"""
    for i, result in enumerate(results):
        score_percent = int(result['similarity_score'] * 100)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{result['sample_name']}**")
        with col2:
            st.markdown(f'<span class="score-badge">{score_percent}% Match</span>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <span class="specialty-badge">{result['specialty']}</span>
        <span style="color: #64748b; margin-left: 0.5rem;">Case #{result['case_id']}</span>
        """, unsafe_allow_html=True)
        
        with st.expander("View Full Transcription", expanded=False):
            st.markdown(result['transcription'])
        
        if result.get('keywords'):
            keywords = [k.strip() for k in result['keywords'].split(',')[:6] if k.strip()]
            if keywords:
                keyword_html = " ".join([f'<span class="keyword-tag">{k}</span>' for k in keywords])
                st.markdown(f"Keywords: {keyword_html}", unsafe_allow_html=True)
        
        st.markdown("---")


def render_search_page():
    """Render the main search page"""
    # Sidebar
    with st.sidebar:
        st.markdown("### User Info")
        if st.session_state.user:
            st.markdown(f"**{st.session_state.user.get('full_name', 'Doctor')}**")
            st.markdown(f"*{st.session_state.user.get('specialty', 'General')}*")
        
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### System Stats")
        stats = get_system_stats()
        if stats:
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.metric("Specialties", stats.get("num_specialties", 0))
            st.metric("Storage", stats.get("storage", "FAISS + Local Cache"))
            st.metric("LLM Status", "Available" if stats.get("llm_available") else "Not Configured")
            if stats.get("llm_model"):
                st.caption(f"Model: {stats['llm_model']}")
        
        st.markdown("---")
        st.markdown("""
        <div class="security-badge">
            Secure Local Embeddings
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("""
    <div class="main-header">
        <h1>MediCure RAG</h1>
        <p>AI-Powered Medical Case Search with LLM-Generated Answers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mode selection tabs
    if st.session_state.llm_available:
        tab1, tab2, tab3 = st.tabs(["Retrieval Search", "RAG + LLM Answer", "RAG vs Base LLM Comparison"])
    else:
        tab1 = st.tabs(["Retrieval Search"])[0]
        tab2 = None
        tab3 = None
        st.info("LLM features not available. Set GROQ_API_KEY in .env to enable.")
    
    # TAB 1: Retrieval Only Search
    with tab1:
        st.markdown("### Search Medical Cases")
        st.caption("Find similar cases using semantic search (retrieval only, no LLM)")
        
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            query1 = st.text_input("Search Query", placeholder="Describe symptoms, conditions, or medical terms...", key="search_query", label_visibility="collapsed")
        with col2:
            top_k1 = st.selectbox("Results", [5, 10, 15, 20], index=0, key="search_topk")
        with col3:
            specialty_options = ["All Specialties"] + st.session_state.specialties
            specialty1 = st.selectbox("Specialty", specialty_options, index=0, key="search_spec")
        
        if st.button("Search", use_container_width=True, type="primary", key="search_btn"):
            if query1:
                specialty_filter = None if specialty1 == "All Specialties" else specialty1
                with st.spinner("Searching medical cases..."):
                    results = search_cases(query1, top_k1, specialty_filter)
                
                if results:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"Found **{results['total_results']}** matching cases")
                    with col2:
                        st.info(f"Search completed in **{results['search_time_ms']}ms**")
                    
                    if results['results']:
                        render_result_cards(results['results'])
                    else:
                        st.warning("No matching cases found.")
            else:
                st.warning("Please enter a search query.")
    
    # TAB 2: RAG + LLM Answer
    if tab2 is not None:
        with tab2:
            st.markdown("### Ask a Medical Question")
            st.caption("Get an AI-generated answer grounded in retrieved medical cases")
            
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                query2 = st.text_input("Your Question", placeholder="Ask a medical question...", key="ask_query", label_visibility="collapsed")
            with col2:
                top_k2 = st.selectbox("Context Cases", [3, 5, 7, 10], index=1, key="ask_topk")
            with col3:
                specialty2 = st.selectbox("Specialty", specialty_options, index=0, key="ask_spec")
            
            if st.button("Ask RAG", use_container_width=True, type="primary", key="ask_btn"):
                if query2:
                    specialty_filter = None if specialty2 == "All Specialties" else specialty2
                    with st.spinner("Retrieving cases and generating answer..."):
                        result = ask_rag(query2, top_k2, specialty_filter)
                    
                    if result:
                        st.markdown(f'<span class="mode-tag-rag">RAG + LLM Answer</span>', unsafe_allow_html=True)
                        st.markdown(f"**Model:** {result['model']} | **LLM Time:** {result['llm_time_ms']:.0f}ms | **Retrieval Time:** {result.get('retrieval_time_ms', 0):.0f}ms | **Tokens:** {result['tokens_used']['total_tokens']}")
                        
                        st.markdown("---")
                        st.markdown(result['answer'])
                        
                        if result.get('retrieved_cases'):
                            st.markdown("---")
                            st.markdown("### Retrieved Source Cases")
                            render_result_cards(result['retrieved_cases'])
                else:
                    st.warning("Please enter a question.")
    
    # TAB 3: Comparison Mode
    if tab3 is not None:
        with tab3:
            st.markdown("### RAG vs Base LLM Comparison")
            st.caption("Compare answers from RAG-augmented LLM vs base LLM to evaluate RAG effectiveness")
            
            query3 = st.text_input("Medical Question", placeholder="Enter a medical question to compare...", key="compare_query", label_visibility="collapsed")
            
            col1, col2 = st.columns(2)
            with col1:
                top_k3 = st.selectbox("Context Cases for RAG", [3, 5, 7], index=1, key="compare_topk")
            with col2:
                specialty3 = st.selectbox("Specialty Filter", specialty_options, index=0, key="compare_spec")
            
            if st.button("Compare RAG vs Base LLM", use_container_width=True, type="primary", key="compare_btn"):
                if query3:
                    specialty_filter = None if specialty3 == "All Specialties" else specialty3
                    
                    col_rag, col_base = st.columns(2)
                    
                    with col_rag:
                        st.markdown(f'<span class="mode-tag-rag">RAG + LLM</span>', unsafe_allow_html=True)
                        with st.spinner("Running RAG pipeline..."):
                            rag_result = ask_rag(query3, top_k3, specialty_filter)
                    
                    with col_base:
                        st.markdown(f'<span class="mode-tag-base">Base LLM (No Context)</span>', unsafe_allow_html=True)
                        with st.spinner("Querying base LLM..."):
                            base_result = ask_base_llm(query3)
                    
                    if rag_result and base_result:
                        col_rag, col_base = st.columns(2)
                        
                        with col_rag:
                            st.caption(f"Model: {rag_result['model']} | Time: {rag_result['llm_time_ms']:.0f}ms | Tokens: {rag_result['tokens_used']['total_tokens']} | Cases: {rag_result['num_contexts']}")
                            st.markdown("---")
                            st.markdown(rag_result['answer'])
                            
                            if rag_result.get('retrieved_cases'):
                                with st.expander("View Retrieved Cases"):
                                    for case in rag_result['retrieved_cases']:
                                        score_pct = int(case['similarity_score'] * 100)
                                        st.markdown(f"**{case['sample_name']}** ({case['specialty']}) - {score_pct}% match")
                        
                        with col_base:
                            st.caption(f"Model: {base_result['model']} | Time: {base_result['llm_time_ms']:.0f}ms | Tokens: {base_result['tokens_used']['total_tokens']} | No context")
                            st.markdown("---")
                            st.markdown(base_result['answer'])
                        
                        # Comparison stats
                        st.markdown("---")
                        st.markdown("### Comparison Summary")
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric("RAG Tokens", rag_result['tokens_used']['total_tokens'])
                        with c2:
                            st.metric("Base LLM Tokens", base_result['tokens_used']['total_tokens'])
                        with c3:
                            st.metric("RAG Time", f"{rag_result['llm_time_ms']:.0f}ms")
                        with c4:
                            st.metric("Base Time", f"{base_result['llm_time_ms']:.0f}ms")
                else:
                    st.warning("Please enter a question.")


def main():
    """Main application entry point"""
    init_session_state()
    
    if st.session_state.authenticated:
        render_search_page()
    else:
        render_login_page()


if __name__ == "__main__":
    main()
