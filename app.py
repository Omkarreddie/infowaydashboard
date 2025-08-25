import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import pickle
import hashlib
import PyPDF2
import numpy as np
import base64
import seaborn as sns 
import random 
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# -------------------------- Utility Functions --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password,provided_password):
    return stored_password==hash_password(provided_password)

def save_users(users):
    with open("pickle_files/users.pkl", "wb") as f:
        pickle.dump(users, f)

def load_users():
    if os.path.exists("pickle_files/users.pkl"):
        with open("pickle_files/users.pkl", "rb") as f:
            users = pickle.load(f)
            if users:
                return users
    return {}
def save_dashboard_groups():
    os.makedirs("pickle_files", exist_ok=True)  # Ensure folder exists
    with open("pickle_files/dashboard_groups.pkl", "wb") as f:
        pickle.dump({
            "Dashboard_groups": st.session_state.Dashboard_groups
        }, f)

def load_dashboard_groups():
    if os.path.exists("pickle_files/dashboard_groups.pkl"):
        with open("pickle_files/dashboard_groups.pkl", "rb") as f:
            data = pickle.load(f)
            groups = data.get("Dashboard_groups", {})

            # 🔧 If old data is a set, convert to dict
            if isinstance(groups, set):
                groups = {g: {"Description": ""} for g in groups}
                # Re-save in dict format so error never comes back
                with open("pickle_files/dashboard_groups.pkl", "wb") as fw:
                    pickle.dump({"Dashboard_groups": groups}, fw)

            return groups
    return {}
def save_dashboards():
    os.makedirs("pickle_files", exist_ok=True)  # create directory, not file
    with open("pickle_files/dashboards.pkl", "wb") as f:
        pickle.dump({
            "dashboards": st.session_state.dashboards
        }, f)

# Load dashboards from pickle
def load_dashboards():
    if os.path.exists("pickle_files/dashboards.pkl"):
        with open("pickle_files/dashboards.pkl", "rb") as f:
            data = pickle.load(f)
            return data.get("dashboards", {})
    return {}

# -------------------------- ROLES --------------------------
def save_roles():
    with open("pickle_files/roles.pkl", "wb") as f:
        pickle.dump({
            "ROLES_MAP": st.session_state.ROLES_MAP
        }, f)

def load_roles():
    if os.path.exists("pickle_files/roles.pkl"):
        with open("pickle_files/roles.pkl", "rb") as f:
            data = pickle.load(f)
            return data.get("ROLES_MAP", {})
    return {}

# -------------------------- RESPONSIBILITIES --------------------------

def save_responsibilities():
    os.makedirs("pickle_files", exist_ok=True)  # ensure folder exists
    with open("pickle_files/responsibilities.pkl", "wb") as f:
        # Always save the dict directly
        pickle.dump(st.session_state.RESPONSIBILITIES, f)

def load_responsibilities():
    if os.path.exists("pickle_files/responsibilities.pkl"):
        with open("pickle_files/responsibilities.pkl", "rb") as f:
            data = pickle.load(f)
            # ✅ Ensure dict format
            if isinstance(data, dict):
                return data
            elif isinstance(data, (list, set)):
                # old format migration → convert to dict
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
      
   

