"""User authentication with bcrypt password hashing."""
import bcrypt
from typing import Optional, Dict, Any, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings
from .jwt_handler import JWTHandler


class Authenticator:
    """Handles user authentication and session management."""
    
    def __init__(self):
        self.jwt_handler = JWTHandler()
        self.users = settings.DEMO_USERS
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Authenticate a user and generate a JWT token.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Tuple of (success, token, user_data)
        """
        if username not in self.users:
            return False, None, None
        
        user = self.users[username]
        
        if not self.verify_password(password, user["password_hash"]):
            return False, None, None
        
        user_data = {
            "name": user["name"],
            "specialty": user["specialty"],
            "license_id": user["license_id"]
        }
        
        token = self.jwt_handler.create_token(username, user_data)
        
        return True, token, user_data
    
    def validate_session(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate an existing session token.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Tuple of (is_valid, user_payload)
        """
        payload = self.jwt_handler.verify_token(token)
        if payload:
            return True, payload
        return False, None
    
    def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user information from a valid token."""
        payload = self.jwt_handler.verify_token(token)
        if payload:
            return {
                "username": payload.get("sub"),
                "name": payload.get("name"),
                "specialty": payload.get("specialty"),
                "license_id": payload.get("license_id")
            }
        return None
