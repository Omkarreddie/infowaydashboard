import streamlit as st
from datetime import datetime
import hashlib
from src.utils.css import image_to_base64, load_login_css
from src.utils.user_utils import load_users, save_users
from src.utils.forgot_password_utils import generate_otp, send_email_otp



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)


class LoginPage:

    def login(self):
        # ------------------ Load CSS -----------------
        load_login_css("css/loginstyle.css")

        # ------------------ Initialize session variables ------------------
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "page" not in st.session_state:
            st.session_state.page = "login"
        if "show_otp_form" not in st.session_state:
            st.session_state.show_otp_form = False
        if "login_trigger" not in st.session_state:
            st.session_state.login_trigger = False

        # ------------------ Logo and Title ------------------
        st.markdown(
            f"<img src='data:image/jpg;base64,{image_to_base64('images/logo.jpg')}' class='login-logo'>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='login-title'>Infoway Technosoft Solutions PVT LTD</div>",
            unsafe_allow_html=True
        )

        # ---------------- LOGIN PAGE ----------------
        if st.session_state.page == "login":
            username = st.text_input("Username", key="login_username")

            # Enter key callback
            def trigger_login():
                st.session_state.login_trigger = True

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
                on_change=trigger_login
            )

            # -------- Side by Side Buttons --------
            col1, col2 = st.columns(2)

            # Login (left)
            with col1:
                if st.button("Login", key="login_btn") or st.session_state.login_trigger:
                    st.session_state.login_trigger = False  # Reset trigger
                    if username in st.session_state.users:
                        user_data = st.session_state.users[username]
                        stored_password = user_data.get("password")
                        user_roles = user_data.get("roles", [])
                        email = user_data.get("email")
                        inactive = user_data.get("inactive", False)
                        is_admin = user_data.get("is_admin", False)

                        if inactive and not is_admin:
                            st.error("🚫 This user account is inactive. Please contact Admin.")
                        elif verify_password(stored_password, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = (
                                "admin" if is_admin else (user_roles[0] if user_roles else "user")
                            )

                            # Track last activity
                            save_users(st.session_state.users)

                            st.success("✅ Login Successful")
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error("Invalid Username or Password")
                    else:
                        st.error("Invalid Username or Password")

            # Forgot Password (right)
            with col2:
                if st.button("Forgot Password", key="forgot_pwd_btn"):
                    st.session_state.page = "forgot_password"

        # ---------------- FORGOT PASSWORD PAGE ----------------
        if st.session_state.get("page") == "forgot_password":
            st.subheader("🔑 Reset your password using OTP")
            forgot_email = st.text_input("Enter your registered email", key="forgot_email_input")

            if st.button("Send OTP", key="send_otp_btn"):
                found_user = None
                for uname, data in st.session_state.USERS.items():
                    if data.get("email") == forgot_email:
                        found_user = uname
                        break

                if found_user:
                    otp = str(generate_otp()).zfill(6)
                    st.session_state.otp = otp
                    st.session_state.reset_email = forgot_email
                    st.session_state.show_otp_form = True
                    send_email_otp(forgot_email, otp)
                    st.info("📩 OTP sent to your email.")
                else:
                    st.error("Email not found!")

        # ---------------- OTP FORM ----------------
        if st.session_state.get("show_otp_form"):
            entered_otp = st.text_input("Enter OTP", key="otp_input_field")
            new_password = st.text_input("Enter new password", type="password", key="otp_new_pwd")
            confirm_password = st.text_input("Confirm new password", type="password", key="otp_confirm_pwd")

            if st.button("Reset Password", key="reset_pwd_btn"):
                if str(entered_otp).strip() == str(st.session_state.get("otp")):
                    if new_password == confirm_password:
                        # Update password
                        for uname, data in st.session_state.USERS.items():
                            if data.get("email") == st.session_state.reset_email:
                                st.session_state.USERS[uname]["password"] = hash_password(new_password)
                                break
                        save_users(st.session_state.USERS)
                        st.success("✅ Password reset successfully!")
                        st.session_state.show_otp_form = False
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Invalid OTP")

        # ---------------- LOGOUT BUTTON ----------------
        if st.session_state.get("logged_in"):
            if st.sidebar.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.set_page_config(
    page_title="Infoway Dashboard",
    layout="centered",   # NOT "center"
)
            st.rerun
