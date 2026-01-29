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
import os
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.responses import RedirectResponse
from pymongo.errors import DuplicateKeyError

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
    # Convert to User schema for response
    return User(
        email=user.email,
        disabled=user.disabled,
        username=user.username,
        display_name=user.display_name,
        role=user.role.value,  # Convert enum to string
        has_password=bool(user.hashed_password)
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


# ============================================================
# OAUTH SETUP
# ============================================================

oauth = OAuth()

# Validate Environment Variables
# We don't want to start the app with broken auth configuration if possible,
# or at least warn/fail on specific missing keys if we expect them to work.
if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
    print("WARNING: Google OAuth credentials missing")

if not os.getenv('GITHUB_CLIENT_ID') or not os.getenv('GITHUB_CLIENT_SECRET'):
    print("WARNING: GitHub OAuth credentials missing")


# Google Configuration
if os.getenv('GOOGLE_CLIENT_ID'):
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

# GitHub Configuration
if os.getenv('GITHUB_CLIENT_ID'):
    oauth.register(
        name='github',
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'}
    )


@router.get("/login/{provider}")
async def login_via_provider(provider: str, request: Request):
    """
    Redirects user to the OAuth provider (google or github).
    """
    # Validate provider
    valid_providers = ['google', 'github']
    if provider not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    # Construct absolute redirect URI based on base URL
    # Vercel/Prod vs Localhost
    # Use environment variable if set (Prod), otherwise use the request's base URL (Local)
    # This prevents localhost vs 127.0.0.1 cookie mismatch errors
    env_base = os.getenv("BASE_URL")
    if env_base and "localhost" not in env_base and "127.0.0.1" not in env_base:
         base_url = env_base
    else:
         base_url = str(request.base_url).rstrip('/')
         
    redirect_uri = f"{base_url}/auth/{provider}/callback"
    
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def auth_callback(provider: str, request: Request):
    """
    Handles the callback from the OAuth provider.
    Exchanges code for token, gets user info, and logs them in.
    """
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid provider")

    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        print(f"OAuth Error: {str(e)}") 
        raise HTTPException(status_code=400, detail="OAuth Authentication Failed")

    user_info = None
    email = None
    username = None
    avatar_url = None
    display_name = None

    # --- PROVIDER SPECIFIC LOGIC ---
    if provider == 'google':
        user_info = token.get('userinfo')
        if not user_info:
             user_info = await client.userinfo(token=token)
        
        email = user_info.get('email')
        display_name = user_info.get('name')
        avatar_url = user_info.get('picture')
        
        if email:
            username = email.split('@')[0]

    elif provider == 'github':
        # GitHub requires separate API calls
        resp = await client.get('user', token=token)
        if resp.status_code != 200:
            print(f"GitHub API Error: {resp.status_code} {resp.text}")
            raise HTTPException(status_code=400, detail="Failed to fetch GitHub user")
            
        try:
            user_info = resp.json()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid response from GitHub")
        
        # Get email (might be private)
        email = user_info.get('email')
        if not email:
            resp_emails = await client.get('user/emails', token=token)
            if resp_emails.status_code == 200:
                try:
                    for e in resp_emails.json():
                        if e.get('primary') and e.get('verified'):
                            email = e['email']
                            break
                except ValueError:
                    pass # Ignore if email list is unparseable
        
        username = user_info.get('login')
        display_name = user_info.get('name') or username
        avatar_url = user_info.get('avatar_url')

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from provider")

    # --- DB LOGIC ---
    user_doc = await UserDocument.find_one(UserDocument.email == email)
    
    is_new_user = False
    
    if not user_doc:
        # Create new user
        is_new_user = True
        
        # Prepare base username
        base_username = username or email.split('@')[0]
        base_username = re.sub(r'[^a-z0-9]', '', base_username.lower())
        if not base_username: 
            base_username = "user"
        
        # Atomic Insert Loop (Race Condition Handling)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    final_username = base_username
                else:
                    # Append random suffix on collision
                    final_username = f"{base_username}{random.randint(100, 9999)}"
                
                new_user = UserDocument(
                    email=email,
                    username=final_username,
                    display_name=display_name,
                    avatar_url=avatar_url,
                    provider=provider,
                    role=UserRole.USER,
                    disabled=False,
                    hashed_password=None # Explicitly None for OAuth users
                )
                await new_user.insert()
                user_doc = new_user
                break # Success!
            except DuplicateKeyError:
                if attempt == max_retries - 1:
                    print(f"Failed to generate unique username for {email}")
                    raise HTTPException(status_code=500, detail="Failed to create user account (username collision)")
                continue # Retry with new suffix
    else:
        # Update avatar/provider if missing (optional)
        if not user_doc.avatar_url and avatar_url:
            user_doc.avatar_url = avatar_url
            await user_doc.save()

    # Create JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_doc.email}, expires_delta=access_token_expires
    )
    
    # Redirect to Frontend Callback Handler matching the plan
    # frontend_url/auth/callback?token=...&new_user=true
    
    redirect_url = f"/static/auth/callback.html?token={access_token}"
    if is_new_user:
        redirect_url += "&new_user=true"
        
    return RedirectResponse(url=redirect_url)
