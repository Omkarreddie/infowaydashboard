import streamlit as st
import hashlib
from src.utils.css import image_to_base64, load_login_css
from src.utils.user_utils import load_users, save_users
from src.utils.forgot_password_utils import generate_otp, send_email_otp
from src.utils.jwt_utils import verify_token


# ------------------ Helpers ------------------
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
        if "login_trigger" not in st.session_state:
            st.session_state.login_trigger = False
        if "forgot_password_page" not in st.session_state:
            st.session_state.forgot_password_page = False
        if "otp_reset_page" not in st.session_state:
            st.session_state.otp_reset_page = False
        if "otp" not in st.session_state:
            st.session_state.otp = None
        if "reset_email" not in st.session_state:
            st.session_state.reset_email = None

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
                    return

        # ------------------ Skip login form if already logged in ------------------
        if st.session_state.get("logged_in", False):
            return

        # ------------------ Load CSS -----------------
        load_login_css("css/loginstyle.css")

        # ------------------ Show correct page ------------------
        if st.session_state.forgot_password_page:
            self.forgot_password_form()
        elif st.session_state.otp_reset_page:
            self.otp_reset_form()
        else:
            self.login_form()

    # ------------------ LOGIN FORM ------------------
    def login_form(self):
        st.markdown(
            f"<img src='data:image/jpg;base64,{image_to_base64('images/logo.jpg')}' class='login-logo'>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='login-title'>Infoway Technosoft Solutions Pvt ltd</div>",
            unsafe_allow_html=True
        )

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

        with col2:
            if st.button("Forgot Password", key="forgot_pwd_btn"):
                st.session_state.forgot_password_page = True
                st.rerun()

    # ------------------ FORGOT PASSWORD FORM ------------------
    def forgot_password_form(self):
        st.subheader("🔑 Reset your password")
        forgot_email = st.text_input("Enter your registered email", key="forgot_email_input")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send OTP", key="send_otp_btn"):
                found_user = None
                for uname, data in st.session_state.users.items():
                    if data.get("email") == forgot_email:
                        found_user = uname
                        break

                if found_user:
                    otp = str(generate_otp()).zfill(6)
                    st.session_state.otp = otp
                    st.session_state.reset_email = forgot_email
                    st.session_state.otp_reset_page = True
                    st.session_state.forgot_password_page = False
                    send_email_otp(forgot_email, otp)
                    st.info("📩 OTP sent to your email.")
                    st.rerun()
                else:
                    st.error("Email not found!")

        with col2:
            if st.button("⬅️ Back"):
                st.session_state.forgot_password_page = False
                st.rerun()

    # ------------------ OTP + RESET FORM ------------------
    def otp_reset_form(self):
        st.subheader("🔐 Verify OTP and Reset Password")
        entered_otp = st.text_input("Enter OTP", key="otp_input_field")
        new_password = st.text_input("Enter new password", type="password", key="otp_new_pwd")
        confirm_password = st.text_input("Confirm new password", type="password", key="otp_confirm_pwd")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset Password", key="reset_pwd_btn"):
                if str(entered_otp).strip() == str(st.session_state.otp):
                    if new_password == confirm_password:
                        # Update password
                        for uname, data in st.session_state.users.items():
                            if data.get("email") == st.session_state.reset_email:
                                st.session_state.users[uname]["password"] = hash_password(new_password)
                                break
                        save_users(st.session_state.users)
                        st.success("✅ Password reset successfully!")
                        st.session_state.logged_in = True
                        st.session_state.otp_reset_page = False
                        st.session_state.otp = None
                        st.session_state.reset_email = None
                        st.rerun()
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Invalid OTP")

        with col2:
            if st.button("⬅️ Back", key="back_btn"):
                st.session_state.otp_reset_page = False
                st.session_state.forgot_password_page = True
                st.session_state.otp = None
                st.session_state.reset_email = None
                st.rerun()
