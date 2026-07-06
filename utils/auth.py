import hashlib
import streamlit as st

# Username
USERNAME = "admin"

# Password = Walmi@123
PASSWORD_HASH = hashlib.sha256("Walmi@123".encode()).hexdigest()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.markdown("""
    <style>

    div[data-testid="stForm"]{

        background:white;

        padding:30px;

        border-radius:20px;

    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h1 style='text-align:center;'>🍽️ WALMI Dashboard Login</h1>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        login_btn = st.button(
            "Login",
            use_container_width=True
        )

        if login_btn:

            if (
                username == USERNAME and
                hash_password(password) == PASSWORD_HASH
            ):

                st.session_state.logged_in = True

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Invalid Username or Password")

    return False


def logout():

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in = False

        st.rerun()