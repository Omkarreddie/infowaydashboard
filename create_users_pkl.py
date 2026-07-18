import pickle
import hashlib
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

default_users = {
    "admin": {
        "password": hash_password("admin123"),
        "roles": ["admin"],
        "email": "admin@example.com",
        "inactive": False,   # 🚀 boolean only
        "is_admin": True,
        "id": "0001" 
    },
    "user": {
        "password": hash_password("user123"),
        "roles": ["user"],
        "email": "user@example.com",
        "inactive": False,   # 🚀 allow login
        "is_admin": False,
        "id": "0002" 

        
    }
}

with open("pickle_files/users.pkl", "wb") as f:
    pickle.dump(default_users, f)

print("✅ USERS.pkl file created successfully.")
