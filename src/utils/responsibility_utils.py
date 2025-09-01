import os
import pickle
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
