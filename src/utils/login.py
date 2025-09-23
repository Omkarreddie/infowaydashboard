import streamlit as st
import hashlib
from src.utils.css import image_to_base64, load_login_css
from src.utils.user_utils import load_users, save_users
from src.utils.forgot_password_utils import generate_otp, send_email_otp
from src.utils.jwt_utils import verify_token   # NEW


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)


class LoginPage:

    def login(self):
        # ------------------ Initialize session state ------------------
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "users" not in st.session_state:
            st.session_state.users = load_users()

        # ------------------ 🔑 NEW: Check SSO token ------------------
        if not st.session_state.get("logged_in", False):
            token = st.session_state.get("token", [None])[0]

            if token:
                payload = verify_token(token)
                if payload:
                    st.session_state.logged_in = True
                    st.session_state.username = payload["sub"]
                    st.session_state.role = payload.get("role", "user")
                    st.session_state.page = "dashboard"
                    return  # ✅ skip showing login form

        # ------------------ Skip login form if already logged in ------------------
        if st.session_state.get("logged_in", False):
            return

        # ------------------ Load CSS -----------------
        load_login_css("css/loginstyle.css")

        # ------------------ Logo and Title ------------------
        st.markdown(
            f"<img src='data:image/jpg;base64,{image_to_base64('images/logo.jpg')}' class='login-logo'>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='login-title'>Infoway Technosoft Solutions Pvt ltd</div>",
            unsafe_allow_html=True
        )

        # ------------------ LOGIN FORM ------------------
        username = st.text_input("Username", key="login_username")

        def trigger_login():
            st.session_state.login_trigger = True

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            on_change=trigger_login
        )

        col1, col2 = st.columns(2)

        # Login button
        with col1:
            if st.button("Login", key="login_btn") or st.session_state.get("login_trigger", False):
                st.session_state.login_trigger = False
                if username in st.session_state.users:
                    user_data = st.session_state.users[username]
                    stored_password = user_data.get("password")
                    user_roles = user_data.get("roles", [])
                    inactive = user_data.get("inactive", False)
                    is_admin = user_data.get("is_admin", False)

                    if inactive and not is_admin:
                        st.error("🚫 This account is inactive.")
                    elif verify_password(stored_password, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = (
                            "admin" if is_admin else (user_roles[0] if user_roles else "user")
                        )
                        save_users(st.session_state.users)
                        st.success("✅ Login Successful")
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")
                else:
                    st.error("Invalid Username or Password")

        # Forgot Password button
        with col2:
            if st.button("Forgot Password", key="forgot_pwd_btn"):
                st.session_state.show_forgot_form = True

        # ------------------ Forgot Password & OTP (unchanged) ------------------
        # ... keep your existing forgot password + OTP logic ...
        # ------------------ Logout ------------------
        if st.session_state.get("logged_in"):
            if st.sidebar.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.rerun()
