"""
Authentication Router

Handles user registration, login, and token validation using MongoDB via Beanie.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth.schemas import User, UserRegister, UserLogin, Token, TokenData, UserInDB
from auth.utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from database.models import UserDocument

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_from_db(email: str) -> UserDocument | None:
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
    
    # Convert to User schema for response
    return User(
        email=user.email,
        disabled=user.disabled,
        username=user.username,
        display_name=user.display_name
    )


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
    new_user = UserDocument(
        email=user.email,
        hashed_password=hashed_password,
        disabled=False
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
