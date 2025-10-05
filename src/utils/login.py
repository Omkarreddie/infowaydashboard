import streamlit as st
import hashlib
import oracledb
from src.utils.css import image_to_base64, load_login_css
from src.utils.user_utils import load_users, save_users
from src.utils.forgot_password_utils import generate_otp, send_email_otp
from src.utils.jwt_utils import verify_token

# ------------------ Helpers ------------------
def hash_password(password: str) -> str:
    """Return SHA256 hash of password for local users"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify password against SHA256 hash"""
    return stored_password == hash_password(provided_password)


def md5_hash(password: str) -> str:
    """Return MD5 hash of password for Oracle AXUSERS"""
    return hashlib.md5(password.encode()).hexdigest()


# ------------------ Oracle Configuration ------------------
ORACLE_CONFIG = {
    "user": "omkar_python",
    "password": "log",
    "dsn": "172.16.16.152:1521/orcl"
}
ROLE_DASHBOARDS = {
    "SALES": "sales_dashboard",
    "MANAGER": "manager_dashboard",
    "USER": "user_dashboard"
}



def check_oracle_user(username: str, password: str):
    """Return True and role if Oracle AX user exists with matching MD5 password"""
    try:
        conn = oracledb.connect(**ORACLE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT USERNAME, PASSWORD, USERTYPE,ACTIVE FROM AXUSERS WHERE USERNAME = :u",
            {"u": username}
        )
        result = cursor.fetchone()
        if result:
            oracle_user, oracle_pwd, oracle_role,active_status = result
            if str(active_status).upper() in ["Y", "YES", "ACTIVE", "1", "TRUE",'T']:
                    return True, oracle_role
            else:
                    # User is inactive
                st.error("🚫 Oracle AX user is inactive.")
        return False, None
    except Exception as e:
        st.error(f"Oracle DB connection error: {e}")
        return False, None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ------------------ Login Page ------------------
class LoginPage:

    def login(self):
        # Initialize session state
        session_vars = [
            "logged_in", "users", "login_trigger", "forgot_password_page",
            "otp_reset_page", "otp", "reset_email", "username", "role", "page"
        ]
        for var in session_vars:
            if var not in st.session_state:
                st.session_state[var] = False if "logged_in" in var or "trigger" in var else None

        if st.session_state.users is None:
            st.session_state.users = load_users()

        # Check SSO token
        token = st.session_state.get("token", None)
        if token:
            payload = verify_token(token)
            if payload:
                st.session_state.logged_in = True
                st.session_state.username = payload["sub"]
                st.session_state.role = payload.get("role", "user")
                st.session_state.page = "dashboard"
                return

        if st.session_state.logged_in:
            return

        # Load CSS
        load_login_css("css/loginstyle.css")

        # Show correct page
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
            "<div class='login-title'>Infoway Technosoft Solutions Pvt Ltd</div>",
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
                # First, check local users
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
                        # Try Oracle fallback
                        oracle_valid, oracle_role = check_oracle_user(username, password)
                        if oracle_valid:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = oracle_role
                            st.success("✅ Login Successful via Oracle AX")
                            st.rerun()
                        else:
                            st.error("Invalid Username or Password")
                else:
                    # Oracle fallback if local user not found
                    oracle_valid, oracle_role = check_oracle_user(username, password)
                    if oracle_valid:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = oracle_role
                        st.success("✅ Login Successful via Oracle AX")
                        st.rerun()
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
