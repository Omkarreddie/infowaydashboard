import os
import pickle
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
