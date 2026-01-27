"""
Profile Schemas

Pydantic models for user profile operations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    """User profile data returned from API."""
    email: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_complete: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "cooluser",
                "display_name": "Cool User",
                "age": 25,
                "profile_complete": True
            }
        }


class ProfileUpdate(BaseModel):
    """Fields that can be updated via PATCH /api/profile."""
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    display_name: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=13, le=120)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class OnboardingData(BaseModel):
    """Data submitted during onboarding."""
    username: str = Field(..., min_length=3, max_length=30)
    display_name: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=13, le=120)
    bio: Optional[str] = Field(None, max_length=500)


class OnboardingResponse(BaseModel):
    """Response after completing onboarding."""
    message: str
    profile_complete: bool
    redirect_to: str
