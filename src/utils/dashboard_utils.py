import os
import pickle
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
