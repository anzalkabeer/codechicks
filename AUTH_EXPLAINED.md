# Authentication Code Explained

This document provides a detailed breakdown of the authentication logic implemented in the `auth/` directory.

## 1. Data Models (`auth/schemas.py`)
This file defines the data structures (Schemas) used for request and response validation.

```python
from pydantic import BaseModel
from typing import Optional

# Base User model with common attributes
class User(BaseModel):
    email: str
    disabled: Optional[bool] = None

# Internal model for the database, includes the hashed password.
# Inherits from User, so it has email and disabled too.
class UserInDB(User):
    hashed_password: str

# Schema for the Registration request (what the user sends)
class UserRegister(BaseModel):
    email: str
    password: str

# Schema for the Login request
class UserLogin(BaseModel):
    email: str
    password: str

# Schema for the Token response (what the server sends back after login)
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for data embedded inside the Token
class TokenData(BaseModel):
    email: Optional[str] = None
```

## 2. Utilities (`auth/utils.py`)
This file handles the low-level security operations: hashing strings and generating tokens.

```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# Security Configuration
SECRET_KEY = "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_IN_PRODUCTION" # Key used to sign JWTs
ALGORITHM = "HS256" # Hashing algorithm for the JWT signature
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # How long a token remains valid

# Setup Password Hashing
# We use PBKDF2-SHA256 which is secure and compatible.
# deprecated="auto" allows upgrading hashes in the future if needed.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Function to check if a plain password matches a hashed one
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to turn a plain password into a secure hash
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to generate a JWT (JSON Web Token)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy() # Copy data to avoid mutating original
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Add expiration claim ('exp') to the token data
    to_encode.update({"exp": expire})
    
    # Encode and sign the token using the SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## 3. Router & Logic (`auth/router.py`)
This file contains the API endpoints and the logic to glue everything together.

### Imports & Setup
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
...

# Create a router instance prefixed with /auth
router = APIRouter(prefix="/auth", tags=["auth"])

# Local dictionary acting as a database for this demo
fake_users_db = {}

# Defines how the client sends the token (Authorization: Bearer <token>)
# and where the user goes to get one (auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
```

### Dependency: `get_current_user`
This is critical. It protects routes by verifying the token.
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Standard 401 Unauthorized Error to raise if anything fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        ...
    )
    try:
        # Decode the JWT using our SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract the email (subject) from the payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        # If token is invalid or expired
        raise credentials_exception
    
    # Check if the user actually exists in our DB
    user = get_user(fake_users_db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user # Return the user object to the path operation
```

### Endpoint: Register (`POST /auth/register`)
```python
@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    # Check if user already exists
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Save user to "DB"
    user_in_db = UserInDB(
        email=user.email,
        hashed_password=hashed_password,
        disabled=False
    )
    fake_users_db[user.email] = user_in_db.dict()
    
    # Create and return an access token immediately (auto-login)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### Endpoint: Login (`POST /auth/login`)
```python
@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    # Retrieve user
    user_in_db = get_user(fake_users_db, user.email)
    
    # Verify both existence and password match
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(...)
    
    # Generate Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### Endpoint: Me (`GET /auth/me`)
```python
# This route requires a valid token because it depends on get_current_user
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user # Returns the user data extracted from the token/DB
```
