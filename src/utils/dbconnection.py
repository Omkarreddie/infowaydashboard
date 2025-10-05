# sso_oracle_dashboard.py
import streamlit as st
import oracledb
import pandas as pd

# ---------------- CONFIG ----------------
ORACLE_CONFIG = {
    "user": "omkar_python",
    "password":"log",
    "dsn": "172.16.16.152:1521/orcl"
}
st.set_page_config(page_title="Databse Connection", layout="wide")
st.title("Oracle SSO Dashboard")

# ---------------- LOGIN CHECK ----------------


# Sidebar with logout

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
    if 'conn' in locals():
        conn.close()

# ---------------- DASHBOARD EXAMPLE ----------------
st.subheader("Example Dashboard")
st.write("You can add charts and other widgets here.")
if st.button("Load Sample Data"):
    # Sample data
    data = {
        "Category": ["A", "B", "C", "D"],
        "Values": [23, 45, 12, 36]
    }
    df_sample = pd.DataFrame(data)
    st.bar_chart(df_sample.set_index("Category"))
    st.success("Sample data loaded!")
    if 'conn' in locals() and conn is not None:
        try:
            conn.close()
        except Exception:
            pass

# Sidebar user info and logout button (always visible)
st.sidebar.write(f"Logged in as: {st.session_state.get('username', 'Guest')}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
