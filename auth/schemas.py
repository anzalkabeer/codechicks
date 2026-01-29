from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    email: str
    disabled: Optional[bool] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    role: str = "user"  # user or admin
    has_password: bool = False  # New field to indicate if user has a password set

class UserInDB(User):
    hashed_password: Optional[str] = None

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: Optional[str] = None  # Optional if setting password for the first time
    new_password: str

class AdminKeyRequest(BaseModel):
    """Schema for admin key verification."""
    admin_key: str
