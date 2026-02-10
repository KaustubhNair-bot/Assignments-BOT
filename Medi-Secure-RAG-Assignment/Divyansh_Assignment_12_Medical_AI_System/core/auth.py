import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv("JWT_SECRET")


def create_tokens(username):
    """Creates both an Access Token and a Refresh Token."""
    # 15 Minute Access
    access_payload = {
        "user": username,
        "type": "access",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    }
    # 7 Day Refresh
    refresh_payload = {
        "user": username,
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }

    access_token = jwt.encode(access_payload, SECRET, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET, algorithm="HS256")
    return access_token, refresh_token


def verify_token(token):
    """Checks if a token is valid and returns the data inside."""
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "EXPIRED"  # Very important: Tell the app it's time to refresh!
    except:
        return None


def refresh_access_token(refresh_token):
    """
    Industry Standard: Uses a Refresh Token to issue a NEW Access Token.
    This prevents the user from being logged out every 15 minutes.
    """
    payload = verify_token(refresh_token)

    # If refresh token is valid and is actually a 'refresh' type
    if payload and payload.get("type") == "refresh":
        username = payload.get("user")
        # Create a new short-lived access token
        new_access_payload = {
            "user": username,
            "type": "access",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        }
        return jwt.encode(new_access_payload, SECRET, algorithm="HS256")

    return None  # If refresh token is expired (after 7 days), user MUST log in again
