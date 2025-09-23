import streamlit as st
from src.utils.login import LoginPage, hash_password
import src.utils.css as css
from src.utils.user_utils import load_users, save_users
from src.utils.role_utils import load_roles, save_roles
from src.utils.responsibility_utils import load_responsibilities, save_responsibilities
from src.utils.dashboard_utils import load_dashboard_groups, save_dashboard_groups, load_dashboards, save_dashboards
import src.utils.dashboard as dashboards
from src.utils.jwt_utils import verify_token  # NEW

import io
import pandas as pd


class InfowayApp():
    def __init__(self):
        # ---------------- INIT SESSION STATE ----------------
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'page' not in st.session_state:
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
            st.session_state.dashboard_groups = load_dashboard_groups()
        if 'dashboards' not in st.session_state:
            st.session_state.dashboards = load_dashboards()

        # ---------------- SSO HANDLING ----------------
        if not st.session_state.get("logged_in", False):
            token = st.session_state.get("token", [None])[0]

            if token:
                payload = verify_token(token)
                if payload:
                    st.session_state.logged_in = True
                    st.session_state.username = payload["sub"]
                    st.session_state.role = payload.get("role", "user")
                    st.session_state.page = "dashboard"

        # ---------------- PAGE CONFIG ----------------
        if not st.session_state.get("logged_in", False):
            st.set_page_config(page_title="Infoway Login", layout="centered")
        else:
            st.set_page_config(page_title="Infoway Dashboard", layout="wide")

    def run(self):
        if not st.session_state.users:
            st.warning("NO Users Found")
            return

        user_role = st.session_state.role.strip().lower()

        if st.session_state.logged_in:
            if user_role == "admin":
                self.admin_dashboard()
            elif user_role:
                self.user_dashboard()
            else:
                st.warning("No dashboard found for this role.")
        else:
            login_page = LoginPage()
            login_page.login()

    # keep rest of your code (admin_dashboard, user_dashboard, etc.) unchanged


    def admin_dashboard(self):
        css.load_login_css("css/main.css" )
        st.sidebar.markdown(
            "<marquee behaviour='scroll' direction='left' scrollamount='5' style='color: #035b30; font-size:20px; font-style: italic;'>Welcome to the Infoway Dashboard!</marquee>",
            unsafe_allow_html=True,
        )  


        st.sidebar.markdown("---")
        st.header("Admin Portal")
        if "active_module" not in st.session_state:
            st.session_state.active_module = None
        
        if st.sidebar.button("Sales Module"):
            st.session_state.active_module= "sales"

        if st.sidebar.button("📦 Purchase Module"):
            st.session_state.active_module = "purchase"

        if st.sidebar.button("🛠️ Admin Portal"):
            st.session_state.active_module = "admin"
        if st.session_state.active_module == "sales":
            sales_tabs = st.tabs([
                "📊 View Sales Chart",
                "📈 View Budgeting"
            ])

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
        css.hyper_link("css/hyperlink.css")  # Load CSS once

        # ------------------ Initialize session state ------------------
        if "dashboard_groups" not in st.session_state:
            st.session_state.dashboard_groups = load_dashboard_groups()

        if "add_group_page" not in st.session_state:
            st.session_state.add_group_page = False

        if "edit_group" not in st.session_state:
            st.session_state.edit_group = None

        if "resp_page" not in st.session_state:
            st.session_state.resp_page = 0

        # ------------------ Convert set to dict if needed ------------------
        if isinstance(st.session_state.dashboard_groups, set):
            st.session_state.dashboard_groups = {
                g: {"Description": "", "id": ""} for g in st.session_state.dashboard_groups
            }
            save_dashboard_groups(st.session_state.dashboard_groups)

        # ------------------ MAIN LIST PAGE ------------------
        if not st.session_state.add_group_page and st.session_state.edit_group is None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("📊 Manage Dashboard Groups")
            with col2:
                if st.button("➕ Add Dashboard Group", key="go_add_group"):
                    st.session_state.add_group_page = True
                    st.rerun()

            if st.session_state.dashboard_groups:
                # Pagination setup
                page_size = 5
                search_query = st.text_input("Filter dashboard groups (By Dashboard Group or ID)").strip().lower()

                if search_query:
                    f_r = {u: d for u, d in st.session_state.dashboard_groups.items()
                        if search_query in u.lower()
                        or search_query in str(d.get("id", "")).lower()}
                else:
                    f_r = st.session_state.dashboard_groups

                d_g = list(f_r.items())
                t_p = (len(d_g) - 1) // page_size + 1 if d_g else 1
                s_i = st.session_state.resp_page * page_size
                e_i = s_i + page_size
                p_i = d_g[s_i:e_i]

                # Header row
                col1, col2, col3 = st.columns([0.2, 0.2, 1])
                col1.markdown("**GROUPS**")
                col2.markdown("**Dashboard ID**")
                col3.markdown("**DESCRIPTION**")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                # Data rows
                for g, d in p_i:
                    col1, col2, col3 = st.columns([0.2, 0.2, 1])
                    with col1:
                        if st.button(g, key=f"edit_{g}", help="Click to edit"):
                            st.session_state.edit_group = g
                            st.rerun()
                    col2.write(d.get("id", ""))
                    col3.write(d.get("Description", ""))
                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                # Pagination buttons
                p1, p3 = st.columns([1, 1])
                with p1:
                    if st.button("Prev") and st.session_state.resp_page > 0:
                        st.session_state.resp_page -= 1
                        st.rerun()
                with p3:
                    if st.button("Next") and st.session_state.resp_page < t_p - 1:
                        st.session_state.resp_page += 1
                        st.rerun()

                st.markdown(f"Page {st.session_state.resp_page + 1} of {t_p}")

            else:
                st.info("No dashboard groups added yet.")

        # ------------------ ADD GROUP PAGE ------------------
        elif st.session_state.add_group_page:
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
        elif st.session_state.edit_group is not None:
            g = st.session_state.edit_group
            st.subheader(f"✏️ Edit Group: {g}")
            old_id = st.session_state.dashboard_groups[g]["id"]
            group_desc_safe = st.session_state.dashboard_groups[g].get("Description", "")

            new_name = st.text_input("Edit Group Name", value=g, key="edit_name_input")
            new_desc = st.text_input("Edit Description", value=group_desc_safe, key="edit_desc_input")
            col1,col2=st.columns([0.2,1])
            with col1:
                if st.button("Update", key="update_group_btn"):
                    if not new_name:
                        st.warning("Group name cannot be empty.")
                    else:
                        if new_name != g:
                            st.session_state.dashboard_groups.pop(g)
                        st.session_state.dashboard_groups[new_name] = {
                            "Description": new_desc,
                            "id": old_id
                        }
                        save_dashboard_groups(st.session_state.dashboard_groups)
                        st.success(f"✅ Group '{new_name}' updated successfully!")
                        st.session_state.edit_group = None
                        st.rerun()
            with col2:
                if st.button("⬅️ Back", key="cancel_edit_group"):
                    st.session_state.edit_group = None
                    st.rerun()

    def dashboard(self):
        css.hyper_link("css/hyperlink.css")  # Load CSS once

        # ------------------ Prepare dashboard groups list ------------------
        dashboard_groups = st.session_state.get("dashboard_groups", {})
        if isinstance(dashboard_groups, dict):
            dashboard_groups_list = list(dashboard_groups.keys())
        elif isinstance(dashboard_groups, set):
            dashboard_groups_list = list(dashboard_groups)
        else:
            dashboard_groups_list = []

        # ------------------ Initialize session state ------------------
        if "add_dashboard_page" not in st.session_state:
            st.session_state.add_dashboard_page = False
        if "edit_dashboard" not in st.session_state:
            st.session_state.edit_dashboard = None
        if "d_page" not in st.session_state:
            st.session_state.d_page = 0
        

        # ------------------ MAIN LIST PAGE ------------------
        if not st.session_state.add_dashboard_page and st.session_state.edit_dashboard is None:
            col1,col2=st.columns([3,1])
            with col1:
                st.subheader("🏠 Manage Dashboards")
            with col2:
                if st.button("➕ Add Dashboard", key="new_dashboard_btn"):
                    st.session_state.add_dashboard_page = True
                    st.rerun()

            st.subheader("Dashboards")
            dashboards = st.session_state.get("dashboards", {})

            if dashboards:
                # --- Pagination setup ---
                page_size = 5
                search_query=st.text_input("Filter Dashboards(by Dashbooard or ID)").strip().lower()
                if search_query:
                    f_r={u:d for u , d in st.session_state.dashboards.items()
                         if search_query in u.lower()
                         or any (search_query in r.lower() for r in 
                                 d.get("Dashboard Name",[]))
                                 or search_query in str(d.get("id","")).lower()}
                else:
                    f_r=st.session_state.dashboards
                d = list(f_r.items())
                t_p = (len(d) - 1) // page_size + 1 if d else 1
                s_i = st.session_state.d_page * page_size
                e_i = s_i + page_size
                p_i = d[s_i:e_i] 

                cols = st.columns([0.2, 0.2, 1])
                cols[0].markdown("**Dashboard Name**")
                cols[1].markdown("**Dashboard ID**")
                cols[2].markdown("**Groups**")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                for d_name, details in p_i:
                    row_cols = st.columns([0.2, 0.2, 1])
                    with row_cols[0]:
                        if st.button(d_name, key=f"dashboard_btn_{d_name}", help="Click to edit"):
                            st.session_state.edit_dashboard = d_name
                            st.rerun()
                    with row_cols[1]:
                        st.write(details.get("id", ""))
                    with row_cols[2]:
                        st.write(", ".join(details.get("groups", [])))
                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                p1, p2 = st.columns([1, 1])
                with p1:
                    if st.button("Prev.") and st.session_state.d_page > 0:
                        st.session_state.d_page -= 1
                        st.rerun()
                with p2:
                    if st.button("Next.") and st.session_state.d_page < t_p - 1:
                        st.session_state.d_page += 1
                        st.rerun()

                st.markdown(f"Page {st.session_state.d_page + 1} of {t_p}")

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
            col1,col2=st.columns([0.2,1])
            with col1:
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
            with col2:
                if st.button("⬅️ Back", key="cancel_edit_dashboard"):
                    st.session_state.edit_dashboard = None
                    st.rerun()


    def manage_roles(self):
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

        page_size = 5
        search_query = st.text_input("Filter Roles (by Role, Group, or ID)").strip().lower()
        if search_query:
                st.session_state.resp_page = 0  # Reset to first page when searching
                filtered_roles = {
                    role: data
                    for role, data in st.session_state.roles_map.items()
                    if search_query in role.lower()
                    or any(search_query in g.lower() for g in data.get("groups", []))
                    or search_query in str(data.get("id", "")).lower()
                }
        else:
            filtered_roles=st.session_state.roles_map
            

    # --- Search / Filter ---
        # --- Pagination on filtered roles ---
        filtered_list = list(filtered_roles.items())
        t_p = max(1, (len(filtered_list) - 1) // page_size + 1)
        start_idx = st.session_state.resp_page * page_size
        end_idx = start_idx + page_size
        page_items = filtered_list[start_idx:end_idx]
        # --- Combined options for groups ---
        column_names = []
        combined_options = sorted(set(st.session_state.dashboard_groups).union(column_names))
        # --- MAIN LIST PAGE ---
        # --- MAIN LIST PAGE ---
        if not st.session_state.add_role_page and st.session_state.edit_role is None:
            col1,col2=st.columns([1,1])
            with col1:
                st.header("👥 Manage Roles")
            with col2:
                if st.button("➕ Add Role", key="new_role_btn"):
                    st.session_state.add_role_page = True
                    st.rerun()
           
            st.subheader("Roles")
            if st.session_state.roles_map:
                cols = st.columns([0.25, 0.25, 1])
                cols[0].markdown("**Role Name**")
                cols[1].markdown("**Groups**")
                cols[2].markdown("Role ID")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                for role, data in page_items: 
                    row_cols = st.columns([0.25, 0.25, 1])
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
                p1,  p3 = st.columns([1, 1])
                with p1:
                    if st.button("Prev", key="roles_prev") and st.session_state.resp_page > 0:
                        st.session_state.resp_page -= 1
                        st.rerun()
                with p3:
                    if st.button("Next", key="roles_next") and st.session_state.resp_page < t_p - 1:
                        st.session_state.resp_page += 1
                        st.rerun()
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
            col1,col2=st.columns([0.2,1])
            with col1:
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
            with col2:
                if st.button("⬅️ Back", key="cancel_edit_role"):
                    st.session_state.edit_role = None
                    st.rerun()


    def manage_responsibilities(self):
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
        total_pages = (len(responsibilities_list) - 1)// PAGE_SIZE + 1 if responsibilities_list else 1
        start_idx = st.session_state.resp_page * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        page_items = responsibilities_list[start_idx:end_idx]

        # --- MAIN LIST PAGE ---
        if not st.session_state.add_resp_page and st.session_state.edit_resp is None:
            col1,col2=st.columns([1,1])
            with col1:
                    st.header("🧩 Manage Responsibilities")
            with col2:
                if st.button("➕ Add Responsibility"):
                    st.session_state.add_resp_page = True
                    st.rerun()
            search_query = st.text_input("Filter users (by Responsibility, Role or ID)").strip().lower()

            if search_query:
                 filtered_responsibilities = {
                    u: d for u, d in st.session_state.responsibilities.items()
                    if search_query in u.lower()
                    or any(search_query in r.lower() for r in d.get("roles", []))
                    or search_query in str(d.get("id", "")).lower()
                    }
            else:
                filtered_responsibilities = st.session_state.responsibilities

            st.subheader("Responsibilities")
            if page_items:
                cols = st.columns([0.3, 0.3, 1])
                cols[0].markdown("**Responsibility**")
                cols[1].markdown("**Roles**")
                cols[2].markdown("ID")
                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)

                for resp, data in page_items:
                    row_cols = st.columns([0.3, 0.3, 1])
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
            col1,col2=st.columns([0.2,1])
            with col1:
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
            with col2:
                if st.button("⬅️ Back"):
                    st.session_state.edit_resp = None
                    st.rerun()



    def manage_users(self):
        css.hyper_link("css/hyperlink.css")

        # --- Initialize session state ---
        if "users" not in st.session_state:
            st.session_state.users = {}
        if "add_user_page" not in st.session_state:
            st.session_state.add_user_page = False
        if "edit_user" not in st.session_state:
            st.session_state.edit_user = None
        if "resp_page" not in st.session_state:
                    st.session_state.resp_page = 0

        # --- Main list page ---
        if not st.session_state.add_user_page and st.session_state.edit_user is None:
            # Add User + Download
            col1, col2 = st.columns([4, 2])
            with col1:
                st.header("🙋 Manage Users")
            with col2:
                if st.button("➕ Add User"):
                    st.session_state.add_user_page = True
                    st.rerun()

            if st.session_state.users:
                # --- 🔍 Search box ---
                search_query = st.text_input("Filter users (by Username, Email, Role, or ID)").strip().lower()

                if search_query:
                    filtered_users = {
                        u: d for u, d in st.session_state.users.items()
                        if search_query in u.lower()
                        or search_query in d.get("email", "").lower()
                        or any(search_query in r.lower() for r in d.get("roles", []))
                        or search_query in str(d.get("id", "")).lower()
                    }
                else:
                    filtered_users = st.session_state.users
                # --- Pagination ---
                page_size = 5
                total_items = len(filtered_users)
                total_pages = max(1, (total_items + page_size - 1) // page_size)
                # Reset page if search changes
             

                start = st.session_state.resp_page * page_size
                end = start + page_size
                page_items = list(sorted(filtered_users.items()))[start:end]

                if page_items:
                    # Scrollable container
                    st.markdown(
                        '<div style="max-height:400px; overflow-y:auto; padding-right:4px;">',
                        unsafe_allow_html=True
                    )
                    st.subheader("📋 Registered Users")


                    # Header
                    cols = st.columns([1, 1, 1.1, 0.5, 0.5, 1])
                    cols[0].markdown("**Username**")
                    cols[1].markdown("**Responsibilities**")
                    cols[2].markdown("**Email**")
                    cols[3].markdown("**Inactive**")
                    cols[4].markdown("**Admin**")
                    cols[5].markdown("**User ID**")

                    # Data rows
                    for username, details in page_items:
                        roles = details.get("roles", [])
                        email = details.get("email", "")
                        inactive = details.get("inactive", False)
                        is_admin = details.get("is_admin", False)

                        st.markdown("<hr style='margin:0;'>", unsafe_allow_html=True)
                        cols = st.columns([1, 1, 1.1, 0.5, 0.5, 1])

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

                    # --- Pagination controls ---
                    prev_col, next_col,col3 = st.columns([3, 2,1])

                    with prev_col:
                        if st.button("Prev", key="prev_page") and st.session_state.resp_page > 0:
                            st.session_state.resp_page -= 1
                            st.rerun()

                    with next_col:
                        if st.button("Next", key="next_page") and st.session_state.resp_page < total_pages - 1:
                            st.session_state.resp_page += 1
                            st.rerun()
                    with col3:
                         if st.session_state.users:
                            users_df = pd.DataFrame.from_dict(st.session_state.users, orient="index")
                            users_df.reset_index(inplace=True)
                            users_df.rename(columns={"index": "Username"}, inplace=True)

                            csv_buffer = io.StringIO()
                            users_df.to_csv(csv_buffer, index=False)
                            csv_bytes = csv_buffer.getvalue().encode("utf-8")

                            st.download_button(
                                label="🡇",
                                data=csv_bytes,
                                file_name="registered_users.csv",
                                mime="text/csv",
                                help="Download all registered users"
                            )


                    st.markdown(f"Page **{st.session_state.resp_page + 1}** of **{total_pages}**")

                else:
                    st.warning("No users found for this search.")
            else:
                st.info("No registered users yet.")
      # --- Add User Page ---
        if st.session_state.add_user_page:
            st.subheader("🆕 Add User")
            self.createuser(is_edit=False)
            if st.button("⬅️ Back", key="add_user"):
                st.session_state.add_user_page = False
                st.rerun()

        # --- Edit User Page ---
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
                resp_id = "0003"

            st.write(f"User ID: {resp_id}")

            submitted = st.form_submit_button("Update User" if is_edit else "Save")

        if submitted:
            if not username_input or not email_input:
                st.error("Please fill all required fields")
                return

            if is_edit:
                if username=="admin":
                    st.session_state.users[username]["email"] = email_input
                    st.session_state.users[username]["roles"] = roles_input
                    st.success("Admin Updated Successfully")
                    st.session_state.edit_user= None

                else:
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
                    "last_activity": {"status": False, "date": None},
                    "id": resp_id   # ✅ SAVE USER ID HERE
                  
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
        st.session_state.page="login" 
         # ✅ cor
        st.rerun()

    def user_dashboard(self):
       
        css.load_main_css("css/main.css")

        # --- Sidebar welcome ---
        st.sidebar.markdown(
            "<marquee behaviour='scroll' direction='left' scrollamount='5' "
            "style='color: #035b30; font-size:20px; font-style: italic;'>"
            "Welcome to the Infoway Dashboard!</marquee>", unsafe_allow_html=True
        )
        if "show_home" not in st.session_state:
           st.session_state.show_home = True   # or False, depending on your default

        if "show_profile" not in st.session_state:
            st.session_state.show_profile = False

        username = st.session_state.username
        user_data = st.session_state.users.get(username, {})
        responsibilities = user_data.get("roles", [])
        email = user_data.get("email", "")
        inactive = user_data.get("inactive", False)
        user_id = user_data.get("id", "N/A")

        if st.sidebar.button("Home"):
            st.session_state.show_profile= False
            st.session_state.show_home=True
        if st.sidebar.button("👤 My Profile"):
            st.session_state.show_profile = True
            st.session_state.show_home=False

        if st.sidebar.button("🚪 Log Out"):
            self.logout()
            st.success("Logged out successfully")
            st.session_state.show_profile = False
            st.rerun()
        if st.session_state.show_home:
            st.header(f"🏠 Welcome {username}")
            st.write("Your dynamic dashboard modules:")

            if responsibilities:
                for resp in responsibilities:
                    module_name = resp.lower()
                    if module_name == "view sales chart":
                        with st.expander("📈 Sales Chart Module"):
                            dashboards.show_sales_chart()

                    elif module_name == "view purchase chart":
                        with st.expander("📊 Purchase Chart Module"):
                            dashboards.lpo_grn_gross_amount()

                    elif module_name == "budgeting":
                        with st.expander("💰 Budgeting Module"):
                            dashboards.show_budgeting_section()

                    elif module_name=="View Grn Data":
                        with st.expander("📊 Purchase Module"):
                             dashboards.lpo_data()

                    else:
                        st.warning(f"⚠️ Responsibility '{resp}' is not mapped to any module yet.")
            else:
                st.info("No responsibilities assigned to you yet.")
        # --- Profile Section ---
        if st.session_state.show_profile :
            st.subheader("👤 My Profile")
            st.write(f"**Username:** {username}")
            st.write(f"**Responsibilities:** {', '.join(responsibilities) if responsibilities else 'No responsibilities'}")
            st.write("🏢 **Company:** Infoway Technosoft Solutions")

            profile_df = pd.DataFrame([{ 
                "Email": email,
                "User ID": user_id
            }])
            st.table(profile_df)        
if __name__ == "__main__":
    app = InfowayApp()
    app.run()