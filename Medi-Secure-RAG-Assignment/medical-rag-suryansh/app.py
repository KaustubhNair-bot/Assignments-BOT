import streamlit as st
import requests

st.set_page_config(page_title="Clinical Case Retrieval System")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.title("Clinical Case Retrieval System")
st.caption("Secure RAG system for searching similar clinical transcriptions")

st.markdown("""
### About
This system allows authorized doctors to:
- Search past clinical cases using symptoms  
- Retrieve similar transcriptions using semantic RAG  
- View evidence with confidence scores  
- Keep all patient data locally and secure
""")

st.subheader("Doctor Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if "token" not in st.session_state:
    st.session_state.token = None

if st.button("Login"):

    res = requests.post(
        "http://localhost:8000/login",
        json={"username": username, "password": password}
    )

    data = res.json()

    if "token" in data:
        st.session_state.token = data["token"]
        st.success("Login Successful")
        st.switch_page("pages/search.py")   # go to dashboard
    else:
        st.error("Invalid Credentials")
