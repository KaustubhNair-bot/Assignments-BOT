import sys
from pathlib import Path
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
from rag.pipeline import rag_query
from app.auth import require_login, logout

# Require authentication first
require_login()

# Sidebar
st.sidebar.title("McDonald's Marketing RAG")
st.sidebar.write(f"Logged in as: {st.session_state.get('username')}")
logout()

st.title("🍔 McDonald's India Marketing Strategy Analyst")

st.write("""
Ask questions related to:
- Financial performance
- Competitor strategy
- Pricing & offers
- Digital expansion
- Menu-based campaigns
""")

query = st.text_area("Enter your strategic question:")

if st.button("Generate Strategy"):
    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing documents and generating strategy..."):
            result = rag_query(query, n_results=5)

        st.subheader("📊 Strategic Response")
        st.write(result["response"])

        st.subheader("📚 Retrieved Context Chunks")

        for i, source in enumerate(result["sources"]):
            with st.expander(f"Source {i+1} | Category: {source['metadata'].get('category')}"):
                st.write(f"**Document Type:** {source['metadata'].get('doc_type')}")
                st.write(f"**Year:** {source['metadata'].get('year')}")
                st.write(f"**Similarity Score:** {round(source['score'], 3)}")
                st.write(source["text"])
