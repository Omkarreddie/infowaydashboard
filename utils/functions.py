import os
import pickle
import base64
import hashlib
import random 
import smtplib
from email.mime.text import MIMEText
import streamlit as st

# -------------------------- Image Helper --------------------------
def image_to_base64(image_path):
    """Convert image to base64 for embedding in HTML."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# -------------------------- Password Utils --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# -------------------------- USERS --------------------------
def save_users(users):
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/users.pkl", "wb") as f:
        pickle.dump(users, f)

def load_users():
    if os.path.exists("pickle_files/users.pkl"):
        with open("pickle_files/users.pkl", "rb") as f:
            users = pickle.load(f)
            if isinstance(users, dict):
                return users
    return {}

# -------------------------- DASHBOARD GROUPS --------------------------
def save_dashboard_groups(groups):
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/dashboard_groups.pkl", "wb") as f:
        pickle.dump(groups, f)

def load_dashboard_groups():
    if os.path.exists("pickle_files/dashboard_groups.pkl"):
        with open("pickle_files/dashboard_groups.pkl", "rb") as f:
            groups = pickle.load(f)
            if isinstance(groups, set):
                groups = {g: {"Description": ""} for g in groups}
                save_dashboard_groups(groups)
            return groups
    return {}

# -------------------------- DASHBOARDS --------------------------
def save_dashboards(dashboards):
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/dashboards.pkl", "wb") as f:
        pickle.dump(dashboards, f)

def load_dashboards():
    if os.path.exists("pickle_files/dashboards.pkl"):
        with open("pickle_files/dashboards.pkl", "rb") as f:
            dashboards = pickle.load(f)
            if isinstance(dashboards, dict):
                return dashboards
    return {}

# -------------------------- ROLES --------------------------
def save_roles(roles_map):
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/roles.pkl", "wb") as f:
        pickle.dump(roles_map, f)

def load_roles():
    if os.path.exists("pickle_files/roles.pkl"):
        with open("pickle_files/roles.pkl", "rb") as f:
            roles_map = pickle.load(f)
            if isinstance(roles_map, dict):
                return roles_map
    return {}

# -------------------------- RESPONSIBILITIES --------------------------
def save_responsibilities(responsibilities):
    os.makedirs("pickle_files", exist_ok=True)
    with open("pickle_files/responsibilities.pkl", "wb") as f:
        pickle.dump(responsibilities, f)

def load_responsibilities():
    if os.path.exists("pickle_files/responsibilities.pkl"):
        with open("pickle_files/responsibilities.pkl", "rb") as f:
            data = pickle.load(f)
            if isinstance(data, dict):
                return data
            elif isinstance(data, (list, set)):
                return {r: [] for r in data}
    return {}

def generate_otp():
        return str(random.randint(10000,100000))
def send_email_otp(to_email, otp):
        # Replace below with your real email credentials
        sender_email = "omkaradireddy143@gmail.com"
        sender_password = "mmih jxwl suoj xvti"  # Use App Password for Gmail

        msg = MIMEText(f"Your OTP for password reset is: {otp}")
        msg['Subject'] = "Password Reset OTP"
        msg['From'] = sender_email
        msg['To'] = to_email
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                st.success("OTP sent to Successfully ")
        except Exception as e:
            st.error(f"Failed to send email: {e}")
        
def load_login_css(css="css/loginstyle.css"):
    try:
        with open(css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css}")

def load_main_css(css="css/main.css"):
    try:
        with open(css, "r") as f:
            st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Css file not found:{css}")

