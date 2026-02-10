import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Search Cases", page_icon="🔍")

if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("🔒 Please login first to access search.")
    st.stop()

st.title("🔍 Search Patient Cases")

query = st.text_area(
    "Describe the patient case or symptoms:",
    height=100,
    placeholder="e.g. patient with chest pain and shortness of breath after exercise",
)
top_k = st.slider("Number of source documents", min_value=1, max_value=10, value=5)

col_search, col_compare = st.columns(2)

with col_search:
    search_clicked = st.button("🔎 RAG Search + Answer", type="primary")

with col_compare:
    compare_clicked = st.button("⚖️ Compare RAG vs Base LLM")

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

if search_clicked:
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Retrieving relevant cases and generating answer …"):
            try:
                resp = requests.post(
                    f"{API_URL}/generate",
                    json={"query": query, "top_k": top_k},
                    headers=headers,
                    timeout=60,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.subheader("💡 RAG-Generated Answer")
                    st.success(data["answer"])
                    st.markdown(f"*Based on {data['num_sources']} retrieved source documents.*")

                    if data.get("sources"):
                        with st.expander("📄 Source Documents"):
                            for i, src in enumerate(data["sources"], 1):
                                st.markdown(f"**Source {i}:** {src}")
                else:
                    st.error(f"Error: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend. Is it running?")
            except Exception as e:
                st.error(f"Error: {e}")

if compare_clicked:
    if not query:
        st.warning("Please enter a query.")
    else:
        col_rag, col_base = st.columns(2)

        with col_rag:
            st.subheader("🧠 RAG Answer")
            with st.spinner("Generating RAG answer …"):
                try:
                    resp = requests.post(
                        f"{API_URL}/generate",
                        json={"query": query, "top_k": top_k},
                        headers=headers,
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(data["answer"])
                        st.caption(f"Sources used: {data['num_sources']}")
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col_base:
            st.subheader("🤖 Base LLM Answer")
            with st.spinner("Generating base LLM answer …"):
                try:
                    resp = requests.post(
                        f"{API_URL}/base-generate",
                        json={"query": query, "top_k": top_k},
                        headers=headers,
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.info(data["answer"])
                        st.caption("No retrieval context used")
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
