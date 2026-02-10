import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Search Cases", page_icon="🔍")

if 'access_token' not in st.session_state or not st.session_state.access_token:
    st.warning("Please login first.")
    st.stop()

st.title("🔍 Search Patient Cases")

query = st.text_area("Describe the patient case or symptoms:", height=100)
top_k = st.slider("Number of results", min_value=1, max_value=10, value=3)

if st.button("Search"):
    if not query:
        st.warning("Please enter a query.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        try:
            with st.spinner("Searching knowledge base..."):
                response = requests.post(
                    f"{API_URL}/search",
                    json={"query": query, "top_k": top_k},
                    headers=headers
                )
                
            if response.status_code == 200:
                results = response.json()
                st.subheader(f"Found {len(results)} similar cases:")
                
                for i, res in enumerate(results):
                    with st.expander(f"Case #{i+1} (Score: {res.get('score', 0):.2f})"):
                        st.markdown(f"**Transcription:**\n{res['transcription']}")
                        if res.get('metadata'):
                             st.json(res['metadata'])
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")
