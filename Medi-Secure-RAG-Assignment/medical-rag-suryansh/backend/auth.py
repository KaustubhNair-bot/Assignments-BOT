from jose import jwt 
from datetime import datetime, timedelta

SECRET = "hospital-secret"

USERS = {
    "doctor1": "pass123",
    "doctor2": "med456"
}

def authenticate(username, password):
    if username in USERS and USERS[username] == password:
        return True
    return False

def create_token(user):
    payload = {
        "sub": user,
        "exp": datetime.utcnow() + timedelta(hours=2) # Token valid for 2 hours
    }
    return jwt.encode(payload, SECRET)

def verify_token(token):
    return jwt.decode(token, SECRET) # Decode and verify token authenticity and return stored data; Raises error if token is invalid or expired