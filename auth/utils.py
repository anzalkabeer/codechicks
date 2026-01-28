from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Debug mode - defaults to FALSE for security (opt-in)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Admin key for upgrading users to admin role
ADMIN_KEY = os.getenv("ADMIN_KEY", "")

# Security: Raise errors in production if keys are not properly set
if not DEBUG:
    if SECRET_KEY == "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION":
        raise ValueError("SECRET_KEY must be set in production! Generate with: openssl rand -hex 32")
    if not ADMIN_KEY or ADMIN_KEY == "supersecretadminkey123":
        raise ValueError("ADMIN_KEY must be set to a secure value in production! Generate with: openssl rand -hex 32")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Use configured expiry time from environment
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
