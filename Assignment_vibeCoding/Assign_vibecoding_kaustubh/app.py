import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from prompt import BASE_INSTRUCTIONS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

st.title("Groq Chat Interface")

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Prompt")
        system_prompt = st.text_area(
            "Enter system instructions here...",
            height=200,
            label_visibility="collapsed"
        )
    
    with col2:
        st.subheader("User Prompt")
        user_prompt = st.text_area(
            "Enter your message here...",
            height=200,
            label_visibility="collapsed"
        )

st.divider()

if "response" not in st.session_state:
    st.session_state.response = ""

if st.button("Generate Response", type="primary", use_container_width=True):
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        st.error("Please set your Groq API key in the .env file")
    elif not user_prompt:
        st.warning("Please enter a user prompt")
    else:
        with st.spinner("Generating response..."):
            try:
                messages = [
                    {"role": "system", "content": f"{BASE_INSTRUCTIONS}\n\n{system_prompt}"},
                    {"role": "user", "content": user_prompt}
                ]
                
                response = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=1024
                )
                
                st.session_state.response = response.choices[0].message.content
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()

st.subheader("Response")
response_container = st.container()
with response_container:
    response_text = st.text_area(
        "Response will appear here...",
        value=st.session_state.response,
        height=300,
        disabled=True,
        label_visibility="collapsed"
    )
