import streamlit as st

def login():

    # center container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <h2 style='text-align: center; color: #003791;'>
            🎮 PlayStation Secure Login
            </h2>
            """,
            unsafe_allow_html=True
        )

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # login button
        if st.button("Login", use_container_width=True):
            if username == "admin" and password == "ps5":
                st.session_state["authenticated"] = True
                st.rerun() # rerun app to immediately move past login screen
            else:
                st.error("Invalid credentials")


def check_auth():
    # returns True if user is authenticated, otherwise False
    return st.session_state.get("authenticated", False)
