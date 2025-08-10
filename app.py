import streamlit as st
import os
import pandas as pd
from PIL import Image
import pickle
import hashlib
import matplotlib.pyplot as py
import PyPDF2

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

    def run(self):
        if not st.session_state.USERS:
            self.initial_admin_setup()
            return
        if st.session_state.logged_in:
            role = st.session_state.role
            if role == "admin":
                self.admin_dashboard()
            elif role in ["user", "salesmanager", "salesman1", "salesman2", "purchasemanager", "purchaseasst1", "purchaseasst2"]:
                self.user_dashboard()
            else:
                st.warning(f"No dashboard assigned for role: {role}")
        else:
            self.login()

    def login(self):
        img = Image.open('src/logo.jpg')
        st.image(img, width=250)
        st.markdown("<h1 style='color: white; font-size: 35px; text-align: center;'>Infoway Technosoft Solutions PVT LTD</h1>", unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
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
    
    def admin_dashboard(self):
        st.sidebar.markdown(
            "<marquee behaviour='scroll' direction='left' scrollamount='5' style='color: white; font-size:20px; font-style: italic;'>Welcome to the Infoway Dashboard!</marquee>",
            unsafe_allow_html=True,
        )

        st.header("Admin Panel")
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📦 Sales Module")

        if "sales_module_open" not in st.session_state:
            st.session_state.sales_module_open = False
        if st.sidebar.button("📦 Sales Dashboard"):
            st.session_state.sales_module_open = not st.session_state.sales_module_open
            st.session_state.page = None

        if st.session_state.sales_module_open:
            if st.session_state.role in ["admin", "salesmanager", "salesman1","salesman2"]:
                if st.sidebar.button("📊 View Sales Chart"):
                    st.session_state.page = "sales_dashboard"
            if st.session_state.role in ["admin", "salesmanager"]:
                if st.sidebar.button("📈 View Budgeting"):
                    st.session_state.page = "budgeting"

        st.sidebar.markdown("### 🛒 Purchase Module")
        if "purchase_open" not in st.session_state:
            st.session_state.purchase_open = False
        if st.sidebar.button("📦 Purchase Dashboard"):
            st.session_state.purchase_open = not st.session_state.purchase_open
            st.session_state.page = None

        if st.session_state.purchase_open:
            if st.session_state.role in ["admin", "purchasemanager", "purchaseasst1","purchaseasst2"]:
                if st.sidebar.button("LPO DATA"):
                    st.session_state.page = "purchase_dashboard"
                if st.sidebar.button("GRN DATA"):
                    st.session_state.page = "Grn_data"
                if st.sidebar.button("LPO GRN GROSS AMOUNT"):
                    st.session_state.page = "lpo_grn_gross_amount"
                if st.sidebar.button("LPO GRN NET VALUES"):
                    st.session_state.page = "lpo_grn_net_values"

        if "admin_menu_open" not in st.session_state:
            st.session_state.admin_menu_open = False
        st.sidebar.markdown("Admin Portal")
        if st.sidebar.button("Admin Portal"):
            st.text("Infoway Techno Soft Solutions")
            st.session_state.admin_menu_open = not st.session_state.admin_menu_open
            st.session_state.page = None

        if st.session_state.admin_menu_open:
            with st.sidebar:
                st.markdown("**Admin Options:**")
                if st.button("🏠 DashBoard"):
                    st.session_state.page = "admin_dashboard"
                if st.button("🧩 Responsibilities"):
                    st.session_state.page = "responsibilities"
                if st.button("👥 Roles"):
                    st.session_state.page = "roles"
                if st.button("🙋 Users"):
                    st.session_state.page = "users"  

        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            self.logout() 

        if st.session_state.get("page") == "admin_dashboard":
            st.subheader("🏠 Admin Dashboard")
            st.write("Welcome to the Admin Dashboard.")
        elif st.session_state.get("page") == "responsibilities":
            self.manage_responsibilities()
        elif st.session_state.get("page") == "roles":
            self.manage_roles()
        elif st.session_state.get("page") == "users":
            self.manage_users()
        elif st.session_state.get("page") == "sales_dashboard":
            st.subheader("📊 Sales Dashboard")
            self.show_sales_chart()
        elif st.session_state.get("page") == "budgeting":
            st.subheader("📈 Budgeting Section")
            self.show_budgeting_section()
        elif st.session_state.get("page") == "purchase_dashboard":
            st.subheader("Purchase Dashboard")
            self.purchase()
        elif st.session_state.get("page") == "purchase_summary":
            st.subheader("Purchase Summary")
            self.view_summary()
        elif st.session_state.get("page")=="Grn_data":
            st.subheader("GRN DATA")
        elif st.session_state.get("page") == "lpo_grn_gross_amount":
            st.subheader("LPO GRN GROSS AMOUNT")
        elif st.session_state.get("page") == "lpo_grn_net_values":
            st.subheader("LPO GRN NET VALUES")

    def manage_responsibilities(self):
        st.header("Manage Responsibilities")
        new_resp = st.text_input("Enter New Responsibility")
        if st.button("Add Responsibility"):
            if new_resp and new_resp not in st.session_state.RESPONSIBILITIES:
                st.session_state.RESPONSIBILITIES.add(new_resp)
                save_responsibilities()
                st.success(f"Responsibility '{new_resp}' added.")
                st.rerun()
            else:
                st.warning("Invalid or Duplicate Responsibility")

        st.markdown("---")
        st.subheader("Existing Responsibilities")
        if st.session_state.RESPONSIBILITIES:
            for resp in sorted(st.session_state.RESPONSIBILITIES):
                st.markdown(f"| {resp} |")
        else:
            st.info("No responsibilities yet.")

    def manage_roles(self):
        st.header("Manage Roles")
        if not st.session_state.RESPONSIBILITIES:
            st.warning("No responsibilities defined yet. Add some first.")
        else:
            new_role = st.text_input("Enter New Role")
            selected_responsibilities = st.multiselect("Assign Responsibilities", list(st.session_state.RESPONSIBILITIES))
            if st.button("Add Role"):
                if new_role and selected_responsibilities:
                    if new_role not in st.session_state.ROLES_MAP:
                        st.session_state.ROLES_MAP[new_role] = selected_responsibilities
                        save_roles()
                        st.success(f"Role '{new_role}' created.")
                        st.rerun()
                    else:
                        st.warning("Role already exists.")
                else:
                    st.warning("Enter a role and select responsibilities")

        st.markdown("---")
        st.subheader("Existing Roles")
        if st.session_state.ROLES_MAP:
            for role, responsibilities in sorted(st.session_state.ROLES_MAP.items()):
                with st.expander(f"Role: {role}"):
                    for r in responsibilities:
                        st.markdown(f"- {r}")
        else:
            st.info("No roles defined yet.")

    def manage_users(self):
        st.header("User Access")
        if st.button("Create New User"):
            st.session_state.show_create_user_form = True
            st.session_state._editing_user = None
        if st.session_state.show_create_user_form:
            self.createuser()
        st.subheader("Registered Users")
        for name, details in st.session_state.USERS.items():
            [role] = details[1] if isinstance(details[1], list) else [details[1]]
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{name}** | Role: {role} | Email: {details[2]}")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{name}"):
                    st.session_state._editing_user = name
                    st.session_state.show_create_user_form = True
                    st.rerun()

    def createuser(self):
        is_edit_mode = st.session_state.get("_editing_user") is not None
        user_to_edit = st.session_state.get("_editing_user")
        st.title("Edit User" if is_edit_mode else "Create New User")

        if is_edit_mode:
            user_data = st.session_state.USERS[user_to_edit]
            default_email = user_data[2]
            saved_roles = user_data[1]
        else:
            default_email = ""
            saved_roles = []

        available_roles = list(st.session_state.ROLES_MAP.keys())
        valid_saved_roles = [r for r in saved_roles if r in available_roles]

        with st.form("create_user_form"):
            username = st.text_input("Username", value=user_to_edit if is_edit_mode else "")
            email = st.text_input("Email", value=default_email)
            password = st.text_input("Password (leave blank to keep same)", type="password")
            roles = st.multiselect("Select Roles", available_roles, default=valid_saved_roles, key="add_user_roles")
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
                st.session_state.USERS[username] = [hashed_pw, roles, email]
                st.success("User updated successfully")
            else:
                if username in st.session_state.USERS:
                    st.warning("Username already exists")
                else:
                    hashed_pw = hash_password(password)
                    st.session_state.USERS[username] = [hashed_pw, roles, email]
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
        fig, ax = py.subplots()
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

    def purchase(self):
        st.write("Purchase dashboard")
        if not os.path.exists("data/lpo_data.csv"):
            st.error("Csv file not found")
            return
        df = pd.read_csv("data/lpo_data.csv")
        st.dataframe(df)
    def GRN(self):
        if not os.path.exists("data/grn_data.csv"):
            st.error("csv file not exist")
            return
        df=pd.read_csv("data/grn_data.csv")    
    def view_summary(self):
        st.write("Purchase Summary")
        if not os.path.exists("data/view_summary.csv"):
            st.error("Csv file not found")
            return
        df = pd.read_csv("data/view_summary.csv")  
        st.dataframe(df)
        st.bar_chart(df.set_index("Date")["Amount"])

if __name__ == "__main__":
    app = InfowayApp()
    app.run()
