# sso_oracle_dashboard.py
import streamlit as st
import oracledb
import pandas as pd
from src.utils.jwt_utils import verify_token  # ✅ use the same JWT validator

# ---------------- CONFIG ----------------
ORACLE_CONFIG = {
    "user": "omkar_python",
    "password": "log",
    "dsn": "172.16.16.152:1521/orcl"
}

# ---------------- FUNCTIONS ----------------
def require_login():
    """Check SSO token from URL and store user info in session_state."""
    if "user" in st.session_state:
        return st.session_state["user"]

    # Get token from query parameters (?token=...)
    
    token = st.session_state.get("token", [None])[0]

    if not token:
        st.error("Access denied. No SSO token provided.")
        st.stop()

    # Validate token locally
    payload = verify_token(token)
    if not payload:
        st.error("Invalid or expired token. Access denied.")
        st.stop()

    # Save user info in session_state
    user_info = {"username": payload["sub"], "role": payload.get("role", "user")}
    st.session_state["user"] = user_info
    st.session_state["token"] = token
    return user_info

def logout():
    """Clear session and reload app."""
    for key in ["user", "token"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ---------------- APP START ----------------
st.set_page_config(page_title="Oracle SSO Dashboard", layout="wide")
st.title("Oracle SSO Dashboard")

# ---------------- LOGIN CHECK ----------------
user = require_login()
st.success(f"Welcome {user['username']}! Role: {user['role']}")

# Sidebar with logout
st.sidebar.button("Logout", on_click=logout)

# ---------------- ORACLE DB CONNECTION ----------------
st.header("OracleDB Version & Axusers Table")
st.write(f"oracledb version: {oracledb.__version__}")

try:
    conn = oracledb.connect(**ORACLE_CONFIG)
    st.success("Connected to Oracle DB successfully!")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM axusers")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    st.subheader("Axusers Table Data")
    st.dataframe(df)

except oracledb.DatabaseError as e:
    st.error(f"Failed to connect to Oracle DB: {e}")
finally:
    if 'conn' in locals():
        conn.close()
        st.info("Database connection closed.")

# ---------------- DASHBOARD EXAMPLE ----------------
st.subheader("Example Dashboard")
st.write("You can add charts and other widgets here.")
