import streamlit as st
import requests

st.set_page_config(page_title="Clinical Case Retrieval System", layout="centered")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Remove default streamlit padding and margins */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 900px;
        }
        
        /* Reduce all spacing */
        .element-container {
            margin-bottom: 0.3rem;
        }
        
        h1 {
            margin-bottom: 0.2rem !important;
            font-size: 2rem !important;
        }
        
        h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
            font-size: 1.2rem !important;
        }
        
        p {
            margin-bottom: 0.3rem !important;
        }
        
        hr {
            margin: 0.8rem 0 !important;
        }
        
        /* Feature cards - equal height */
        .feature-card {
            background: #f8f9fa;
            padding: 0.9rem;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
            height: 85px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .feature-title {
            font-weight: 600;
            color: #262730;
            margin-bottom: 0.3rem;
            font-size: 0.9rem;
        }
        
        .feature-desc {
            color: #666;
            font-size: 0.8rem;
            line-height: 1.3;
        }
        
        /* Login button styling */
        .stButton>button {
            width: 100%;
            background: #4CAF50;
            color: white;
            font-weight: 600;
            padding: 0.6rem;
            border-radius: 8px;
            border: none;
            margin-top: 0.5rem;
        }
        
        .stButton>button:hover {
            background: #45a049;
        }
        
        /* Reduce input spacing */
        .stTextInput > div > div {
            margin-bottom: 0.3rem;
        }
        
        /* Make columns equal */
        [data-testid="column"] {
            gap: 0.75rem;
        }
    </style>
""", unsafe_allow_html=True)

# main header
st.title("🏥 Clinical Case Retrieval System")
st.caption("Secure RAG system for searching similar clinical transcriptions")

st.markdown("---")

# about section with feature cards
st.markdown("### 📋 About This System")

col1, col2 = st.columns(2, gap="small")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🔍 Smart Search</div>
        <div class="feature-desc">Search past clinical cases using symptoms and conditions</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🧠 AI-Powered Retrieval</div>
        <div class="feature-desc">Retrieve similar transcriptions using semantic RAG</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Evidence-Based</div>
        <div class="feature-desc">View evidence with confidence scores</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🔒 Secure & Private</div>
        <div class="feature-desc">All patient data kept locally and secure</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# login section
st.subheader("🔐 Doctor Login")

username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed")
st.caption("Username")

password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
st.caption("Password")

if "token" not in st.session_state:
    st.session_state.token = None

if st.button("Login", type="primary"):
    if not username or not password:
        st.error("Please enter both username and password")
    else:
        with st.spinner("Authenticating..."):
            res = requests.post(
                "http://localhost:8000/login",
                json={"username": username, "password": password}
            )
            
            data = res.json()
            
            if "token" in data:
                st.session_state.token = data["token"]
                st.success("✅ Login Successful")
                st.switch_page("pages/search.py")   # go to dashboard
            else:
                st.error("❌ Invalid Credentials")

# footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 0.8rem; margin-top: 0.5rem;'>Clinical Case Retrieval System v1.0 • Secure • HIPAA Compliant</p>",
    unsafe_allow_html=True
)