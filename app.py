import streamlit as st
from src.utils.login import LoginPage,hash_password
import src.utils.css as css
from src.utils.user_utils import load_users, save_users
from src.utils.role_utils import load_roles, save_roles
from src.utils.responsibility_utils import load_responsibilities, save_responsibilities
from src.utils.dashboard_utils import load_dashboard_groups, save_dashboard_groups,load_dashboards, save_dashboards
import src.utils.dashboard as dashboards 
import io
import pandas as pd
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
        if 'users' not in st.session_state:
            st.session_state.users = load_users()
        if 'responsibilities' not in st.session_state:
            st.session_state.responsibilities = load_responsibilities()
        if 'roles_map' not in st.session_state:
            st.session_state.roles_map = load_roles()
        if 'dashboard_groups' not in st.session_state:
            st.session_state.dashboard_groups=load_dashboard_groups()
        if 'dashboards' not in st.session_state:
            st.session_state.dashboards=load_dashboards()
        if not st.session_state.get("logged_in", False):
                st.set_page_config(page_title="Infoway Login", layout="centered")
        else:
            st.set_page_config(page_title="Infoway Dashboard", layout="wide")
    def run(self):
        if not st.session_state.users:
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
            login_page = LoginPage()
            login_page.login()

    def admin_dashboard(self):
        st.sidebar.markdown(
            "<marquee behaviour='scroll' direction='left' scrollamount='5' style='color: blue; font-size:20px; font-style: italic;'>Welcome to the Infoway Dashboard!</marquee>",
            unsafe_allow_html=True,
        )
       
        css.load_main_css("css/main.css")
        css.hyper_link("css/hyperlink.css")
        st.header("Admin Portal")
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
                dashboards.show_sales_chart()
            with sales_tabs[1]:
                dashboards.show_budgeting_section()
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
                    dashboards.lpo_data()

                # Tab 2: GRN DATA only
                with purchase_tabs[2]:
                    st.subheader("GRN DATA")
                    dashboards.GRN()

                # Tab 3: LPO GRN Gross Amount only
                with purchase_tabs[3]:
                    st.subheader("LPO GRN Gross Amount")
                    dashboards.lpo_grn_gross_amount()

                # Tab 4: LPO GRN Net Values only
                with purchase_tabs[4]:
                    st.subheader("LPO GRN Net Values")
                    dashboards.lpo_grn_net_values()

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
        st.subheader("📊 Manage Dashboard Groups")
        css.hyper_link("css/hyperlink.css")
        css.load_main_css("css/main.css")

        # ------------------ Initialize session state ------------------
        if "dashboard_groups" not in st.session_state:
            st.session_state.dashboard_groups = load_dashboard_groups()
        if "add_group_page" not in st.session_state:
            st.session_state.add_group_page = False
        if "edit_group" not in st.session_state:
            st.session_state.edit_group = None

        # Convert set to dict if needed
        if isinstance(st.session_state.dashboard_groups, set):
            st.session_state.dashboard_groups = {g: {"Description": "", "id": ""} 
                                                for g in st.session_state.dashboard_groups}
            save_dashboard_groups(st.session_state.dashboard_groups)

        # ------------------ MAIN LIST PAGE ------------------
        if not st.session_state.add_group_page and st.session_state.edit_group is None:

            # Add Dashboard Group button
            if st.button("➕ Add Dashboard Group", key="go_add_group"):
                st.session_state.add_group_page = True
                st.rerun()

            if st.session_state.dashboard_groups:
                # Scrollable container
                st.markdown('<div class="scrollable-div">', unsafe_allow_html=True)

                # Header row
                st.markdown('<div class="table-row" style="display:flex;">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 1, 2])
                col1.markdown("**GROUPS**")
                col2.markdown("**Dashboard ID**")
                col3.markdown("**DESCRIPTION**")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                # Data rows
                for g, d in st.session_state.dashboard_groups.items():
                    st.markdown('<div class="table-row" style="display:flex;">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button(g, key=f"edit_{g}", help="Click to edit"):
                            st.session_state.edit_group = g
                            st.rerun()
                    col2.write(d.get("id", ""))
                    col3.write(d.get("Description", ""))
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.info("No dashboard groups added yet.")

        # ------------------ ADD GROUP PAGE ------------------
        if st.session_state.add_group_page:
            st.subheader("🆕 Add Dashboard Group")
            group_name = st.text_input("Group Name", key="new_grp_name")
            group_desc = st.text_input("Description", key="new_grp_desc")

            # Generate Dashboard ID
            if st.session_state.dashboard_groups:
                max_id = max([int(details.get("id", 0) or 0) 
                            for details in st.session_state.dashboard_groups.values()])
                dashboard_id = f"{max_id + 1:04d}"
            else:
                dashboard_id = "0001"

            st.write(f"Dashboard ID: {dashboard_id}")

            if st.button("Save", key="add_group_btn"):
                if not group_name:
                    st.warning("Group name cannot be empty.")
                elif group_name in st.session_state.dashboard_groups:
                    st.warning("Duplicate group name.")
                else:
                    st.session_state.dashboard_groups[group_name] = {
                        "id": dashboard_id,
                        "Description": group_desc
                    }
                    save_dashboard_groups(st.session_state.dashboard_groups)
                    st.success(f"✅ Group '{group_name}' added successfully!")
                    st.session_state.add_group_page = False
                    st.rerun()

            if st.button("⬅️ Back", key="cancel_add_group"):
                st.session_state.add_group_page = False
                st.rerun()

        # ------------------ EDIT GROUP PAGE ------------------
        if st.session_state.edit_group is not None:
            g = st.session_state.edit_group
            st.subheader(f"✏️ Edit Group: {g}")
            group_desc_safe = st.session_state.dashboard_groups.get(g, {}).get("Description", "")

            new_name = st.text_input("Edit Group Name", value=g, key="edit_name_input")
            new_desc = st.text_input("Edit Description", value=group_desc_safe, key="edit_desc_input")

            if st.button("Update", key="update_group_btn"):
                if not new_name:
                    st.warning("Group name cannot be empty.")
                else:
                    if new_name != g:
                        st.session_state.dashboard_groups.pop(g)
                    st.session_state.dashboard_groups[new_name] = {
                        "Description": new_desc,
                        "id": st.session_state.dashboard_groups.get(g, {}).get("id", "")
                    }
                    save_dashboard_groups(st.session_state.dashboard_groups)
                    st.success(f"✅ Group '{new_name}' updated successfully!")
                    st.session_state.edit_group = None
                    st.rerun()

            if st.button("⬅️ Back", key="cancel_edit_group"):
                st.session_state.edit_group = None
                st.rerun()


    def dashboard(self):
        st.subheader("🏠 Manage Dashboards")
        css.hyper_link("css/hyperlink.css")
        # --- Prepare dashboard groups list ---
        dashboard_groups = st.session_state.get("dashboard_groups", {})
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
            if st.button("➕ Add Dashboard", key="new_dashboard_btn"):
                st.session_state.add_dashboard_page = True
                st.rerun()

            st.subheader("Dashboards")
            if st.session_state.dashboards:
                cols = st.columns([2, 2, 4])
                cols[0].markdown("**Dashboard Name**")
                cols[1].markdown("**Dashboard ID**")
                cols[2].markdown("**Groups**")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                for d_name, details in st.session_state.dashboards.items():
                    row_cols = st.columns([2, 2, 4])
                    with row_cols[0]:
                        # Use a unique key for each dashboard button
                        if st.button(d_name, key=f"dashboard_btn_{d_name}",help="Click to edit"):
                            st.session_state.edit_dashboard = d_name
                            st.rerun()
                    with row_cols[1]:
                        st.write(details["id"])
                    with row_cols[2]:
                        st.write(", ".join(details["groups"]))
                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
            else:
                st.info("No dashboards added yet.")
            #if st.session_state.dashboards:
             #           data = []
              #          for role, details in st.session_state.dashboards.items():
               #                              data.append({
                #                           "Dashboard ID": details.get("id", ""),
                 #
                #                          "Groups": ", ".join(details.get("groups", []))})

                       # users_df = pd.DataFrame(data)

                        # Create CSV in memory
                        #csv_buffer = io.StringIO()
                        #users_df.to_csv(csv_buffer, index=False)
                        #csv_bytes = csv_buffer.getvalue().encode("utf-8")

                        #st.download_button(
                         #   label="⬇️",
                          #  data=csv_bytes,
                           # file_name="dashboards.csv",
                            #mime="text/csv",
                            #help="Download all responsibilities")
                        

        # --- ADD DASHBOARD PAGE ---
        if st.session_state.add_dashboard_page:
            st.subheader("🆕 Add Dashboard")
            new_name = st.text_input("Dashboard Name", key="new_db_name")
            selected_groups = st.multiselect("Dashboard Group", options=dashboard_groups_list, key="new_db_groups")

            # Auto-generate Dashboard ID
            if st.session_state.dashboards:
                max_id = max([int(details["id"]) for details in st.session_state.dashboards.values()])
                dashboard_id = f"{max_id + 1:04d}"
            else:
                dashboard_id = "0001"
            st.write(f"Dashboard ID: {dashboard_id}")

            if st.button("Add Dashboard", key="add_dashboard_btn"):
                if not new_name or not selected_groups:
                    st.warning("Please provide a dashboard name and select at least one group.")
                elif new_name in st.session_state.dashboards:
                    st.warning("Dashboard name already exists.")
                else:
                    st.session_state.dashboards[new_name] = {
                        "id": dashboard_id,
                        "groups": selected_groups
                    }
                    save_dashboards(st.session_state.dashboards)  # ✅ Pass the dashboards
                    st.success(f"✅ Dashboard '{new_name}' added successfully!")
                    st.session_state.add_dashboard_page = False
                    st.rerun()

            if st.button("⬅️ Back", key="cancel_add_dashboard"):
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

            if st.button("Update", key="update_dashboard_btn"):
                if not new_name or not selected_groups:
                    st.warning("Please provide a name and select at least one group.")
                else:
                    if new_name != d_name:
                        st.session_state.dashboards.pop(d_name)
                    st.session_state.dashboards[new_name] = {
                        "id": dashboard_id,
                        "groups": selected_groups
                    }
                    save_dashboards(st.session_state.dashboards)  # ✅ Pass the dashboards
                    st.success(f"✅ Dashboard '{new_name}' updated successfully!")
                    st.session_state.edit_dashboard = None
                    st.rerun()

            if st.button("⬅️ Back", key="cancel_edit_dashboard"):
                st.session_state.edit_dashboard = None
                st.rerun()


    def manage_roles(self):
        st.header("👥 Manage Roles")
        css.hyper_link("css/hyperlink.css")

        # --- Initialize session state ---
        if "roles_map" not in st.session_state:
            st.session_state.roles_map = load_roles()
        if "add_role_page" not in st.session_state:
            st.session_state.add_role_page = False
        if "edit_role" not in st.session_state:
            st.session_state.edit_role = None
        if "dashboard_groups" not in st.session_state:
            st.session_state.dashboard_groups = set()
        if "dashboards" not in st.session_state:
            st.session_state.dashboards = {}
        if "resp_page" not in st.session_state:
            st.session_state.resp_page = 0

        page_size=1
        r_l=list(st.session_state.roles_map.items())
        t_p=(len(r_l)-1)//page_size+1 if r_l else 1
        s_i=st.session_state.resp_page* page_size
        end_idx=s_i+page_size
        page_items=r_l[s_i:end_idx]


        # --- Combined options for groups ---
        column_names = []
        combined_options = sorted(set(st.session_state.dashboard_groups).union(column_names))
        # --- MAIN LIST PAGE ---
        # --- MAIN LIST PAGE ---
        if not st.session_state.add_role_page and st.session_state.edit_role is None:
            if st.button("➕ Add Role", key="new_role_btn"):
                st.session_state.add_role_page = True
                st.rerun()

            st.subheader("Roles")
            if st.session_state.roles_map:
                cols = st.columns([3, 4, 5])
                cols[0].markdown("**Role Name**")
                cols[1].markdown("**Groups**")
                cols[2].markdown("Role ID")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                for role, data in page_items: 
                    row_cols = st.columns([3, 4, 5])
                    with row_cols[0]:
                        if st.button(role, key=f"role_btn_{role}", help="Click to edit"):
                            st.session_state.edit_role = role
                            st.rerun()
                    with row_cols[1]:
                        st.write(", ".join(data.get("groups", [])))
                    with row_cols[2]:
                        # Safe access for role ID
                        st.write(data.get("id"))
                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                p1, p2, p3 = st.columns([1, 2, 1])
                with p1:
                    if st.button("⬅️ Prev", key="roles_prev") and st.session_state.resp_page > 0:
                        st.session_state.resp_page -= 1
                        st.rerun()
                with p3:
                    if st.button("Next ➡️", key="roles_next") and st.session_state.resp_page < t_p - 1:
                        st.session_state.resp_page += 1
                        st.rerun()
                with p2:
                    st.markdown(f"Page {st.session_state.resp_page + 1} of {t_p}")

            else:
               st.info("No roles defined yet.")

        # --- ADD ROLE PAGE ---
        if st.session_state.add_role_page:
            st.subheader("🆕 Add Role")
            new_role = st.text_input("Enter New Role", key="new_role").strip()
            selected_groups = st.multiselect("Dashboard Groups", options=combined_options, key="new_role_groups")

            selected_dashboards = []
            if selected_groups:
                st.markdown("**Select Dashboards for this Role:**")
                for name, details in st.session_state.dashboards.items():
                    if any(group in details["groups"] for group in selected_groups):
                        if st.checkbox(
                            f"{details['id']} - {name} ({', '.join(details['groups'])})",
                            key=f"add_chk_{name}"
                        ):
                            selected_dashboards.append(name)

            # Assign a new role ID safely
            if st.session_state.roles_map:
                max_id = max([int(details.get("id", "0")) for details in st.session_state.roles_map.values()])
                role_id = f"{max_id + 1:04d}"
            else:
                role_id = "0001"

            st.write(f"Role ID: {role_id}")

            if st.button("Add Role", key="add_role_btn"):
                if not new_role or not selected_groups:
                    st.warning("Please enter a role name and select at least one group.")
                elif new_role in st.session_state.roles_map:
                    st.warning("Role already exists.")
                else:
                    st.session_state.roles_map[new_role] = {
                        "id": role_id,
                        "groups": selected_groups,
                        "dashboards": selected_dashboards
                    }
                    save_roles(st.session_state.roles_map)
                    st.success(f"✅ Role '{new_role}' created successfully!")
                    st.session_state.add_role_page = False
                    st.rerun()  

            if st.button("⬅️ Back", key="cancel_add_role"):
                st.session_state.add_role_page = False
                st.rerun()
        

           # if st.session_state.roles_map:
            #        data = []
             #       for role, details in st.session_state.roles_map.items():
              #                          data.append({
               #                             "Role": role,
                #                            "Groups": ", ".join(details.get("groups", [])),
                 #                           "Dashboards": ", ".join(details.get("dashboards", []))
                  #                      })


                   # users_df = pd.DataFrame(data)

                    # Create CSV in memory
                    #csv_buffer = io.StringIO()
                    #users_df.to_csv(csv_buffer, index=False)
                    #csv_bytes = csv_buffer.getvalue().encode("utf-8")

                    #st.download_button(
                     #   label="⬇️",
                      #  data=csv_bytes,
                       
                       # file_name="roles.csv",
                        #mime="text/csv",
                        #help="Download all responsibilities")
                    


        # --- EDIT ROLE PAGE ---
        if st.session_state.edit_role is not None:
            role_to_edit = st.session_state.edit_role
            role_data = st.session_state.roles_map.get(role_to_edit, {"groups": [], "dashboards": []})

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
                        if st.checkbox(
                            f"{details['id']} - {name} ({', '.join(details['groups'])})",
                            value=checked,
                            key=f"edit_chk_{name}"
                        ):
                            selected_dashboards.append(name)

            if st.button("Update", key="update_role_btn"):
                if not new_name or not selected_groups:
                    st.warning("Please enter a role name and select at least one group.")
                else:
                    if new_name != role_to_edit:
                        st.session_state.roles_map.pop(role_to_edit)
                    st.session_state.roles_map[new_name] = {
                        "groups": selected_groups,
                        "dashboards": selected_dashboards
                    }
                    save_roles(st.session_state.roles_map)  # ✅ Pass the roles
                    st.success(f"✅ Role '{new_name}' updated successfully!")
                    st.session_state.edit_role = None
                    st.rerun()

            if st.button("⬅️ Back", key="cancel_edit_role"):
                st.session_state.edit_role = None
                st.rerun()


    def manage_responsibilities(self):
        st.header("🧩 Manage Responsibilities")
        css.hyper_link("css/hyperlink.css")

        # --- Initialize state ---
        if "responsibilities" not in st.session_state:
            st.session_state.responsibilities = {}
        if "add_resp_page" not in st.session_state:
            st.session_state.add_resp_page = False
        if "edit_resp" not in st.session_state:
            st.session_state.edit_resp = None
        if "roles_map" not in st.session_state:
            st.session_state.roles_map = {}
        if "resp_page" not in st.session_state:
            st.session_state.resp_page = 0  # Current page number

        PAGE_SIZE = 5  # Number of items per page
        responsibilities_list = list(st.session_state.responsibilities.items())
        total_pages = (len(responsibilities_list) - 1) // PAGE_SIZE + 1 if responsibilities_list else 1
        start_idx = st.session_state.resp_page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_items = responsibilities_list[start_idx:end_idx]

        # --- MAIN LIST PAGE ---
        if not st.session_state.add_resp_page and st.session_state.edit_resp is None:
            if st.button("➕ Add Responsibility"):
                st.session_state.add_resp_page = True
                st.rerun()

            st.subheader("Responsibilities")
            if page_items:
                cols = st.columns([4, 6, 2])
                cols[0].markdown("**Responsibility**")
                cols[1].markdown("**Roles**")
                cols[2].markdown("ID")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                for resp, data in page_items:
                    row_cols = st.columns([4, 6, 2])
                    with row_cols[0]:
                        if st.button(resp, key=f"edit_{resp}", help="Click to edit"):
                            st.session_state.edit_resp = resp
                            st.rerun()
                    with row_cols[1]:
                        st.write(", ".join(data.get("roles", []) if isinstance(data, dict) else data))
                    with row_cols[2]:
                        st.write(data.get("id", "") if isinstance(data, dict) else "")
                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                # --- Pagination Controls (OUTSIDE loop) ---
                pag_col1, pag_col2, pag_col3 = st.columns([1, 2, 1])
                with pag_col1:
                    if st.button("Prev", key="resp_prev") and st.session_state.resp_page > 0:
                        st.session_state.resp_page -= 1
                        st.rerun()
                with pag_col3:
                    if st.button("Next", key="resp_next") and st.session_state.resp_page < total_pages - 1:
                        st.session_state.resp_page += 1
                        st.rerun()
                st.markdown(f"Page {st.session_state.resp_page + 1} of {total_pages}")
            else:
                st.info("No responsibilities yet.")


        # --- ADD RESPONSIBILITY PAGE ---
        if st.session_state.add_resp_page:
            st.subheader("🆕 Add Responsibility")
            new_resp = st.text_input("Enter New Responsibility", key="new_resp").strip()
            selected_roles = st.multiselect(
                "Assign to Roles",
                list(st.session_state.roles_map.keys()),
                key="new_resp_roles"
            )

            # Assign ID safely
            if st.session_state.responsibilities:
                max_id = max([
                    int(details.get("id", 0)) if isinstance(details, dict) and str(details.get("id", "0")).isdigit() else 0
                    for details in st.session_state.responsibilities.values()
                ])
                resp_id = f"{max_id + 1:04d}"
            else:
                resp_id = "0001"

            st.write(f"Responsibility ID: {resp_id}")

            if st.button("Add Responsibility"):
                if not new_resp or not selected_roles:
                    st.warning("Please enter a responsibility and select at least one role.")
                elif new_resp in st.session_state.responsibilities:
                    st.warning("Responsibility already exists.")
                else:
                    st.session_state.responsibilities[new_resp] = {
                        "id": resp_id,
                        "roles": selected_roles
                    }
                save_responsibilities(st.session_state.responsibilities)
                st.success(f"✅ Responsibility '{new_resp}' created successfully!")
                st.session_state.add_resp_page = False
                st.rerun()

            if st.button("⬅️ Back"):
                st.session_state.add_resp_page = False
                st.rerun()

        # --- EDIT RESPONSIBILITY PAGE ---
        if st.session_state.edit_resp is not None:
            resp_to_edit = st.session_state.edit_resp
            data = st.session_state.responsibilities.get(resp_to_edit, {"roles": []})

            st.subheader(f"✏️ Edit Responsibility: {resp_to_edit}")
            new_name = st.text_input("Responsibility Name", value=resp_to_edit, key="edit_resp_name")
            selected_roles = st.multiselect(
                "Assign to Roles",
                options=list(st.session_state.roles_map.keys()),
                default=[r for r in data.get("roles", []) if r in st.session_state.roles_map],
                key="edit_resp_roles"
            )

            if st.button("Update"):
                if not new_name or not selected_roles:
                    st.warning("Please enter a name and select at least one role.")
                else:
                    if new_name != resp_to_edit:
                        st.session_state.responsibilities.pop(resp_to_edit)
                    st.session_state.responsibilities[new_name] = {
                        "id": data.get("id", resp_to_edit),
                        "roles": selected_roles
                    }
                    save_responsibilities(st.session_state.responsibilities)
                    st.success(f"✅ Responsibility '{new_name}' updated successfully!")
                    st.session_state.edit_resp = None
                    st.rerun()

            if st.button("⬅️ Back"):
                st.session_state.edit_resp = None
                st.rerun()



    def manage_users(self):
        st.header("🙋 Manage Users")
        css.hyper_link("css/hyperlink.css")

        # --- 1. Initialize session state ---
        if "users" not in st.session_state:
            st.session_state.users = {}
        if "add_user_page" not in st.session_state:
            st.session_state.add_user_page = False
        if "edit_user" not in st.session_state:
            st.session_state.edit_user = None
        if "resp_page" not in st.session_state:
            st.session_state.resp_page = 0

        # page size and items
        p_s = 5
        r_l = sorted(st.session_state.users.items())  # deterministic order by username
        total_items = len(r_l)
        # total pages (ceil division), at least 1
        t_p = max(1, (total_items + p_s - 1) // p_s)

        # ensure current page is in range
        if st.session_state.resp_page < 0:
            st.session_state.resp_page = 0
        if st.session_state.resp_page > t_p - 1:
            st.session_state.resp_page = t_p - 1

        s_i = st.session_state.resp_page * p_s
        e_i = s_i + p_s
        p_i = r_l[s_i:e_i]  # slice for current page

        # --- 2. Main list page ---
        if not st.session_state.add_user_page and st.session_state.edit_user is None:
            # Add User + Download
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button("➕ Add User"):
                    st.session_state.add_user_page = True
                    st.rerun()

            if st.session_state.users:
                with col2:
                    users_df = pd.DataFrame.from_dict(st.session_state.users, orient="index")
                    users_df.reset_index(inplace=True)
                    users_df.rename(columns={"index": "Username"}, inplace=True)

                    csv_buffer = io.StringIO()
                    users_df.to_csv(csv_buffer, index=False)
                    csv_bytes = csv_buffer.getvalue().encode("utf-8")

                    st.download_button(
                        label="⬇️",
                        data=csv_bytes,
                        file_name="registered_users.csv",
                        mime="text/csv",
                        help="Download all registered users"
                    )

            st.subheader("📋 Registered Users")

            if st.session_state.users:
                # Scrollable container
                st.markdown(
                    '<div style="max-height:400px; overflow-y:auto; padding-right:4px;">',
                    unsafe_allow_html=True
                )

                # Header
                cols = st.columns([1, 1, 1, 1, 1, 1])
                cols[0].markdown("**Username**")
                cols[1].markdown("**Responsibilities**")
                cols[2].markdown("**Email**")
                cols[3].markdown("**Inactive**")
                cols[4].markdown("**Admin**")
                cols[5].markdown("**User ID**")

                # Data rows - USE THE PAGED SLICE p_i
                for username, details in p_i:
                    roles = details.get("roles", [])
                    email = details.get("email", "")
                    inactive = details.get("inactive", False)
                    is_admin = details.get("is_admin", False)

                    st.markdown("<hr style='margin:0;'>", unsafe_allow_html=True)
                    cols = st.columns([1,1,1,1,1,1])

                    with cols[0]:
                        if st.button(username, key=f"user_{username}", help="Click to edit"):
                            st.session_state.edit_user = username
                            st.rerun()

                    cols[1].write(", ".join(roles))
                    cols[2].text(email)
                    cols[3].write("YES" if inactive else "NO")
                    cols[4].write("YES" if is_admin else "NO")
                    cols[5].write(details.get("id"))

                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # ---------------- Pagination controls ----------------
                prev_col, pages_col, next_col = st.columns([1, 1, 1])
                with prev_col:
                    if st.button(" Prev", key="prev_page") and st.session_state.resp_page > 0:
                        st.session_state.resp_page -= 1
                        st.rerun()


                with next_col:
                    if st.button("Next", key="next_page") and st.session_state.resp_page < t_p - 1:
                        st.session_state.resp_page += 1
                        st.rerun()

                st.markdown(f"Page {st.session_state.resp_page + 1} of {t_p}")

            else:
                st.info("No registered users yet.")

        # --- 4. Add User Page ---
        if st.session_state.add_user_page:
            st.subheader("🆕 Add User")
            self.createuser(is_edit=False)
            if st.button("⬅️ Back", key="add_user"):
                st.session_state.add_user_page = False
                st.rerun()

        # --- 5. Edit User Page ---
        if st.session_state.edit_user is not None:
            username = st.session_state.edit_user
            st.subheader(f"✏️ Edit User: {username}")
            self.createuser(is_edit=True, username=username)
            if st.button("⬅️ Back", key="edit_users"):
                st.session_state.edit_user = None
                st.rerun()

    def createuser(self, is_edit=False, username=None):
        # --- Prepare defaults ---
        if is_edit and username:
            user_data = st.session_state.users[username]
            default_email = user_data.get("email", "")
            saved_roles = user_data.get("roles", [])
            inactive_status = user_data.get("inactive", False)
            is_admin_default = user_data.get("is_admin", False)
            user_id = user_data.get("id", "N/A")
        else:
            username = ""
            default_email = ""
            saved_roles = []
            inactive_status = False
            is_admin_default = False

        available_roles = list(st.session_state.get("responsibilities", {}).keys())
        valid_saved_roles = [r for r in saved_roles if r in available_roles]

        # --- Unique form key ---
        form_key = f"user_form_{username}" if is_edit else "user_form_new"

        with st.form(key=form_key):
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
            if st.session_state.users:
                max_id = max([
                    int(details.get("id", 0)) if isinstance(details, dict) and str(details.get("id", "0")).isdigit() else 0
                    for details in st.session_state.users.values()
                ])
                resp_id = f"{max_id + 1:04d}"
            else:
                resp_id = "0001"

            st.write(f"User ID: {resp_id}")

            submitted = st.form_submit_button("Update User" if is_edit else "Save")

        if submitted:
            if not username_input or not email_input:
                st.error("Please fill all required fields")
                return

            if is_edit:
                # Update existing user
                if password_input:
                    hashed_pw = hash_password(password_input)
                    st.session_state.users[username]["password"] = hashed_pw
                st.session_state.users[username]["email"] = email_input
                st.session_state.users[username]["roles"] = roles_input
                st.session_state.users[username]["inactive"] = inactive_checkbox
                st.session_state.users[username]["is_admin"] = is_admin_checkbox
                st.success("✅ User updated successfully")
                st.session_state.edit_user = None
            else:
                # Create new user
                if username_input in st.session_state.users:
                    st.warning("Username already exists")
                    return
                if not password_input:
                    st.error("Password is required for new users")
                    return

                hashed_pw = hash_password(password_input)
                st.session_state.users[username_input] = {
                    "password": hashed_pw,
                    "roles": roles_input,
                    "email": email_input,
                    "inactive": inactive_checkbox,
                    "is_admin": is_admin_checkbox,
                    "last_activity": {"status": False, "date": None}
                  
                }
                st.success("✅ User created successfully")
                st.session_state.add_user_page = False

            # Save changes
            save_users(st.session_state.users)
            st.rerun()


    def logout(self):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.page="login"  # ✅ cor
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
        responsibilities = st.session_state.responsibilities.get(role, [])
        if option == "Home":
            st.write(f"Welcome User: {st.session_state.username}")
            if responsibilities:
                st.subheader("Your Responsibilities")
                for resp in responsibilities:
                    st.success(f"✅ {resp}")
            if "View Sales Chart" in responsibilities:
                st.subheader("Sales Dashboard")
                dashboards.show_sales_chart()
            if "Budgeting Access" in responsibilities:
                st.subheader("Budgeting Section")
                dashboards.show_budgeting_section()
            if "View Purchase Chart" in responsibilities:
                st.subheader("Purchase Dashboard")
            if "View Summary" in responsibilities:
                st.subheader("Purchase Summary")
                dashboards.show_budgeting_section()
        elif option == "My Profile":
            st.write(f"Username: {st.session_state.username}")
            st.write(f"Role: {st.session_state.role}")
            st.write("Company: Infoway Technosoft Solutions")


if __name__ == "__main__":
    app = InfowayApp()
    app.run()