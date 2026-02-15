import streamlit as st

def check_login(username, password):
    """
    Verifies credentials against hardcoded values.
    """
    return username == "admin" and password == "nike123"

def login_page():
    """
    Renders the login page and handles session state.
    Returns True if logged in, False otherwise.
    """

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.title("👟 Nike HR AI Consultant")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Secure Internal HR Access")
        st.write("Please enter your credentials to access the Nike HR AI Consultant.")

        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            submit_button = st.form_submit_button("Login", type="primary")

            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif check_login(username, password):
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        st.markdown("---")
        st.subheader("Demo Credentials")

        st.info("""
        **Available Demo Users:**
        - Username: `admin` | Password: `nike123` (HR Administrator)
        - Username: `hr_manager` | Password: `nike456` (HR Manager)
        """)

    return False


def logout():
    """
    Logs the user out.
    """
    st.session_state.logged_in = False
    st.rerun()
