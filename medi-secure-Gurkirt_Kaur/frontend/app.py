#!/usr/bin/env python3
"""
Simple Hospital RAG Frontend
Uses API for search and authentication
"""

import streamlit as st
import requests
import hashlib
from pathlib import Path

# Simple page setup
st.set_page_config(page_title="Medi-Secure", page_icon="🏥", layout="wide")

# Simple CSS
st.markdown("""
<style>
.main-header { font-size: 2rem; color: #2E86AB; text-align: center; }
.search-result { background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #e1e5e9; }
.similarity-badge { background: #28a745; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; }
.specialty-badge { background: #007bff; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; }
.transcription-box { 
    background-color: #f8f9fa; 
    padding: 1rem; 
    border-radius: 5px; 
    border-left: 4px solid #007bff;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE = "http://localhost:8000"

def login_api(username, password):
    """Login to API with JWT"""
    try:
        response = requests.post(f"{API_BASE}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def search_api(query, limit=5, token=None):
    """Search medical transcriptions with JWT"""
    if not token:
        return []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE}/search",
            json={"query": query, "limit": limit},
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_stats_api(token=None):
    """Get system statistics with JWT"""
    if not token:
        return {}
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/stats", headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}

def main():
    st.markdown('<h1 class="main-header">🏥 Medi-Secure: Your Private Hospital Assistant</h1>', unsafe_allow_html=True)
    
    # Simple session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.token = None
    
    # Login page
    if not st.session_state.logged_in:
        st.subheader("🔐 Doctor Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Try JWT login
            login_result = login_api(username, password)
            
            if login_result and 'access_token' in login_result:
                st.session_state.logged_in = True
                st.session_state.username = login_result['user']
                st.session_state.token = login_result['access_token']
                st.success(f"Welcome, {login_result['user']}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        # Show default credentials
        st.info("Default logins:\n- doctor / doctor123\n- admin / admin123")
        return
    
    # Main app after login
    st.write(f"👤 Logged in as: {st.session_state.username}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.token = None
            st.rerun()
    
    # Check API connection
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            st.error("❌ API server is not running. Please start it first:")
            st.code("cd app && python main.py")
            return
    except:
        st.error("❌ Cannot connect to API server. Please start it first:")
        st.code("cd app && python main.py")
        return
    
    # Search interface
    st.subheader("🔍 Search Patient Notes")
    
    query = st.text_input("Enter medical symptoms or condition:")
    num_results = st.selectbox("Number of results:", [3, 5, 10])
    
    if st.button("Search") and query:
        with st.spinner("Searching patient notes..."):
            results = search_api(query, num_results, st.session_state.token)
            
            if results:
                st.success(f"Found {len(results)} similar cases")
                
                for i, result in enumerate(results, 1):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="search-result">
                            <h4>Case {i}</h4>
                            <span class="similarity-badge">Similarity: {result['similarity']:.3f}</span>
                            <span class="specialty-badge">{result['medical_specialty']}</span>
                            <p><strong>Description:</strong> {result['description']}</p>
                            <p><strong>Full Transcription:</strong></p>
                            <div class="transcription-box">{result['text']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write("")
                        st.write("")
                        if st.button(f"📋 Copy", key=f"copy_{i}"):
                            st.code(result['text'], language=None)
                            st.success("Transcription copied to clipboard (select and copy above)")
                    
                    st.divider()
            else:
                st.warning("No similar cases found")
    
    # Statistics
    st.subheader("� System Statistics")
    
    stats = get_stats_api(st.session_state.token)
    
    if stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Transcriptions", stats['total_transcriptions'])
        with col2:
            st.metric("Medical Specialties", len(stats['medical_specialties']))
        
        st.write("**Medical Specialties:**")
        for specialty, count in list(stats['medical_specialties'].items())[:10]:
            st.write(f"- {specialty}: {count} cases")

if __name__ == "__main__":
    main()
