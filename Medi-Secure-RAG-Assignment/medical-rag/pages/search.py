import streamlit as st
import requests
from backend.summarizer import medical_summary

st.set_page_config(page_title="Clinical Case Search")

#hiding sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)


#session safety checks
if "token" not in st.session_state:
    st.session_state.token = None

if "results" not in st.session_state:
    st.session_state.results = []

if "summary_index" not in st.session_state:
    st.session_state.summary_index = None


# if no token, show session expired and return to login option
if not st.session_state.token:

    st.title("Session Expired")
    st.info("Please login again to access Clinical Case Search")

    if st.button("Return to Login"):
        st.switch_page("app.py")

    st.stop()


# search form

st.title("Clinical Case Search")

query = st.text_input("Enter symptoms or condition")

if st.button("Search"):

    r = requests.get(
        "http://localhost:8000/search",
        params={"query": query},
        headers={"token": st.session_state.token}
    )

    data = r.json()

    st.session_state.results = data.get("results", [])
    st.session_state.summary_index = None


def relevance(dist):
    if dist < 1.0:
        return "🟢 High Relevance"
    elif dist < 1.3:
        return "🟡 Moderate Relevance"
    else:
        return "🔴 Low Relevance"


for i, item in enumerate(st.session_state.results):

    st.subheader(f"Clinical Case {i+1}")

    st.markdown(f"**Relevance:** {relevance(item['distance'])}")

    st.markdown("**Key Details**")
    st.write(item["text"][:800])

    if st.button("Generate Medical Summary", key=f"sum_{i}"):

        st.session_state.summary_index = i

    if st.session_state.summary_index == i:

        with st.spinner("Summarizing..."):

            summary = medical_summary(item["text"])

            st.markdown("### 🩺 Medical Summary")
            st.success(summary)

    st.divider()

if st.button("Logout"):
    st.session_state.token = None
    st.switch_page("app.py")
