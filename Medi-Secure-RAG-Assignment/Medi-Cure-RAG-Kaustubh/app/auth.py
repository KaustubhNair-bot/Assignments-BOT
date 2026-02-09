"""
JWT Authentication Module
Handles user authentication, token generation, and verification
All authentication is performed locally - no data leaves the system
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import json
import os

from app.config import settings
from app.models import TokenData, UserCreate, UserResponse
from app.database import mongodb

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Fallback file-based user storage (if MongoDB not available)
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.json")


def load_users_from_file() -> dict:
    """Load users from JSON file (fallback)"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users_to_file(users: dict):
    """Save users to JSON file (fallback)"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, default=str)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt directly"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Generate password hash using bcrypt directly"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception


def get_user_data(username: str) -> Optional[dict]:
    """Get user data from MongoDB or file"""
    # Try MongoDB first
    if mongodb.is_connected():
        user = mongodb.get_user(username)
        if user:
            return user
    
    # Fallback to file
    users = load_users_from_file()
    if username in users:
        return {"username": username, **users[username]}
    
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get current authenticated user from JWT token"""
    token_data = verify_token(token)
    user_data = get_user_data(token_data.username)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        username=user_data.get("username", token_data.username),
        full_name=user_data["full_name"],
        specialty=user_data.get("specialty"),
        created_at=datetime.fromisoformat(user_data["created_at"]) if isinstance(user_data["created_at"], str) else user_data["created_at"]
    )


def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user with hashed password"""
    created_at = datetime.utcnow()
    
    user_doc = {
        "username": user_data.username,
        "password_hash": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "specialty": user_data.specialty,
        "created_at": created_at.isoformat()
    }
    
    # Try MongoDB first
    if mongodb.is_connected():
        if not mongodb.create_user(user_doc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
    else:
        # Fallback to file
        users = load_users_from_file()
        if user_data.username in users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        users[user_data.username] = {
            "password_hash": user_doc["password_hash"],
            "full_name": user_doc["full_name"],
            "specialty": user_doc["specialty"],
            "created_at": user_doc["created_at"]
        }
        save_users_to_file(users)
    
    return UserResponse(
        username=user_data.username,
        full_name=user_data.full_name,
        specialty=user_data.specialty,
        created_at=created_at
    )


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password"""
    user_data = get_user_data(username)
    
    if not user_data:
        return None
    
    if not verify_password(password, user_data["password_hash"]):
        return None
    
    return user_data


def create_demo_users():
    """Create demo users for testing"""
    demo_users = [
        {
            "username": "dr.smith",
            "password": "doctor123",
            "full_name": "Dr. John Smith",
            "specialty": "Cardiology"
        },
        {
            "username": "dr.jones",
            "password": "doctor123",
            "full_name": "Dr. Sarah Jones",
            "specialty": "General Surgery"
        },
        {
            "username": "dr.patel",
            "password": "doctor123",
            "full_name": "Dr. Raj Patel",
            "specialty": "Internal Medicine"
        }
    ]
    
    for user in demo_users:
        try:
            # Check if user already exists
            if get_user_data(user["username"]):
                continue
            create_user(UserCreate(**user))
            print(f"Created demo user: {user['username']}")
        except HTTPException:
            # User already exists
            pass
    
    print("Demo users ready!")
