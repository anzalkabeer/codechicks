from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    email: str
    disabled: Optional[bool] = None
    username: Optional[str] = None
    display_name: Optional[str] = None

class UserInDB(User):
    hashed_password: str

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
