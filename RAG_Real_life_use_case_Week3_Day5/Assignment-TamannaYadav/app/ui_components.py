"""
UI Components for Tesla RAG Streamlit App.
Tesla-themed reusable components.
"""

import streamlit as st
from typing import List, Dict, Any, Optional


def apply_tesla_theme():
    """Apply Tesla-inspired CSS styling."""
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --tesla-red: #e82127;
        --tesla-dark: #171a20;
        --tesla-gray: #393c41;
        --tesla-light: #f4f4f4;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #171a20 0%, #393c41 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-weight: 300;
    }
    
    .main-header .tesla-accent {
        color: #e82127;
        font-weight: 600;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #e8e8e8;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #393c41;
    }
    
    .assistant-message {
        background-color: #f8f8f8;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #e82127;
    }
    
    /* Chunk display styling */
    .chunk-card {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chunk-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    
    .chunk-source {
        font-weight: 600;
        color: #171a20;
    }
    
    .chunk-score {
        background-color: #e82127;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    
    .chunk-text {
        color: #393c41;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background-color: #f8f8f8;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-weight: 600;
        color: #171a20;
        margin-bottom: 0.5rem;
    }
    
    /* Stats display */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-box {
        background-color: #f4f4f4;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        flex: 1;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e82127;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Loading animation */
    .loading-text {
        color: #666;
        font-style: italic;
    }
    
    /* Error styling */
    .error-box {
        background-color: #fff5f5;
        border: 1px solid #e82127;
        border-radius: 8px;
        padding: 1rem;
        color: #c41e22;
    }
    
    /* Success styling */
    .success-box {
        background-color: #f0fff4;
        border: 1px solid #38a169;
        border-radius: 8px;
        padding: 1rem;
        color: #276749;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1><span class="tesla-accent">TESLA</span> Knowledge Assistant</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">
            Powered by RAG • Grounded in Tesla Documents
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_user_message(message: str):
    """Render a user message in chat."""
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 You:</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_assistant_message(message: str):
    """Render an assistant message in chat."""
    st.markdown(f"""
    <div class="assistant-message">
        <strong>🤖 Tesla Assistant:</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_chunk_card(chunk: Dict[str, Any], index: int):
    """Render a retrieved chunk card."""
    source = chunk.get('metadata', {}).get('filename', 'Unknown Source')
    score = chunk.get('similarity_score', 0)
    content = chunk.get('content', '')
    
    # Truncate content for display
    display_content = content[:500] + "..." if len(content) > 500 else content
    
    st.markdown(f"""
    <div class="chunk-card">
        <div class="chunk-header">
            <span class="chunk-source">📄 {source}</span>
            <span class="chunk-score">Score: {score:.3f}</span>
        </div>
        <div class="chunk-text">{display_content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_chunks_panel(chunks: List[Dict[str, Any]]):
    """Render the retrieved chunks panel."""
    if not chunks:
        st.info("No chunks retrieved for this query.")
        return
    
    st.markdown("### 📚 Retrieved Context")
    st.markdown(f"*Showing {len(chunks)} relevant document chunks*")
    
    for i, chunk in enumerate(chunks):
        with st.expander(f"Chunk {i+1}: {chunk.get('metadata', {}).get('filename', 'Unknown')[:30]}...", expanded=(i == 0)):
            render_chunk_card(chunk, i)


def render_stats(metadata: Dict[str, Any]):
    """Render query statistics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Retrieval Time", f"{metadata.get('retrieval_time', 0):.2f}s")
    
    with col2:
        st.metric("Generation Time", f"{metadata.get('generation_time', 0):.2f}s")
    
    with col3:
        st.metric("Total Time", f"{metadata.get('total_time', 0):.2f}s")
    
    with col4:
        st.metric("Chunks Used", metadata.get('num_chunks', 0))


def render_sidebar_controls() -> Dict[str, Any]:
    """
    Render sidebar controls and return selected values.
    
    Returns:
        Dict with temperature, top_p, and top_k values
    """
    st.sidebar.markdown("### ⚙️ Generation Controls")
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
        help="Lower = more factual, Higher = more creative"
    )
    
    top_p = st.sidebar.slider(
        "Top-P",
        min_value=0.5,
        max_value=1.0,
        value=0.9,
        step=0.05,
        help="Nucleus sampling parameter"
    )
    
    top_k = st.sidebar.selectbox(
        "Top-K Retrieval",
        options=[3, 5, 7, 10],
        index=1,
        help="Number of chunks to retrieve"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Settings Info")
    
    if temperature <= 0.2:
        st.sidebar.info("🎯 **Factual Mode**: Best for policy/legal queries")
    elif temperature <= 0.5:
        st.sidebar.info("⚖️ **Balanced Mode**: Good for general queries")
    else:
        st.sidebar.warning("🎨 **Creative Mode**: May increase hallucination risk")
    
    return {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k
    }


def render_error(message: str):
    """Render an error message."""
    st.markdown(f"""
    <div class="error-box">
        <strong>⚠️ Error:</strong> {message}
    </div>
    """, unsafe_allow_html=True)


def render_success(message: str):
    """Render a success message."""
    st.markdown(f"""
    <div class="success-box">
        <strong>✅ Success:</strong> {message}
    </div>
    """, unsafe_allow_html=True)


def render_loading():
    """Render loading indicator."""
    return st.spinner("🔍 Searching Tesla documents and generating response...")


def init_chat_history():
    """Initialize chat history in session state."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def add_to_chat_history(role: str, content: str, metadata: Optional[Dict] = None):
    """Add a message to chat history."""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "metadata": metadata or {}
    })


def render_chat_history():
    """Render the chat history."""
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            render_user_message(msg["content"])
        else:
            render_assistant_message(msg["content"])


def clear_chat_history():
    """Clear the chat history."""
    st.session_state.chat_history = []
