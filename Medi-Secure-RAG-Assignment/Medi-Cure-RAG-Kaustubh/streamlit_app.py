"""
MediCure RAG - Streamlit UI
A secure medical case search interface for healthcare professionals
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
    /* Main theme colors */
    :root {
        --primary-color: #3b82f6;
        --secondary-color: #14b8a6;
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.8);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(59, 130, 246, 0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
    }
    
    /* Card styling */
    .result-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
        transform: translateY(-2px);
    }
    
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
    
    /* Security badge */
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
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #60a5fa;
    }
    
    .stat-label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Button styling */
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
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.5rem;
        color: white;
    }
    
    .stSelectbox > div > div {
        background: #1e293b;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'specialties' not in st.session_state:
        st.session_state.specialties = []


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
            
            # Get user info
            user_response = requests.get(
                f"{API_BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                timeout=10
            )
            
            if user_response.status_code == 200:
                st.session_state.user = user_response.json()
                st.session_state.authenticated = True
                
                # Load specialties
                load_specialties()
                return True
        
        return False
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to the API server. Please make sure the backend is running.")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False


def logout():
    """Clear session and logout"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.specialties = []


def load_specialties():
    """Load available medical specialties"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/specialties",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            st.session_state.specialties = response.json()
    except:
        st.session_state.specialties = []


def search_cases(query: str, top_k: int, specialty_filter: str = None):
    """Search for similar medical cases"""
    try:
        search_body = {
            "query": query,
            "top_k": top_k
        }
        
        if specialty_filter:
            search_body["specialty_filter"] = specialty_filter
        
        response = requests.post(
            f"{API_BASE_URL}/search",
            headers={
                "Authorization": f"Bearer {st.session_state.token}",
                "Content-Type": "application/json"
            },
            json=search_body,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.session_state.authenticated = False
            st.error("Session expired. Please login again.")
            return None
        else:
            st.error(f"Search failed: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to the API server.")
        return None
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return None


def get_system_stats():
    """Get system statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/stats",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def render_login_page():
    """Render the login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🏥 MediCure RAG</h1>
        <p>Secure AI-Powered Medical Case Search System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👨‍⚕️ Doctor Login")
        st.markdown("Access the secure medical case search system")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)
            
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
        st.code("""
dr.smith / doctor123
dr.jones / doctor123  
dr.patel / doctor123
        """)
        
        st.markdown("""
        <div class="security-badge">
            🔒 All data is processed locally - Patient data never leaves the system
        </div>
        """, unsafe_allow_html=True)


def render_search_page():
    """Render the search page"""
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Info")
        if st.session_state.user:
            st.markdown(f"**{st.session_state.user.get('full_name', 'Doctor')}**")
            st.markdown(f"*{st.session_state.user.get('specialty', 'General')}*")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        
        # System stats
        st.markdown("### 📊 System Stats")
        stats = get_system_stats()
        if stats:
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.metric("Specialties", stats.get("num_specialties", 0))
            st.metric("MongoDB", "✅ Connected" if stats.get("mongodb_connected") else "⚠️ File Mode")
        
        st.markdown("---")
        st.markdown("""
        <div class="security-badge">
            🔒 Secure Local Processing
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("""
    <div class="main-header">
        <h1>🏥 MediCure RAG</h1>
        <p>Search for similar medical cases using AI-powered semantic search</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search form
    st.markdown("### 🔍 Search Medical Cases")
    
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="Describe symptoms, conditions, or medical terms...",
            label_visibility="collapsed"
        )
    
    with col2:
        top_k = st.selectbox("Results", [5, 10, 15, 20], index=0)
    
    with col3:
        specialty_options = ["All Specialties"] + st.session_state.specialties
        specialty = st.selectbox("Specialty", specialty_options, index=0)
    
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    
    # Search results
    if search_button and query:
        specialty_filter = None if specialty == "All Specialties" else specialty
        
        with st.spinner("🔎 Searching medical cases..."):
            results = search_cases(query, top_k, specialty_filter)
        
        if results:
            st.markdown("---")
            
            # Stats
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📋 Found **{results['total_results']}** matching cases")
            with col2:
                st.info(f"⏱️ Search completed in **{results['search_time_ms']}ms**")
            
            # Results
            if results['results']:
                for i, result in enumerate(results['results']):
                    with st.container():
                        score_percent = int(result['similarity_score'] * 100)
                        
                        # Header with badges
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### {result['sample_name']}")
                        with col2:
                            st.markdown(f"""
                            <span class="score-badge">{score_percent}% Match</span>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <span class="specialty-badge">{result['specialty']}</span>
                        <span style="color: #64748b; margin-left: 1rem;">Case #{result['case_id']}</span>
                        """, unsafe_allow_html=True)
                        
                        # Transcription
                        with st.expander("📄 View Full Transcription", expanded=i == 0):
                            st.markdown(result['transcription'])
                        
                        # Keywords
                        if result.get('keywords'):
                            keywords = [k.strip() for k in result['keywords'].split(',')[:8] if k.strip()]
                            if keywords:
                                keyword_html = " ".join([f'<span class="keyword-tag">{k}</span>' for k in keywords])
                                st.markdown(f"**Keywords:** {keyword_html}", unsafe_allow_html=True)
                        
                        st.markdown("---")
            else:
                st.warning("No matching cases found. Try adjusting your search terms.")
    
    elif search_button:
        st.warning("Please enter a search query.")


def main():
    """Main application entry point"""
    init_session_state()
    
    if st.session_state.authenticated:
        render_search_page()
    else:
        render_login_page()


if __name__ == "__main__":
    main()
