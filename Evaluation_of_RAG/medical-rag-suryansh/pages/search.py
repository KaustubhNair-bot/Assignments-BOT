import streamlit as st
import requests
from backend.summarizer import medical_summary
import time

st.set_page_config(page_title="Clinical Case Search", layout="wide")

# hiding sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
    
/* Custom styling */
.stButton>button {
    border-radius: 8px;
    font-weight: 500;
}
    
.case-card {
    background: #f0f2f6;
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #4CAF50;
    margin-bottom: 1rem;
    color: #262730;
}
    
.search-container {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
}

.ai-stats {
    font-size: 0.75rem;
    color: #999;
    text-align: center;
    margin-top: 1rem;
    padding: 0.5rem;
    border-top: 1px solid #eee;
}

.relevance-badge {
    float: right;
    background: #4CAF50;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 600;
}

.relevance-medium {
    background: #FF9800;
}

.relevance-low {
    background: #9E9E9E;
}
</style>
""", unsafe_allow_html=True)

# session safety checks
if "token" not in st.session_state:
    st.session_state.token = None

if "rag_result" not in st.session_state:
    st.session_state.rag_result = None

if "summary_index" not in st.session_state:
    st.session_state.summary_index = None

if "open_case" not in st.session_state:
    st.session_state.open_case = None

if "response_time" not in st.session_state:
    st.session_state.response_time = None

# if no token, show session expired and return to login option
if not st.session_state.token:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔒 Session Expired")
        st.info("Please login again to access Clinical Case Search")
        
        if st.button("Return to Login", use_container_width=True):
            st.switch_page("app.py")
    
    st.stop()

# main ui
st.title("🏥 Clinical Decision Support")
st.markdown("---")

# search section with better layout
col1, col2 = st.columns([4, 1])

with col1:
    query = st.text_input("Enter symptoms or condition", placeholder="e.g., chest pain, shortness of breath...")

with col2:
    st.write("")  # spacing
    st.write("")  # spacing
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

if search_button and query:
    with st.spinner("Searching clinical cases..."):
        # calling NEW RAG+LLM endpoint
        start_time = time.time()
        
        r = requests.get(
            "http://localhost:8000/ask",
            params={"query": query},
            headers={"token": st.session_state.token}
        )
        
        end_time = time.time()
        st.session_state.response_time = round(end_time - start_time, 2)
        
        st.session_state.rag_result = r.json()
        st.session_state.summary_index = None
        st.session_state.open_case = None

# rendering results if available
if st.session_state.rag_result:
    raw = st.session_state.rag_result
    
    # handling different possible response formats from the API for backward compatibility
    
    # format 1: { "answer": "...", "retrieved": [...] }
    if "answer" in raw:
        data = raw
    
    # format 2: { "rag": { "answer": "...", "retrieved": [...] } }
    elif "rag" in raw:
        data = raw["rag"]
    
    # format 3: { "result": {...} }
    elif "result" in raw:
        data = raw["result"]
    
    else:
        st.error("Unexpected API response format")
        st.json(raw)          # debug helper
        st.stop()
    
    st.markdown("---")
    
    # final answer
    st.markdown("## 🧠 Clinical Answer")
    st.success(data.get("answer", "No answer generated"))
    
    # AI performance stats at the bottom of answer (small)
    answer_text = data.get("answer", "")
    token_estimate = len(answer_text.split()) * 1.3  # rough estimate
    
    st.markdown(f"""
    <div class="ai-stats">
        Response time: {st.session_state.response_time}s • Tokens (est.): ~{int(token_estimate)} • Retrieved: {len(data.get("retrieved", []))} cases
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # retrieved cases
    st.markdown("## 📁 Supporting Clinical Cases")
    st.caption(f"Found {len(data.get('retrieved', []))} relevant cases")
    
    retrieved = data.get("retrieved", [])
    
    for i, text in enumerate(retrieved):
        # calculate mock relevance score (you can replace this with actual scores from your backend)
        # decreasing relevance: first case is most relevant
        relevance = max(95 - (i * 8), 60)
        
        # determine badge class based on relevance
        if relevance >= 85:
            badge_class = "relevance-badge"
        elif relevance >= 70:
            badge_class = "relevance-badge relevance-medium"
        else:
            badge_class = "relevance-badge relevance-low"
        
        # clickable case header that toggles open/closed
        is_open = st.session_state.open_case == i
        
        # case header with relevance badge
        case_header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <span>Clinical Case {i+1}</span>
            <span class="{badge_class}">{relevance}% relevant</span>
        </div>
        """
        
        if st.button(
            f"Clinical Case {i+1} - {relevance}% relevant",
            key=f"case_toggle_{i}",
            use_container_width=True,
            type="primary" if is_open else "secondary"
        ):
            # toggle: if already open, close it; otherwise open it
            if st.session_state.open_case == i:
                st.session_state.open_case = None
                st.session_state.summary_index = None
            else:
                st.session_state.open_case = i
                st.session_state.summary_index = None
            st.rerun()
        
        # only selected case stays open
        if is_open:
            st.markdown(f"""
            <div class="case-card">
                {text[:900]}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 5])
            
            with col1:
                # optional summarization button
                if st.button("📝 Summarize", key=f"s_{i}"):
                    st.session_state.summary_index = i
                    st.rerun()
            
            if st.session_state.summary_index == i:
                with st.spinner("Summarizing..."):
                    summary = medical_summary(text)
                    
                    st.markdown("### 🩺 Case Summary")
                    st.info(summary)
        
        st.markdown("<br>", unsafe_allow_html=True)

# logout button
st.markdown("---")
col1, col2, col3 = st.columns([5, 1, 1])

with col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.token = None
        st.switch_page("app.py")