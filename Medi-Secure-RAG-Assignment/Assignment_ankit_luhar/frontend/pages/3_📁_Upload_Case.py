import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Upload Case", page_icon="📁")

if 'access_token' not in st.session_state or not st.session_state.access_token:
    st.warning("Please login first.")
    st.stop()

st.title("📁 Upload New Patient Case")

with st.form("upload_form"):
    transcription = st.text_area("Case Transcription", height=200, placeholder="Enter the detailed patient case or transcription here...")
    specialty = st.selectbox("Medical Specialty", ["General Medicine", "Cardiology", "Neurology", "Pulmonology", "Endocrinology", "Deontology", "Other"])
    keywords = st.text_input("Keywords (comma separated)", placeholder="e.g. fever, cough, hypertension")
    
    submitted = st.form_submit_button("Upload Case")
    
    if submitted:
        if not transcription:
            st.error("Transcription is required.")
        else:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            payload = {
                "transcription": transcription,
                "specialty": specialty,
                "keywords": keywords
            }
            
            try:
                with st.spinner("Uploading and indexing..."):
                    response = requests.post(f"{API_URL}/upload", json=payload, headers=headers)
                    
                if response.status_code == 200:
                    st.success("Case uploaded successfully! It is now searchable.")
                else:
                    st.error(f"Upload failed: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend.")
