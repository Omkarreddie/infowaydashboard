import os
import pickle
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