import streamlit as st
import os
import pandas as pd
from PIL import Image
import pickle
import hashlib
import matplotlib.pyplot as plt
import PyPDF2
import numpy as np
import base64
# Make sure to set wide layout first

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# -------------------------- Utility Functions --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------- USERS --------------------------
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
            # Return the saved set or an empty set
            return data.get("Dashboard_groups", set())
    return set()
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
    with open("pickle_files/responsibilities.pkl", "wb") as f:
        pickle.dump({
            "RESPONSIBILITIES": list(st.session_state.RESPONSIBILITIES)
        }, f)

def load_responsibilities():
    if os.path.exists("pickle_files/responsibilities.pkl"):
        with open("pickle_files/responsibilities.pkl", "rb") as f:
            data = pickle.load(f)
            return set(data.get("RESPONSIBILITIES", []))
    return set()

# -------------------------- Main App Class --------------------------
class InfowayApp():
    def __init__(self):
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
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
            self.initial_admin_setup()
            return
        if st.session_state.logged_in:
            role = st.session_state.role.strip().lower()
            if role == "admin":
                self.admin_dashboard()
            elif role in ["user", "salesmanager", "salesman1", "salesman2",
                        "purchasemanager", "purchaseasst1", "purchaseasst2"]:
                self.user_dashboard()
            else:
                st.warning(f"No dashboard assigned for role: {st.session_state.role}")

        else:
            self.login()

    def login(self):
        # Custom CSS for styling
        st.markdown("""
            <style>
                /* Full page background */
                .stApp {
                    background: linear-gradient(135deg, #1e3c72, #2a5298);
                    background-attachment: fixed;
                }


                /* Logo styling */
                .login-logo {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    object-fit: contain;
                    border: 2px solid white;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    margin-bottom: 20px;
                }

                /* Title styling */
                .login-title {
                    color: white;
                    font-size: 22px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }

                /* Input labels */
                label {
                    color: white !important;
                    font-weight: bold;
                }

                /* Button styling */
                div.stButton > button {
                    width: 100%;
                    background-color: #2a5298;
                    color: white;
                    height: 40px;
                    font-size: 16px;
                    border-radius: 8px;
                }
            </style>
        """, unsafe_allow_html=True)

        # Logo
        st.markdown(
            f"<img src='data:image/jpg;base64,{image_to_base64('src/logo.jpg')}' class='login-logo'>",
            unsafe_allow_html=True
        )

        # Title
        st.markdown("<div class='login-title'>Infoway Technosoft Solutions PVT LTD</div>", unsafe_allow_html=True)

        # Inputs
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # Button
        if st.button("Login"):
            if username in st.session_state.USERS:
                stored_password = st.session_state.USERS[username][0]
                if hash_password(password) == stored_password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    roles = st.session_state.USERS[username][1]
                    user_role = roles[0] if isinstance(roles, list) else roles
                    st.session_state.role = user_role
                    st.success("Login Successful")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
            else:
                st.error("Invalid Username or Password")

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
         {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;   /* no horizontal gap */
            padding-right: 0rem !important;
        }
 {
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
 {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
        }

        
        section[data-testid="stSidebar"] button {
            margin: 0.1rem 0 !important;
            padding: 0.35rem 0.5rem !important;
        }
 {
            margin: 0.1rem 0 !important;
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
        }

      {
            margin-bottom: 0.25rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
      

        st.header("Admin Panel")
        st.sidebar.markdown("---")
       # st.sidebar.markdown("### 📦 Sales Module")

        #if "sales_module_open" not in st.session_state:
         #   st.session_state.sales_module_open = False
        #if st.sidebar.button("📦 Sales Dashboard"):
         #   st.session_state.sales_module_open = not st.session_state.sales_module_open
          #  st.session_state.page = None

        #if st.session_state.sales_module_open:
         #   if st.session_state.role in ["admin", "salesmanager", "salesman1","salesman2"]:
          #      if st.sidebar.button("📊 View Sales Chart"):
           #         st.session_state.page = "sales_dashboard"
            #if st.session_state.role in ["admin", "salesmanager"]:
             #   if st.sidebar.button("📈 View Budgeting"):
              #      st.session_state.page = "budgeting"

        if "purchase_open" not in st.session_state:
            st.session_state.purchase_open = False
        if st.sidebar.button("📦 Purchase Module"):
           st.session_state.purchase_open = not st.session_state.purchase_open
           st.session_state.page = None

        if st.session_state.purchase_open:
            if st.session_state.role in ["admin", "purchasemanager", "purchaseasst1","purchaseasst2","purchase assistant"]:
                if st.sidebar.button("Purchase Dashboard"):
                    st.session_state.page="purchase_dashborad"
                if st.sidebar.button("LPO DATA"):
                    st.session_state.page = "Lpo_data"
                if st.sidebar.button("GRN DATA"):
                    st.session_state.page = "Grn_data"
                if st.sidebar.button("LPO GRN GROSS AMOUNT"):
                    st.session_state.page = "lpo_grn_gross_amount"
                if st.sidebar.button("LPO GRN NET VALUES"):
                    st.session_state.page = "lpo_grn_net_values"

        if "admin_menu_open" not in st.session_state:
            st.session_state.admin_menu_open = False
        if st.sidebar.button("Admin Portal"):
            st.text("Infoway Techno Soft Solutions")
            st.session_state.admin_menu_open = not st.session_state.admin_menu_open
            st.session_state.page = None

        if st.session_state.admin_menu_open:
            with st.sidebar:
                st.markdown("**Admin Options:**")
                if st.button("📊 DashBoard Group"):
                    st.session_state.page= "dashboard_groups"
                if st.button("🏠 DashBoard"):
                    st.session_state.page = "admin_dashboard"
                if st.button("👥 Roles"):
                    st.session_state.page = "roles"
                if st.button("🧩 Responsibilities"):
                    st.session_state.page = "responsibilities"
                if st.button("🙋 Users"):
                    st.session_state.page = "users"  

        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            self.logout() 
        if st.session_state.get("page") == "dashboard_groups":
            st.subheader("Dashboard Groups") 
            self.dashboardgroups()
        elif st.session_state.get("page") == "admin_dashboard":
            st.subheader("🏠 Admin Dashboard")
            self.dashboard()
        elif st.session_state.get("page") == "roles":
            self.manage_roles()
        elif st.session_state.get("page") == "responsibilities":
            self.manage_responsibilities()
        elif st.session_state.get("page") == "users":
            self.manage_users()
       # elif st.session_state.get("page") == "sales_dashboard":
        #    st.subheader("📊 Sales Dashboard")
         #   self.show_sales_chart()
        #elif st.session_state.get("page") == "budgeting":
         #   st.subheader("📈 Budgeting Section")
          #  self.show_budgeting_section()
        elif st.session_state.get("page") == "purchase_dashborad":
            st.subheader("Purchase Dashboard")
            self.purchase_dashboard()
        elif st.session_state.get("page") == "Lpo_data":
            st.subheader("LPO DATA")
            self.purchase()
        elif st.session_state.get("page")=="Grn_data":
            st.subheader("GRN DATA")
            self.GRN()
        elif st.session_state.get("page") == "lpo_grn_gross_amount":
            st.subheader("LPO GRN GROSS AMOUNT")
            self.lpo_grn_gross_amount()
        elif st.session_state.get("page") == "lpo_grn_net_values":
            st.subheader("LPO GRN NET VALUES")
            self.lpo_grn_net_values()
    
    def dashboardgroups(self):
        new_grp = st.text_input("Group Name")
        Desc = st.text_input("Description")

        if st.button("Add Group Name"):
            if not new_grp:
                st.warning("Group name cannot be empty.")
            elif new_grp in st.session_state.Dashboard_groups:
                st.warning("Duplicate group name.")
            else:
                # Add new group
                st.session_state.Dashboard_groups.add(new_grp)
                save_dashboard_groups()  # save updated groups to pickle
                st.success(f"Dashboard group '{new_grp}' added.")
                st.rerun()

# Dashboard function
    def dashboard(self):
        st.subheader("Dashboards")

        # Ensure dashboards exists and is a dict
        if "dashboards" not in st.session_state or not isinstance(st.session_state.dashboards, dict):
            st.session_state.dashboards = {}

        # Prepare dashboard groups list
        dashboard_groups = st.session_state.get("Dashboard_groups")
        if not dashboard_groups:
            dashboard_groups_list = []
        elif isinstance(dashboard_groups, dict):
            dashboard_groups_list = list(dashboard_groups.keys())
        elif isinstance(dashboard_groups, set):
            dashboard_groups_list = list(dashboard_groups)
        else:
            dashboard_groups_list = []

        selected_db_grp = st.multiselect("Dashboard Group", dashboard_groups_list)
        dashboard_name = st.text_input("Dashboard Name")

        # Auto-generate Dashboard ID as 4-digit string starting from 0001
        if st.session_state.dashboards:
            max_id = max([int(details["id"]) for details in st.session_state.dashboards.values()])
            dashboard_id = f"{max_id + 1:04d}"
        else:
            dashboard_id = "0001"

        st.write(f"Dashboard ID: {dashboard_id}")

        # Add dashboard button
        if st.button("Add Dashboard"):
            if not dashboard_name or not selected_db_grp:
                st.warning("Please provide a dashboard name and select at least one group.")
            elif dashboard_name in st.session_state.dashboards:
                st.warning("Dashboard name already exists.")
            else:
                st.session_state.dashboards[dashboard_name] = {
                    "id": dashboard_id,
                    "groups": selected_db_grp
                }
                save_dashboards()  # Save to pickle
                st.success(f"Dashboard '{dashboard_name}' added with ID {dashboard_id}.")
                st.rerun()
    def manage_roles(self):
        st.header("Manage Roles")

        if not st.session_state.Dashboard_groups:
            st.warning("No Dashboard groups defined yet. Add some first.")
        else:
            new_role = st.text_input("Enter New Role")
            selected_groups = st.multiselect(
                "Dashboard Groups", 
                list(st.session_state.Dashboard_groups)
            )

            selected_dashboards = []

            # Show dashboards in selected groups with checkboxes
            if selected_groups and "dashboards" in st.session_state:
                st.markdown("**Select Dashboards for this Role:**")
                for name, details in st.session_state.dashboards.items():
                    if any(group in details["groups"] for group in selected_groups):
                        checkbox_key = f"select_{name}"
                        if st.checkbox(f"{details['id']} - {name} ({', '.join(details['groups'])})", key=checkbox_key):
                            selected_dashboards.append(name)

                if not selected_dashboards:
                    st.info("No dashboards selected yet.")

            if st.button("Add Role"):
                if new_role and selected_groups:
                    if new_role not in st.session_state.ROLES_MAP:
                        st.session_state.ROLES_MAP[new_role] = {
                            "groups": selected_groups,
                            "dashboards": selected_dashboards
                        }
                        save_roles()
                        st.success(f"Role '{new_role}' created with {len(selected_dashboards)} dashboards.")
                        st.rerun()
                    else:
                        st.warning("Role already exists.")
                else:
                    st.warning("Enter a role, select dashboard groups, and choose dashboards.")

        st.markdown("---")
        st.subheader("Existing Roles")

        if st.session_state.ROLES_MAP:
            roles_data = []
            for role, data in sorted(st.session_state.ROLES_MAP.items()):
                if isinstance(data, dict):  # New format
                    groups = data.get("groups", [])
                    dashboards = data.get("dashboards", [])
                else:  # Old format (list of groups only)
                    groups = data
                    dashboards = []
                
                roles_data.append({
                    "Role": role,
                    "Dashboard Groups": ", ".join(groups),
                    "Dashboards": ", ".join(dashboards) if dashboards else ""
                })

            st.dataframe(pd.DataFrame(roles_data), use_container_width=True)
        else:
            st.info("No roles defined yet.")




    def manage_responsibilities(self):
        st.header("Manage Responsibilities")

        # Ensure RESP is a dict
        if "RESPONSIBILITIES" not in st.session_state or not isinstance(st.session_state.RESPONSIBILITIES, dict):
            st.session_state.RESPONSIBILITIES = {}

        # Input for new responsibility
        new_resp = st.text_input("Enter New Responsibility")
        selected_roles = st.multiselect("Roles", list(st.session_state.ROLES_MAP))

        if st.button("Add Responsibility"):
            if new_resp and selected_roles:
                if new_resp not in st.session_state.RESPONSIBILITIES:
                    st.session_state.RESPONSIBILITIES[new_resp] = selected_roles
                    save_responsibilities()
                    st.success(f"Responsibility '{new_resp}' added for roles: {', '.join(selected_roles)}")
                    st.rerun()
                else:
                    st.warning("Responsibility already exists.")
            else:
                st.warning("Please enter a responsibility and select at least one role.")

        st.markdown("---")
        st.subheader("Existing Responsibilities")

        if st.session_state.RESPONSIBILITIES:
            respons = [
                {"Responsibilities": resp, "Roles": ", ".join(roles)}
                for resp, roles in sorted(st.session_state.RESPONSIBILITIES.items())
            ]
            df_resps = pd.DataFrame(respons)
            st.dataframe(df_resps, use_container_width=True)
        else:
            st.info("No responsibilities yet.")

    
  

    def manage_users(self):
        st.header("User Access")

        # Create User Button
        if st.button("Add New User"):
            st.session_state.show_create_user_form = True
            st.session_state._editing_user = None

        if st.session_state.get("show_create_user_form", False):
            self.createuser()

        st.subheader("Registered Users")

        if not st.session_state.USERS:
            st.info("No registered users found.")
            return

        # Table header
        cols = st.columns([2, 3, 3])
        cols[0].write("**Username**")
        cols[1].write("**Responsibilities**")
        cols[2].write("**Email**")

        # Display users as "hyperlinks"
        for username, details in st.session_state.USERS.items():
            resp_data = details[1]  # responsibilities
            responsibilities = ", ".join(resp_data) if isinstance(resp_data, list) else resp_data
            email = details[2]

            cols = st.columns([2, 3, 3])

            # Button styled as hyperlink
            if cols[0].button(f"➡️ {username}", key=f"user_{username}"):
                st.session_state._editing_user = username
                st.session_state.show_create_user_form = True
                st.rerun()

            cols[1].write(responsibilities)
            cols[2].write(email)



    def createuser(self):
        is_edit_mode = st.session_state.get("_editing_user") is not None
        user_to_edit = st.session_state.get("_editing_user")
        st.title("Edit User" if is_edit_mode else "Create New User")

        if is_edit_mode:
            user_data = st.session_state.USERS[user_to_edit]
            default_email = user_data[2]
            saved_responsibilities = user_data[1]  # now stores responsibilities
        else:
            default_email = ""
            saved_responsibilities = []

        # Get available responsibilities

        available_responsibilities = list(st.session_state.setdefault("RESPONSIBILITIES", {}))
        valid_saved_responsibilities = [r for r in saved_responsibilities if r in available_responsibilities]

        with st.form("create_user_form"):
            username = st.text_input("Username", value=user_to_edit if is_edit_mode else "")
            email = st.text_input("Email", value=default_email)
            password = st.text_input("Password (leave blank to keep same)", type="password")

            # Change: Responsibilities instead of Roles
            responsibilities = st.multiselect(
                "Select Responsibilities",
                available_responsibilities,
                default=valid_saved_responsibilities,
                key="add_user_responsibilities"
            )

            submitted = st.form_submit_button("Update User" if is_edit_mode else "Create User")

        if submitted:
            if not username or not email:
                st.error("Please fill all required fields")
                return

            if is_edit_mode:
                if username != user_to_edit and username in st.session_state.USERS:
                    st.warning("New username already exists")
                    return
                hashed_pw = hash_password(password) if password else st.session_state.USERS[user_to_edit][0]
                if username != user_to_edit:
                    del st.session_state.USERS[user_to_edit]
                # Save responsibilities instead of roles
                st.session_state.USERS[username] = [hashed_pw, responsibilities, email]
                st.success("User updated successfully")
            else:
                if username in st.session_state.USERS:
                    st.warning("Username already exists")
                else:
                    hashed_pw = hash_password(password)
                    st.session_state.USERS[username] = [hashed_pw, responsibilities, email]
                    st.success("User created successfully")

            save_users(st.session_state.USERS)
            st.session_state.show_create_user_form = False
            st.session_state._editing_user = None
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
           # if "View Sales Chart" in responsibilities:
            #    st.subheader("Sales Dashboard")
             #   self.show_sales_chart()
            #if "Budgeting Access" in responsibilities:
             #   st.subheader("Budgeting Section")
              #  self.show_budgeting_section()
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

    #def show_sales_chart(self):
        #st.subheader("Sales Data Charts")
        #if not os.path.exists("data/sales_data.csv"):
         #   st.error("Your file does not exist")
          #  return
        #df = pd.read_csv("data/sales_data.csv")
        #st.dataframe(df)
        #st.bar_chart(data=df, x="City", y="Total")
        #data = {'Name': ['Omkar', 'Lakshman', 'Ajay'], 'Sales': [24, 25, 23], 'Location': ['Nellore', 'Chennai', 'Hyderabad']}
        #df_chart = pd.DataFrame(data)
        #st.title("Sales")
        #fig, ax = plt.subplots()
        #ax.bar(df_chart["Name"], df_chart["Sales"], color="blue")
        #ax.set_title("Sales by Person")
        #ax.set_xlabel("Name")
        #ax.set_ylabel("Sales")
        #st.pyplot(fig)

    #def show_budgeting_section(self):
     #   st.write("📋 This is the budgeting area.")
      #  budget_data = {"Department": ["Sales", "Marketing", "HR"], "Budget": [150000, 100000, 80000]}
       # df_budget = pd.DataFrame(budget_data)
        #st.dataframe(df_budget)
        #st.bar_chart(df_budget.set_index("Department"))
    def purchase_dashboard(self):
        st.title("Dashboards of Purchase module")
        self.purchase()
        self.GRN()
        self.lpo_grn_gross_amount()
        self.lpo_grn_net_values()
        
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

    def purchase(self):
        st.title("📊 Purchase Dashboard")

        df = self.load_purchase_data()

        # Create a proper Date column from Year + Month
        df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")

        # Sidebar filters
        projects = st.multiselect(
            "Select Projects",
            options=sorted(df["Project"].unique()),
            default=sorted(df["Project"].unique())
        )

        view_mode = st.radio(
            "View Mode",
            options=["Yearly", "Monthly"],
            index=0,
            horizontal=True,key="radio"
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
            default=sorted(df["Project"].unique())
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
        selected_projects = st.multiselect("Select Projects (max 15)", projects, default=projects[:10])

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

        # Add Net_Cost column before filtering
        data['Net_Cost'] = data['PO_Net Value'] + data['GRN_Net Value']

        projects = data['Project'].unique().tolist()
        selected_projects = st.multiselect("Select Projects (max 15)", projects, default=projects[:10],key="lpo_grn_projects")

        if len(selected_projects) > 15:
            st.warning("Please select 15 or fewer projects.")
            st.stop()

        if not selected_projects:
            st.info("Please select at least one project.")
            st.stop()

        filtered_df = data[data['Project'].isin(selected_projects)].reset_index(drop=True)

        net_cost_by_project = filtered_df.groupby('Project')['Net_Cost'].sum()

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(net_cost_by_project, labels=net_cost_by_project.index, autopct='%1.1f%%')
        ax.set_title('Net Cost (OMR) by Project')

        st.pyplot(fig)


if __name__ == "__main__":
    app = InfowayApp()
    app.run()