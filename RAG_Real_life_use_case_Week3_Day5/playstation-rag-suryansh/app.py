import streamlit as st
from rag_engine import rag_pipeline_enhanced, ConversationMemory
from auth import login, check_auth

st.set_page_config(
    page_title="PlayStation AI Support",
    page_icon="🎮",
    layout="wide"
)

#styling
st.markdown("""
<style>

/* Background */
.stApp {
    background:
        radial-gradient(
            circle at 50% 50%,
            rgba(31, 111, 235, 0.12),
            transparent 70%
        ),
        radial-gradient(
            circle at 80% 90%,
            rgba(20, 30, 60, 0.6),
            transparent 50%
        ),
        linear-gradient(
            135deg,
            #0a0f1c 0%,
            #0d1426 40%,
            #0a0f1c 100%
        );

    color: #e6edf3;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f1628;
}

/* Headers */
h1, h2, h3 {
    color: #1f6feb !important;
    font-weight: 700;
}

/* Chat Messages */
.stChatMessage {
    background-color: #141a2b;
    border-radius: 14px;
    padding: 14px;
    border: 1px solid #1f2636;
}

/* User Bubble */
.stChatMessage[data-testid="stChatMessageUser"] {
    border-left: 4px solid #1f6feb;
}

/* Assistant Bubble */
.stChatMessage[data-testid="stChatMessageAssistant"] {
    border-left: 4px solid #ff8a5c;
}

/* Buttons */
.stButton>button {
    background-color: #1f6feb;
    color: white;
    border-radius: 24px;
    font-weight: 600;
    border: none;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    background-color: #1858c6;
}

/* Chat Input Arrow Button */
div[data-testid="stChatInput"] button {
    background-color: #ff8a5c !important;
    color: white !important;
    border-radius: 50% !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stChatInput"] button:hover {
    background-color: #e67649 !important;
    box-shadow: 0 0 8px rgba(255, 138, 92, 0.4);
}

/* Structured Data Box */
.structured-data {
    background-color: #1a2332;
    border-left: 3px solid #ffd700;
    padding: 12px;
    border-radius: 8px;
    margin-top: 10px;
}

/* Query Rewrite Indicator */
.query-rewrite {
    background-color: #2d1810;
    border-left: 3px solid #ff8a5c;
    padding: 8px;
    border-radius: 6px;
    font-size: 0.9em;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# login check
if not check_auth():
    login()
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory(max_turns=5)

#sidebar
with st.sidebar:
    st.title("⚙️ Control Center")
    st.markdown("---")

    # model settings
    st.markdown("### 🎛️ Model Settings")
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.1)
    show_cot = st.toggle("Show Reasoning (CoT)", value=False)
    
    st.markdown("### 🚀 Advanced Features")
    enable_rewriting = st.toggle("Query Rewriting", value=True, help="Rewrite queries using conversation context")
    
    st.markdown("### 📊 System Status")
    st.caption("Model: Llama-3.3-70B-Versatile")
    st.caption("Embedder: BGE-base-en-v1.5")
    st.caption("Reranker: MS-MARCO-MiniLM-L6")
    st.caption(f"Memory: {len(st.session_state.conversation_memory.history)} turns")

    st.markdown("---")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_memory.clear()
        st.rerun()

# main chat interface
st.title("🎮 PlayStation AI Support")
st.caption("Premium AI-powered assistance with conversational memory & advanced retrieval.")

# display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"] 
            
            if metadata.get("query_rewritten"):
                st.markdown(
                    f"""<div class="query-rewrite">
                    🔄 <strong>Query Enhanced:</strong> {metadata['rewritten_query']}
                    </div>""",
                    unsafe_allow_html=True
                )
            
            st.markdown(f"**System Confidence:** {metadata['confidence_label']}")
            
            with st.expander("📚 View Retrieved Source Context"):
                for i, chunk in enumerate(metadata["retrieved_chunks"]):
                    st.markdown(
                        f"**Source {i+1} (Score: {metadata['scores'][i]:.3f})**"
                    )
                    st.info(chunk)

#chat input
if prompt := st.chat_input("How can I help you with your PS5 today?"):

    # store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing PlayStation Knowledge Base..."):

            result = rag_pipeline_enhanced(
                prompt,
                st.session_state.conversation_memory,
                temperature=temperature,
                show_cot=show_cot,
                enable_rewriting=enable_rewriting,
                enable_reranking=True
            )

            answer = result["answer"]
            
            st.markdown(answer) # displaying answer
            
            if result["query_rewritten"]:
                st.markdown(
                    f"""<div class="query-rewrite">
                    🔄 <strong>Query Enhanced:</strong> {result['rewritten_query']}
                    </div>""",
                    unsafe_allow_html=True
                )
            
            st.markdown(f"**System Confidence:** {result['confidence_label']}")

            with st.expander("📚 View Retrieved Source Context"):
                for i, chunk in enumerate(result["retrieved_chunks"]):
                    st.markdown(
                        f"**Source {i+1} (Score: {result['scores'][i]:.3f})**"
                    )
                    st.info(chunk)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "metadata": {
            "retrieved_chunks": result["retrieved_chunks"],
            "scores": result["scores"],
            "confidence_label": result["confidence_label"],
            "structured_data": result["structured_data"],
            "query_rewritten": result["query_rewritten"],
            "rewritten_query": result["rewritten_query"]
        }
    })