from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# pre-created demo users 
fake_doctors_db = {
    "abhimanyu": pwd_context.hash("doctor123"),
    "dr_singh": pwd_context.hash("secure456"),
}

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