# -------------------------- Main App Class --------------------------
class InfowayApp():
    def __init__(self):
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if "show_otp_form" not in st.session_state:
            st.session_state.show_otp_form = False
        if "page" not in st.session_state:
            st.session_state.page = "login"
        if 'username' not in st.session_state:
            st.session_state.username = ""
        if 'role' not in st.session_state:
            st.session_state.role = ""
        if 'show_create_user_form' not in st.session_state:
            st.session_state.show_create_user_form = False
        if 'USERS' not in st.session_state:
            st.session_state.USERS = load_users()
        if 'RESPONSIBILITIES' not in st.session_state:
            st.session_state.RESPONSIBILITIES = load_responsibilities()
        if 'ROLES_MAP' not in st.session_state:
            st.session_state.ROLES_MAP = load_roles()
        if 'Dashboard_groups' not in st.session_state:
            st.session_state.Dashboard_groups=load_dashboard_groups()
        if 'dashboards' not in st.session_state:
            st.session_state.dashboards=load_dashboards()
    def run(self):
        if not st.session_state.USERS:
            return
        if st.session_state.logged_in:
            role = st.session_state.role.strip().lower()
            
            
            if role == "admin":
                self.admin_dashboard()
            #elif role in ["user", "salesmanager", "salesman1", "salesman2",
             #       "purchasemanager", "purchaseasst1", "purchaseasst2","View Purchase Chart"]:
              #  self.user_dashboard()
            elif  role:
                self.user_dashboard()
            else:
                st.warning("No dashboard found")


        else:
            self.login()

    def login(self):
        # Custom CSS
        st.markdown("""
            <style>
                .stApp { background: #e3f2fd; }
                .login-logo {
                    width: 120px; height: 120px; border-radius: 50%;
                    object-fit: contain; border: 3px solid #cccccc;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    margin-bottom: 25px; transition: transform 0.3s ease;
                }
                .login-logo:hover { transform: scale(1.05); }
                .login-title {
                    color: #2a2a2a; font-size: 26px; font-weight: bold;
                    margin-bottom: 25px;
                }
                label { color: #333333 !important; font-weight: bold; font-size: 14px; }
                div.stButton > button {
                    width: 100%; background: #42a5f5; color: white;
                    height: 45px; font-size: 16px; border-radius: 10px;
                    border: none; box-shadow: 0 3px 6px rgba(0,0,0,0.2);
                    transition: all 0.3s ease-in-out;
                }
                div.stButton > button:hover {
                    background: #1e88e5; transform: translateY(-2px);
                    box-shadow: 0 5px 10px rgba(0,0,0,0.3);
                }
            </style>
        """, unsafe_allow_html=True)

        # ✅ Logo
        st.markdown(
            f"<img src='data:image/jpg;base64,{image_to_base64('src/logo.jpg')}' class='login-logo'>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='login-title'>Infoway Technosoft Solutions PVT LTD</div>", unsafe_allow_html=True)

        # ---------------- LOGIN PAGE ----------------
        if st.session_state.page == "login":
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", key="login_btn"):
                if username in st.session_state.USERS:
                    user_data = st.session_state.USERS[username]

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
                        st.session_state.role = "admin" if is_admin else (user_roles[0] if user_roles else "user")

                        # ✅ Track last activity
                        st.session_state.USERS[username]["last_activity"] = {
                            "status": True,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_users(st.session_state.USERS)

                        st.success("✅ Login Successful")
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")
                else:
                    st.error("Invalid Username or Password")

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


            # -----------------------
    # Run login
    # -----------------------
        st.markdown("</div></div>", unsafe_allow_html=True)
            


    def admin_dashboard(self):
        st.sidebar.markdown(
            "<marquee behaviour='scroll' direction='left' scrollamount='5' style='color: blue; font-size:20px; font-style: italic;'>Welcome to the Infoway Dashboard!</marquee>",
            unsafe_allow_html=True,
        )
        st.set_page_config(layout="wide")

        # Inject CSS
        
        st.markdown("""
    <style>
        /* ================= Sidebar & Normal Buttons ================= */
        section[data-testid="stSidebar"] button,
        div.stButton > button {
            width: 190px;
            height: 45px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 16px;
            color: white;
            border: none;
            background: linear-gradient(135deg, #89CFF0, #70B7FF); /* Soft pastel blue */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* soft shadow */
            transition: all 0.3s ease-in-out;
        }

        section[data-testid="stSidebar"] button:hover,
        div.stButton > button:hover {
            background: linear-gradient(135deg, #70B7FF, #5A9DFF); /* Slightly darker on hover */
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        /* ================= Tabs ================= */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background-color: #F0F8FF;  /* Light soft background */
            padding: 8px;
            border-radius: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 8px;
            background-color: white;
            border: 1px solid #CFE2F3;
            color: #4178BE;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #89CFF0, #70B7FF);
            color: white !important;
            font-weight: bold;
            border: none;
        }

        /* ================= Main content padding ================= */
        div.block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)


        st.header("Admin Panel")
        st.sidebar.markdown("---")

        if "active_module" not in st.session_state:
            st.session_state.active_module = None
        
        if st.sidebar.button("Sales Module"):
            st.session_state.active_module= "sales"

        if st.sidebar.button("📦 Purchase Module"):
            st.session_state.active_module = "purchase"

        if st.sidebar.button("🛠️ Admin Portal"):
            st.session_state.active_module = "admin"
        
        if st.session_state.active_module == "sales":
                 #   if st.session_state.role in ["admin", "salesmanager", "salesman1","salesman2"]:
            sales_tabs=st.tabs({
                     "📊 View Sales Chart",
                     "📈 View Budgeting"
                 })
            with sales_tabs[0]:
                self.show_sales_chart()
            with sales_tabs[1]:
                self.show_budgeting_section()
        if st.sidebar.button("🚪 Logout"):
            self.logout() 
            st.success("Logout Successfully")
            st.rerun()
        # ========== PURCHASE MODULE ==========
        elif st.session_state.active_module == "purchase":
                purchase_tabs = st.tabs([
                "📊 Purchase Dashboard",
                "📑 LPO DATA",
                "📦 GRN DATA",
                "💰 LPO GRN Gross Amount",
                "📉 LPO GRN Net Values"
            ])

                # Tab 0: Show all data together
                with purchase_tabs[0]:
                    st.subheader("Purchase Dashboard")
                # Tab 1: LPO DATA only
                with purchase_tabs[1]:
                    st.subheader("LPO DATA")
                    self.lpo_data()

                # Tab 2: GRN DATA only
                with purchase_tabs[2]:
                    st.subheader("GRN DATA")
                    self.GRN()

                # Tab 3: LPO GRN Gross Amount only
                with purchase_tabs[3]:
                    st.subheader("LPO GRN Gross Amount")
                    self.lpo_grn_gross_amount()

                # Tab 4: LPO GRN Net Values only
                with purchase_tabs[4]:
                    st.subheader("LPO GRN Net Values")
                    self.lpo_grn_net_values()

        # ========== ADMIN MODULE ==========
        elif st.session_state.active_module == "admin":

            admin_tabs = st.tabs([
                "📊 Dashboard Groups",
                "🏠 Dashboard",
                "👥 Roles",
                "🧩 Responsibilities",
                "🙋 Users"
            ])

            with admin_tabs[0]:
                self.dashboardgroups()

            with admin_tabs[1]:
                self.dashboard()

            with admin_tabs[2]:
                self.manage_roles()

            with admin_tabs[3]:
                self.manage_responsibilities()

            with admin_tabs[4]:
                self.manage_users()
    def dashboardgroups(self):
        st.subheader("📊 Dashboard Groups")

        if st.button("➕ New Group"):
                st.session_state.add_group_page = True
                st.rerun()


        # --- Initialize session state ---
        if "Dashboard_groups" not in st.session_state:
            st.session_state.Dashboard_groups = load_dashboard_groups()

        if isinstance(st.session_state.Dashboard_groups, set):
            st.session_state.Dashboard_groups = {
                g: {"Description": ""} for g in st.session_state.Dashboard_groups
            }
            save_dashboard_groups()

        if "add_group_page" not in st.session_state:
            st.session_state.add_group_page = False
        if "edit_group" not in st.session_state:
            st.session_state.edit_group = None

        # --- MAIN LIST PAGE ---
        if not st.session_state.add_group_page and st.session_state.edit_group is None:
            st.write("### Dashboard Groups")
            if st.session_state.Dashboard_groups:
                cols = st.columns([2, 4])
                cols[0].markdown("**Group Name**")
                cols[1].markdown("**Description**")

                for g, d in st.session_state.Dashboard_groups.items():
                    row_cols = st.columns([2, 4])
                    with row_cols[0]:
                        if st.button(g, key=f"group_{g}"):
                            st.session_state.edit_group = g
                            st.rerun()
                    with row_cols[1]:
                        st.write(d["Description"])
            else:
                st.info("No dashboard groups added yet.")

        # --- ADD GROUP PAGE ---
        if st.session_state.add_group_page:
            st.subheader("🆕 Add New Dashboard Group")
            group_name = st.text_input("Group Name", key="new_grp_name")
            group_desc = st.text_input("Description", key="new_grp_desc")

            if st.button("Add Group"):
                if not group_name:
                    st.warning("Group name cannot be empty.")
                elif group_name in st.session_state.Dashboard_groups:
                    st.warning("Duplicate group name.")
                else:
                    st.session_state.Dashboard_groups[group_name] = {"Description": group_desc}
                    save_dashboard_groups()
                    st.success(f"✅ Group '{group_name}' added successfully!")
                    st.session_state.add_group_page = False
                    st.session_state.new_grp_name = ""
                    st.session_state.new_grp_desc = ""
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.add_group_page = False
                st.rerun()

        # --- EDIT GROUP PAGE ---
        if st.session_state.edit_group is not None:
            g = st.session_state.edit_group
            st.subheader(f"✏️ Edit Group: {g}")
            new_name = st.text_input("Edit Group Name", value=g, key="edit_name_input")
            new_desc = st.text_input(
                "Edit Description",
                value=st.session_state.Dashboard_groups[g]["Description"],
                key="edit_desc_input"
            )

            if st.button("Update"):
                if not new_name:
                    st.warning("Group name cannot be empty.")
                else:
                    if new_name != g:
                        st.session_state.Dashboard_groups.pop(g)
                    st.session_state.Dashboard_groups[new_name] = {"Description": new_desc}
                    save_dashboard_groups()
                    st.success(f"✅ Group '{new_name}' updated successfully!")
                    st.session_state.edit_group = None
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.edit_group = None
                st.rerun()


    def dashboard(self):
        st.subheader("📊 Dashboards")

        # --- Prepare dashboard groups list ---
        dashboard_groups = st.session_state.get("Dashboard_groups", {})
        if isinstance(dashboard_groups, dict):
            dashboard_groups_list = list(dashboard_groups.keys())
        elif isinstance(dashboard_groups, set):
            dashboard_groups_list = list(dashboard_groups)
        else:
            dashboard_groups_list = []

        # --- Initialize session state flags ---
        if "add_dashboard_page" not in st.session_state:
            st.session_state.add_dashboard_page = False
        if "edit_dashboard" not in st.session_state:
            st.session_state.edit_dashboard = None

        # --- MAIN LIST PAGE ---
        if not st.session_state.add_dashboard_page and st.session_state.edit_dashboard is None:
            if st.button("➕ New Dashboard"):
                st.session_state.add_dashboard_page = True
                st.rerun()

            st.subheader("Dashboards")
            if st.session_state.dashboards:
                cols = st.columns([2, 2, 4])
                cols[0].markdown("**Dashboard ID**")
                cols[1].markdown("**Dashboard Name**")
                cols[2].markdown("**Groups**")

                for d_name, details in st.session_state.dashboards.items():
                    row_cols = st.columns([2, 2, 4])
                    with row_cols[0]:
                        st.write(details["id"])
                    with row_cols[1]:
                        if st.button(d_name, key=f"dashboard_{d_name}"):
                            st.session_state.edit_dashboard = d_name
                            st.rerun()
                    with row_cols[2]:
                        st.write(", ".join(details["groups"]))
            else:
                st.info("No dashboards added yet.")

        # --- ADD DASHBOARD PAGE ---
        if st.session_state.add_dashboard_page:
            st.subheader("🆕 Add New Dashboard")
            new_name = st.text_input("Dashboard Name", key="new_db_name")
            selected_groups = st.multiselect("Dashboard Group", options=dashboard_groups_list, key="new_db_groups")

            # Auto-generate Dashboard ID
            if st.session_state.dashboards:
                max_id = max([int(details["id"]) for details in st.session_state.dashboards.values()])
                dashboard_id = f"{max_id + 1:04d}"
            else:
                dashboard_id = "0001"
            st.write(f"Dashboard ID: {dashboard_id}")

            if st.button("Add Dashboard"):
                if not new_name or not selected_groups:
                    st.warning("Please provide a dashboard name and select at least one group.")
                elif new_name in st.session_state.dashboards:
                    st.warning("Dashboard name already exists.")
                else:
                    st.session_state.dashboards[new_name] = {
                        "id": dashboard_id,
                        "groups": selected_groups
                    }
                    save_dashboards()
                    st.success(f"✅ Dashboard '{new_name}' added successfully!")
                    st.session_state.add_dashboard_page = False
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.add_dashboard_page = False
                st.rerun()

        # --- EDIT DASHBOARD PAGE ---
        if st.session_state.edit_dashboard is not None:
            d_name = st.session_state.edit_dashboard
            details = st.session_state.dashboards[d_name]

            st.subheader(f"✏️ Edit Dashboard: {d_name}")
            new_name = st.text_input("Dashboard Name", value=d_name, key="edit_db_name")
            selected_groups = st.multiselect(
                "Dashboard Groups",
                options=dashboard_groups_list,
                default=details["groups"],
                key="edit_db_groups"
            )
            dashboard_id = st.text_input("Dashboard ID", value=details["id"], disabled=True)

            if st.button("Update"):
                if not new_name or not selected_groups:
                    st.warning("Please provide a name and select at least one group.")
                else:
                    if new_name != d_name:
                        st.session_state.dashboards.pop(d_name)
                    st.session_state.dashboards[new_name] = {
                        "id": dashboard_id,
                        "groups": selected_groups
                    }
                    save_dashboards()
                    st.success(f"✅ Dashboard '{new_name}' updated successfully!")
                    st.session_state.edit_dashboard = None
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.edit_dashboard = None
                st.rerun()

    def manage_roles(self):
        st.header("👤 Manage Roles")

        # --- Initialize session state ---
        if "ROLES_MAP" not in st.session_state:
            st.session_state.ROLES_MAP = {}
        if "add_role_page" not in st.session_state:
            st.session_state.add_role_page = False
        if "edit_role" not in st.session_state:
            st.session_state.edit_role = None
        if "Dashboard_groups" not in st.session_state:
            st.session_state.Dashboard_groups = set()
        if "dashboards" not in st.session_state:
            st.session_state.dashboards = {}

        # --- Combined options for groups ---
        try:
            df = self.load_purchase_data()
            column_names = list(df.columns)
        except Exception:
            column_names = []
        combined_options = sorted(set(st.session_state.Dashboard_groups).union(column_names))

        # --- MAIN LIST PAGE ---
        if not st.session_state.add_role_page and st.session_state.edit_role is None:
            if st.button("➕ New Role"):
                st.session_state.add_role_page = True
                st.rerun()

            st.subheader("Roles")
            if st.session_state.ROLES_MAP:
                cols = st.columns([3, 5])
                cols[0].markdown("**Role Name**")
                cols[1].markdown("**Groups**")

                for role, data in sorted(st.session_state.ROLES_MAP.items()):
                    row_cols = st.columns([3, 5])
                    with row_cols[0]:
                        if st.button(role, key=f"role_{role}"):
                            st.session_state.edit_role = role
                            st.rerun()
                    with row_cols[1]:
                        st.write(", ".join(data.get("groups", [])))
            else:
                st.info("No roles defined yet.")

        # --- ADD ROLE PAGE ---
        if st.session_state.add_role_page:
            st.subheader("🆕 Add New Role")
            new_role = st.text_input("Enter New Role", key="new_role").strip()
            selected_groups = st.multiselect("Dashboard Groups", options=combined_options, key="new_role_groups")

            selected_dashboards = []
            if selected_groups:
                st.markdown("**Select Dashboards for this Role:**")
                for name, details in st.session_state.dashboards.items():
                    if any(group in details["groups"] for group in selected_groups):
                        if st.checkbox(f"{details['id']} - {name} ({', '.join(details['groups'])})", key=f"add_chk_{name}"):
                            selected_dashboards.append(name)

            if st.button("Add Role"):
                if not new_role or not selected_groups:
                    st.warning("Please enter a role name and select at least one group.")
                elif new_role in st.session_state.ROLES_MAP:
                    st.warning("Role already exists.")
                else:
                    st.session_state.ROLES_MAP[new_role] = {
                        "groups": selected_groups,
                        "dashboards": selected_dashboards
                    }
                    save_roles()
                    st.success(f"✅ Role '{new_role}' created successfully!")
                    st.session_state.add_role_page = False
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.add_role_page = False
                st.rerun()

        # --- EDIT ROLE PAGE ---
        if st.session_state.edit_role is not None:
            role_to_edit = st.session_state.edit_role
            role_data = st.session_state.ROLES_MAP.get(role_to_edit, {"groups": [], "dashboards": []})

            st.subheader(f"✏️ Edit Role: {role_to_edit}")
            new_name = st.text_input("Role Name", value=role_to_edit, key="edit_role_name")

            valid_defaults = [g for g in role_data.get("groups", []) if g in combined_options]
            selected_groups = st.multiselect(
                "Dashboard Groups",
                options=combined_options,
                default=valid_defaults,
                key="edit_role_groups"
            )

            selected_dashboards = []
            if selected_groups:
                st.markdown("**Select Dashboards for this Role:**")
                for name, details in st.session_state.dashboards.items():
                    if any(group in details["groups"] for group in selected_groups):
                        checked = name in role_data.get("dashboards", [])
                        if st.checkbox(f"{details['id']} - {name} ({', '.join(details['groups'])})", value=checked, key=f"edit_chk_{name}"):
                            selected_dashboards.append(name)

            if st.button("Update"):
                if not new_name or not selected_groups:
                    st.warning("Please enter a role name and select at least one group.")
                else:
                    if new_name != role_to_edit:
                        st.session_state.ROLES_MAP.pop(role_to_edit)
                    st.session_state.ROLES_MAP[new_name] = {
                        "groups": selected_groups,
                        "dashboards": selected_dashboards
                    }
                    save_roles()
                    st.success(f"✅ Role '{new_name}' updated successfully!")
                    st.session_state.edit_role = None
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.edit_role = None
                st.rerun()

    def manage_responsibilities(self):
        st.header("📝 Manage Responsibilities")

        # --- Initialize state ---
        if "RESPONSIBILITIES" not in st.session_state:
            st.session_state.RESPONSIBILITIES = {}
        if "add_resp_page" not in st.session_state:
            st.session_state.add_resp_page = False
        if "edit_resp" not in st.session_state:
            st.session_state.edit_resp = None
        if "ROLES_MAP" not in st.session_state:
            st.session_state.ROLES_MAP = {}

        # --- MAIN LIST PAGE ---
        if not st.session_state.add_resp_page and st.session_state.edit_resp is None:
            if st.button("➕ New Responsibility"):
                st.session_state.add_resp_page = True
                st.rerun()

            st.subheader("Responsibilities")
            if st.session_state.RESPONSIBILITIES:
                cols = st.columns([3, 5])
                cols[0].markdown("**Responsibility**")
                cols[1].markdown("**Roles**")
                for resp, roles in sorted(st.session_state.RESPONSIBILITIES.items()):
                    cols = st.columns([3, 5])
                    with cols[0]:
                        if st.button(resp, key=f"edit_{resp}"):
                            st.session_state.edit_resp = resp
                            st.rerun()
                    with cols[1]:
                        st.write(", ".join(roles))
            else:
                st.info("No responsibilities yet.")

        # --- ADD RESPONSIBILITY PAGE ---
        if st.session_state.add_resp_page:
            st.subheader("🆕 Add New Responsibility")
            new_resp = st.text_input("Enter New Responsibility", key="new_resp").strip()
            selected_roles = st.multiselect("Assign to Roles", list(st.session_state.ROLES_MAP), key="new_resp_roles")

            if st.button("Add Responsibility"):
                if not new_resp or not selected_roles:
                    st.warning("Please enter a responsibility and select at least one role.")
                elif new_resp in st.session_state.RESPONSIBILITIES:
                    st.warning("Responsibility already exists.")
                else:
                    st.session_state.RESPONSIBILITIES[new_resp] = selected_roles
                    save_responsibilities()
                    st.success(f"✅ Responsibility '{new_resp}' created successfully!")
                    st.session_state.add_resp_page = False
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.add_resp_page = False
                st.rerun()

        # --- EDIT RESPONSIBILITY PAGE ---
        if st.session_state.edit_resp is not None:
            resp_to_edit = st.session_state.edit_resp
            role_data = st.session_state.RESPONSIBILITIES.get(resp_to_edit, [])

            st.subheader(f"✏️ Edit Responsibility: {resp_to_edit}")
            new_name = st.text_input("Responsibility Name", value=resp_to_edit, key="edit_resp_name")
            selected_roles = st.multiselect(
                "Assign to Roles",
                options=list(st.session_state.ROLES_MAP),
                default=[r for r in role_data if r in st.session_state.ROLES_MAP],
                key="edit_resp_roles"
            )

            if st.button("Update"):
                if not new_name or not selected_roles:
                    st.warning("Please enter a name and select at least one role.")
                else:
                    if new_name != resp_to_edit:
                        st.session_state.RESPONSIBILITIES.pop(resp_to_edit)
                    st.session_state.RESPONSIBILITIES[new_name] = selected_roles
                    save_responsibilities()
                    st.success(f"✅ Responsibility '{new_name}' updated successfully!")
                    st.session_state.edit_resp = None
                    st.rerun()

            if st.button("⬅️ Cancel"):
                st.session_state.edit_resp = None
                st.rerun()

    def manage_users(self):
        st.header("👥 Manage Users")

        # --- Initialize session state ---
        if "USERS" not in st.session_state:
            st.session_state.USERS = {}
        if "add_user_page" not in st.session_state:
            st.session_state.add_user_page = False
        if "edit_user" not in st.session_state:
            st.session_state.edit_user = None

        # --- Main list page ---
        if not st.session_state.add_user_page and st.session_state.edit_user is None:
            if st.button("➕ Add New User"):
                st.session_state.add_user_page = True
                st.rerun()

            st.subheader("📋 Registered Users")
            if st.session_state.USERS:
                cols = st.columns([2, 3, 3, 2, 2])
                cols[0].markdown("**Username**")
                cols[1].markdown("**Responsibilities**")
                cols[2].markdown("**Email**")
                cols[3].markdown("**Inactive**")
                cols[4].markdown("**Admin**")

                for username, details in sorted(st.session_state.USERS.items()):
                    roles = details.get("roles", [])
                    email = details.get("email", "")
                    inactive = details.get("inactive", False)
                    is_admin = details.get("is_admin", False)

                    cols = st.columns([2, 3, 3, 2, 2])
                    with cols[0]:
                        if st.button(f"➡️ {username}", key=f"user_{username}"):
                            st.session_state.edit_user = username
                            st.rerun()
                    cols[1].write(", ".join(roles))
                    cols[2].write(email)
                    cols[3].write("YES" if inactive else "NO")
                    cols[4].write("YES" if is_admin else "NO")
            else:
                st.info("No registered users yet.")

        # --- Add User Page ---
        if st.session_state.add_user_page:
            st.subheader("🆕 Add New User")
            self.createuser(is_edit=False)
            if st.button("⬅️ Cancel"):
                st.session_state.add_user_page = False
                st.rerun()

        # --- Edit User Page ---
        if st.session_state.edit_user is not None:
            username = st.session_state.edit_user
            st.subheader(f"✏️ Edit User: {username}")
            self.createuser(is_edit=True, username=username)
            if st.button("⬅️ Cancel"):
                st.session_state.edit_user = None
                st.rerun()


    def createuser(self, is_edit=False, username=None):
        # --- Prepare defaults ---
        if is_edit and username:
            user_data = st.session_state.USERS[username]
            default_email = user_data.get("email", "")
            saved_roles = user_data.get("roles", [])
            inactive_status = user_data.get("inactive", False)
            is_admin_default = user_data.get("is_admin", False)
        else:
            username = ""
            default_email = ""
            saved_roles = []
            inactive_status = False
            is_admin_default = False

        available_roles = list(st.session_state.get("RESPONSIBILITIES", {}).keys())
        valid_saved_roles = [r for r in saved_roles if r in available_roles]

        with st.form("create_user_form"):
            username_input = st.text_input("Username", value=username, disabled=is_edit)
            email_input = st.text_input("Email", value=default_email)
            password_input = st.text_input("Password (leave blank to keep same)", type="password")

            inactive_checkbox = st.checkbox("Inactive User", value=inactive_status)
            is_admin_checkbox = st.checkbox("Admin User", value=is_admin_default)

            roles_input = st.multiselect(
                "Select Responsibilities",
                options=available_roles,
                default=valid_saved_roles
            )

            submitted = st.form_submit_button("Update User" if is_edit else "Create User")

        if submitted:
            if not username_input or not email_input:
                st.error("Please fill all required fields")
                return

            if is_edit:
                # Update existing user
                if password_input:
                    hashed_pw = hash_password(password_input)
                    st.session_state.USERS[username]["password"] = hashed_pw
                st.session_state.USERS[username]["email"] = email_input
                st.session_state.USERS[username]["roles"] = roles_input
                st.session_state.USERS[username]["inactive"] = inactive_checkbox
                st.session_state.USERS[username]["is_admin"] = is_admin_checkbox
                st.success("✅ User updated successfully")
                st.session_state.edit_user = None
            else:
                # Create new user
                if username_input in st.session_state.USERS:
                    st.warning("Username already exists")
                    return
                hashed_pw = hash_password(password_input)
                st.session_state.USERS[username_input] = {
                    "password": hashed_pw,
                    "roles": roles_input,
                    "email": email_input,
                    "inactive": inactive_checkbox,
                    "is_admin": is_admin_checkbox,
                    "last_activity": {"status": False, "date": None}
                }
                st.success("✅ User created successfully")
                st.session_state.add_user_page = False

            save_users(st.session_state.USERS)
            st.rerun()

    def logout(self):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.page = "login"
        st.rerun()

    def user_dashboard(self):
        st.title("User Dashboard")
        option = st.sidebar.radio("Select a user option", ["Home", "My Profile"], key="user_radio")
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            self.logout()
        if st.button("Create New User"):
            st.session_state.show_create_user_form = True
        if st.session_state.show_create_user_form:
            self.createuser()
        
        role = st.session_state.role
        responsibilities = st.session_state.ROLES_MAP.get(role, [])
        if option == "Home":
            st.write(f"Welcome User: {st.session_state.username}")
            if responsibilities:
                st.subheader("Your Responsibilities")
                for resp in responsibilities:
                    st.success(f"✅ {resp}")
            if "View Sales Chart" in responsibilities:
                st.subheader("Sales Dashboard")
                self.show_sales_chart()
            if "Budgeting Access" in responsibilities:
                st.subheader("Budgeting Section")
                self.show_budgeting_section()
            if "View Purchase Chart" in responsibilities:
                st.subheader("Purchase Dashboard")
                self.purchase()
            if "View Summary" in responsibilities:
                st.subheader("Purchase Summary")
                self.show_budgeting_section()
        elif option == "My Profile":
            st.write(f"Username: {st.session_state.username}")
            st.write(f"Role: {st.session_state.role}")
            st.write("Company: Infoway Technosoft Solutions")

    def logout(self):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.page = "home"
        st.success("Logged out successfully!")
        st.rerun()

    def show_sales_chart(self):
        st.subheader("Sales Data Charts")
        if not os.path.exists("data/sales_data.csv"):
            st.error("Your file does not exist")
            return
        df = pd.read_csv("data/sales_data.csv")
        st.dataframe(df)
        st.bar_chart(data=df, x="City", y="Total")
        data = {'Name': ['Omkar', 'Lakshman', 'Ajay'], 'Sales': [24, 25, 23], 'Location': ['Nellore', 'Chennai', 'Hyderabad']}
        df_chart = pd.DataFrame(data)
        st.title("Sales")
        fig, ax = plt.subplots()
        ax.bar(df_chart["Name"], df_chart["Sales"], color="blue")
        ax.set_title("Sales by Person")
        ax.set_xlabel("Name")
        ax.set_ylabel("Sales")
        st.pyplot(fig)

    def show_budgeting_section(self):
        st.write("📋 This is the budgeting area.")
        budget_data = {"Department": ["Sales", "Marketing", "HR"], "Budget": [150000, 100000, 80000]}
        df_budget = pd.DataFrame(budget_data)
        st.dataframe(df_budget)
        st.bar_chart(df_budget.set_index("Department"))
    def load_purchase_data(self,file_path="data/lpo_data.csv"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Purchase file not found: {file_path}")

        # Try reading as CSV first
        try:
            df = pd.read_csv(file_path)
        except Exception:
            # If CSV read fails, try tab-delimited
            df = pd.read_csv(file_path, sep="\t")

        # If only 1 column, maybe it's tab or space separated
        if len(df.columns) == 1:
            # Try again with tab separation
            try:
                df = pd.read_csv(file_path, sep="\t")
            except Exception:
                # If still not right, try whitespace separation
                df = pd.read_csv(file_path, delim_whitespace=True)

        # Clean column names: strip spaces, remove special chars
        df.columns = df.columns.str.strip()
        
        
        # Check if 'Project' column exists
        if 'Project' not in df.columns:
            raise KeyError(f"'Project' column not found after cleanup. Found columns: {df.columns.tolist()}")

        return df

    def lpo_data(self):
        st.title("📊 Purchase Dashboard")

        df = self.load_purchase_data()

        # Create a proper Date column from Year + Month
        df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")

        # Sidebar filters
        projects = st.multiselect(
            "Select Projects",
            options=sorted(df["Project"].unique()),
            default=[],
            placeholder="Choose project(s)..."
        )

        view_mode = st.radio(
            "View Mode",
            options=["Yearly", "Monthly"],
            index=0,
            horizontal=True,
            key="radio"
        )

        # Only move forward if projects are selected
        if not projects:
            st.info("👆 Please select at least one project to view data.")
            return

        # Apply project filter
        df_filtered = df[df["Project"].isin(projects)]

        if df_filtered.empty:
            st.warning("No data available for the selected project(s).")
            return

        if view_mode == "Yearly":
            df_grouped = df_filtered.groupby("Year", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Year"].astype(str), df_grouped["Amount"])
            ax.set_title("Yearly Purchase Amount")
            ax.set_xlabel("Year")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        elif view_mode == "Monthly":
            # Don’t auto-show until a year is picked
            selected_year = st.selectbox(
                "Select Year", 
                sorted(df_filtered["Year"].unique()),
                index=None,
                placeholder="Choose a year..."
            )

            if not selected_year:
                st.info("👆 Please select a year to see monthly details.")
                return

            df_year = df_filtered[df_filtered["Year"] == selected_year]
            df_grouped = df_year.groupby("Month", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Month"].astype(str), df_grouped["Amount"])
            ax.set_title(f"Monthly Purchase Amount - {selected_year}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

    def GRN(self):
        st.subheader("GOOD RECIEVE NOTE DATA")
        if not os.path.exists("data/grn_data.csv"):
            raise FileNotFoundError(f"Purchase file not found: {"data/grn_data.csv"}")

        # Try reading as CSV first
        try:
            df = pd.read_csv("data/grn_data.csv")
        except Exception:
            # If CSV read fails, try tab-delimited
            df = pd.read_csv("data/grn_data.csv", sep="\t")

        # If only 1 column, maybe it's tab or space separated
        if len(df.columns) == 1:
            # Try again with tab separation
            try:
                df = pd.read_csv("data/grn_data.csv", sep="\t")
            except Exception:
                # If still not right, try whitespace separation
                df = pd.read_csv("data/grn_data.csv", delim_whitespace=True)

        # Clean column names: strip spaces, remove special chars
        df.columns = df.columns.str.strip()
        
        # Check if 'Project' column exists
        if 'Project' not in df.columns:
            raise KeyError(f"'Project' column not found after cleanup. Found columns: {df.columns.tolist()}")

        df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")

        # Sidebar filters
        projects = st.multiselect(
            "Select Projects",
            options=sorted(df["Project"].unique()),
            default=[]
        )

        view_mode = st.radio(
            "View Mode",
            options=["Yearly", "Monthly"],
            index=0,
            horizontal=True
        )

        # Apply project filter
        df_filtered = df[df["Project"].isin(projects)]

        if view_mode == "Yearly":
            df_grouped = df_filtered.groupby("Year", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Year"].astype(str), df_grouped["Amount"])
            ax.set_title("Yearly Purchase Amount")
            ax.set_xlabel("Year")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        elif view_mode == "Monthly":
            # Let user choose year for monthly view
            selected_year = st.selectbox("Select Year", sorted(df_filtered["Year"].unique()))
            df_year = df_filtered[df_filtered["Year"] == selected_year]
            df_grouped = df_year.groupby("Month", as_index=False)["Amount"].sum()
            fig, ax = plt.subplots()
            ax.bar(df_grouped["Month"].astype(str), df_grouped["Amount"])
            ax.set_title(f"Monthly Purchase Amount - {selected_year}")
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount")
            st.pyplot(fig)
        
    def lpo_grn_gross_amount(self):
        csv_path = "data/lpo_grn.csv"

        st.title("LPO vs GRN – By Project")


        # Load the CSV with utf-8-sig encoding to handle BOM if present
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
        except Exception as e:
            st.error(f"Error loading CSV with pandas: {e}")
            return
        # Strip whitespace from column headers
        df.columns = df.columns.str.strip()
       

        # Check if 'Project' column exists
        if 'Project' not in df.columns:
            st.error("Required column 'Project' not found in data.")
            return

        projects = df['Project'].unique().tolist()
        selected_projects = st.multiselect("Select Projects (max 15)", projects, default=[])

        if len(selected_projects) > 15:
            st.warning("Please select 15 or fewer projects.")
            st.stop()

        if not selected_projects:
            st.info("Please select at least one project.")
            st.stop()

        filtered_df = df[df['Project'].isin(selected_projects)].reset_index(drop=True)

        x = np.arange(len(filtered_df))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 7))
        ax.bar(x - width/2, filtered_df['PO_Value'], width, label='LPO Value')
        ax.bar(x + width/2, filtered_df['GRN_Value'], width, label='GRN Value')

        ax.set_xticks(x)
        ax.set_xticklabels(filtered_df['Project'], rotation=45, ha='right')
        ax.set_xlabel("Project Codes")
        ax.set_ylabel("Value in OMR")
        ax.set_title("LPO vs GRN Values by Project")
        ax.legend()

        plt.tight_layout()
        st.pyplot(fig)

    def lpo_grn_net_values(self):
            data = pd.read_csv("data/lpo_grn_net_value.csv")
            data.columns = data.columns.str.strip()

            # Add Net_Cost column
            data['Net_Cost'] = data['PO_Net Value'] + data['GRN_Net Value']

            projects = sorted(data['Project'].unique().tolist())
            selected_projects = st.multiselect(
        "Select Projects (max 15)", 
        projects, 
        default=[], 
        key="lpo_grn_projects"    # 👈 unique key
    )
            if len(selected_projects) > 15:
                st.warning("⚠️ Please select 15 or fewer projects.")
                return

            if not selected_projects:
                st.info("👆 Please select at least one project to view data.")
                return

            # Filter data
            filtered_df = data[data['Project'].isin(selected_projects)]

            # Aggregate net cost
            net_cost_by_project = filtered_df.groupby('Project')['Net_Cost'].sum()

            # If only 1 project, pie makes no sense → use bar
            if len(net_cost_by_project) == 1:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(net_cost_by_project.index, net_cost_by_project.values)
                ax.set_title("Net Cost (OMR) by Project")
                ax.set_ylabel("Net Cost")
                st.pyplot(fig)
                return

            # Pie chart
            fig, ax = plt.subplots(figsize=(8, 8))
            wedges, texts, autotexts = ax.pie(
                net_cost_by_project, 
                labels=net_cost_by_project.index, 
                autopct='%1.1f%%', 
                startangle=90
            )

            # Improve text size & readability
            for t in texts:
                t.set_size(10)
            for t in autotexts:
                t.set_size(9)

            ax.set_title("Net Cost (OMR) by Project", fontsize=14)
            st.pyplot(fig)

if __name__ == "__main__":
    app = InfowayApp()
    app.run()