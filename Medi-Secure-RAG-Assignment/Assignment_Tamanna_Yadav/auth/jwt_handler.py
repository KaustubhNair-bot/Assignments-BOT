"""JWT token generation and validation."""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings


class JWTHandler:
    """Handles JWT token creation and verification for doctor authentication."""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_hours = settings.JWT_EXPIRATION_HOURS
    
    def create_token(self, username: str, user_data: Dict[str, Any]) -> str:
        """
        Create a JWT token for an authenticated doctor.
        
        Args:
            username: The doctor's username
            user_data: Additional user information (name, specialty, etc.)
            
        Returns:
            Encoded JWT token string
        """
        payload = {
            "sub": username,
            "name": user_data.get("name", ""),
            "specialty": user_data.get("specialty", ""),
            "license_id": user_data.get("license_id", ""),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            Decoded payload if valid, None if invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def is_token_valid(self, token: str) -> bool:
        """Check if a token is valid without returning the payload."""
        return self.verify_token(token) is not None
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get the expiration time of a token."""
        payload = self.verify_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
