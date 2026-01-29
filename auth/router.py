"""
Authentication Router

Handles user registration, login, and token validation using MongoDB via Beanie.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth.schemas import User, UserRegister, UserLogin, Token, TokenData, AdminKeyRequest
from auth.utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_KEY
from datetime import timedelta
from database.models import UserDocument, UserRole
import secrets
import re
import random

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_from_db(email: str) -> Optional[UserDocument]:
    """Fetch user from MongoDB by email."""
    return await UserDocument.find_one(UserDocument.email == email)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validate JWT token and return current user.
    
    Raises HTTPException 401 if token is invalid or user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_from_db(token_data.email)
    if user is None:
        raise credentials_exception
    
    # Check if user is disabled
    if user.disabled:
        raise credentials_exception
    
    # Convert to User schema for response
    return User(
        email=user.email,
        disabled=user.disabled,
        username=user.username,
        display_name=user.display_name,
        role=user.role.value  # Convert enum to string
    )


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the current user is an admin.
    
    Raises HTTPException 403 if user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    """
    Register a new user.
    
    Creates user in MongoDB and returns JWT token.
    """
    # Check if user already exists
    existing_user = await UserDocument.find_one(UserDocument.email == user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user document
    hashed_password = get_password_hash(user.password)
    
    # Generate sanitary and unique username from email prefix
    base_username = user.email.split('@')[0].lower()
    # Remove special characters, keep alphanumeric
    base_username = re.sub(r'[^a-z0-9]', '', base_username)
    if not base_username:
        base_username = f"user{random.randint(1000, 9999)}"
        
    # Ensure uniqueness
    username = base_username
    counter = 1
    while await UserDocument.find_one(UserDocument.username == username):
        username = f"{base_username}{counter}"
        counter += 1
    
    display_name = username.title() if len(username) > 2 else "User"
    
    new_user = UserDocument(
        email=user.email,
        hashed_password=hashed_password,
        disabled=False,
        role=UserRole.USER,
        username=username,
        display_name=display_name
    )
    await new_user.insert()
    
    # Generate and return access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """
    Authenticate user and return JWT token.
    """
    user_in_db = await get_user_from_db(user.email)
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user


@router.post("/upgrade-to-admin")
async def upgrade_to_admin(
    request: AdminKeyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Upgrade current user to admin role by verifying admin key.
    
    The admin key is stored in the .env file.
    """
    # Verify admin key using constant-time comparison to prevent timing attacks
    if not ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin key not configured"
        )
    if not request.admin_key or not secrets.compare_digest(request.admin_key, ADMIN_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin key"
        )
    
    # Get user document and update role
    user_doc = await get_user_from_db(current_user.email)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_doc.role == UserRole.ADMIN:
        return {"message": "You are already an admin", "role": "admin"}
    
    user_doc.role = UserRole.ADMIN
    await user_doc.save()
    
    return {"message": "Successfully upgraded to admin", "role": "admin"}


@router.post("/downgrade-to-user")
async def downgrade_to_user(current_user: User = Depends(get_current_user)):
    """
    Downgrade current admin to regular user role.
    """
    user_doc = await get_user_from_db(current_user.email)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_doc.role == UserRole.USER:
        return {"message": "You are already a regular user", "role": "user"}
    
    # Safeguard: Prevent the last admin from downgrading
    admin_count = await UserDocument.find(UserDocument.role == UserRole.ADMIN).count()
    if admin_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot downgrade the last admin account. Promote another user first."
        )
    
    user_doc.role = UserRole.USER
    await user_doc.save()
    
    return {"message": "Successfully downgraded to user", "role": "user"}
