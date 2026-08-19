import os
import json
import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "data" / "users.json"

def init_users_file():
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        default_data = {
            "users": [
                {
                    "user_id": "CM001",
                    "password": hash_password("password123"),
                    "name": "Enter your name",
                    "role": "Care Manager"
                }
            ]
        }
        with open(USERS_FILE, "w") as f:
            json.dump(default_data, f, indent=4)

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, hashed_or_plain):
    if hashed_or_plain.startswith("$2b$") or hashed_or_plain.startswith("$2a$"):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_or_plain.encode("utf-8"))
        except Exception:
            return False
    return password == hashed_or_plain

def authenticate_user(user_id, password):
    init_users_file()
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return None
        
    for user in data.get("users", []):
        if user["user_id"] == user_id:
            if verify_password(password, user["password"]):
                return user
    return None

def register_user(user_id, name, password, role):
    init_users_file()
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        data = {"users": []}
        
    # Check if duplicate
    for user in data.get("users", []):
        if user["user_id"] == user_id:
            return False
            
    # Add new user
    new_user = {
        "user_id": user_id,
        "password": hash_password(password),
        "name": name,
        "role": role
    }
    data["users"].append(new_user)
    
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False
