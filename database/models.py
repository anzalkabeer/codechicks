"""
Beanie Document Models

Defines MongoDB document schemas using Beanie ODM.
These models extend Pydantic BaseModel and provide MongoDB integration.
"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional
from enum import Enum
from utils.timezone import now_ist


class UserRole(str, Enum):
    """User role enum for RBAC."""
    USER = "user"
    ADMIN = "admin"


class UserDocument(Document):
    """
    User document model for MongoDB.
    
    Stores user authentication data and profile information.
    """
    # Auth fields
    email: Indexed(str, unique=True)
    hashed_password: str
    disabled: bool = False
    
    # Role-based access control
    role: UserRole = UserRole.USER
    
    # Profile fields - sparse index allows multiple None values
    username: Optional[Indexed(str, unique=True, sparse=True)] = None
    display_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Status flags
    profile_complete: bool = False
    
    # Timestamps (IST)
    created_at: datetime = Field(default_factory=now_ist)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "users"
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "$pbkdf2-sha256$...",
                "disabled": False,
                "role": "user",
                "username": "cooluser",
                "display_name": "Cool User",
                "profile_complete": True
            }
        }


class MessageDocument(Document):
    """
    Chat message document model for MongoDB.
    
    Stores chat messages with sender info, content, and metadata.
    """
    sender_id: Indexed(str)  # User email
    sender_name: Optional[str] = None
    content: str
    timestamp: Indexed(datetime, index_type=-1) = Field(default_factory=now_ist)
    room_id: Indexed(str) = "global"
    message_type: str = "text"  # text, system, etc.
    is_deleted: bool = False
    
    # Reply functionality
    reply_to_id: Optional[str] = None
    reply_to_username: Optional[str] = None
    reply_to_content: Optional[str] = None

    
    class Settings:
        name = "messages"
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "user@example.com",
                "sender_name": "user",
                "content": "Hello, World!",
                "room_id": "global",
                "message_type": "text"
            }
        }
