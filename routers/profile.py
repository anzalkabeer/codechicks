"""
Profile Router - User profile management endpoints.

Provides CRUD operations for user profiles, onboarding flow, and password change.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from pydantic import BaseModel

from schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    OnboardingData,
    OnboardingResponse
)
from database.models import UserDocument
from auth.router import get_current_user
from auth.schemas import User, PasswordChange
from auth.utils import verify_password, get_password_hash
from utils.timezone import now_ist

router = APIRouter(prefix="/api/profile", tags=["profile"])


def user_to_profile_response(user: UserDocument) -> ProfileResponse:
    """Convert UserDocument to ProfileResponse."""
    return ProfileResponse(
        email=user.email,
        username=user.username,
        display_name=user.display_name,
        age=user.age,
        bio=user.bio,
        avatar_url=user.avatar_url,
        profile_complete=user.profile_complete,
        created_at=user.created_at
    )


@router.get("", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    
    Protected endpoint - requires valid JWT token.
    """
    user = await UserDocument.find_one(UserDocument.email == current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_to_profile_response(user)


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile fields.
    
    Protected endpoint - requires valid JWT token.
    """
    user = await UserDocument.find_one(UserDocument.email == current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check username uniqueness if being updated
    if updates.username and updates.username != user.username:
        existing = await UserDocument.find_one(UserDocument.username == updates.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = now_ist()
    
    try:
        await user.save()
    except Exception as e:
        # Handle duplicate key error (race condition fallback)
        if "duplicate key" in str(e).lower() or "E11000" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        raise
    
    return user_to_profile_response(user)


@router.post("/complete", response_model=OnboardingResponse)
async def complete_onboarding(
    data: OnboardingData,
    current_user: User = Depends(get_current_user)
):
    """
    Complete user onboarding.
    
    Sets profile fields and marks profile as complete.
    Redirects to dashboard after success.
    
    Protected endpoint - requires valid JWT token.
    """
    user = await UserDocument.find_one(UserDocument.email == current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check username uniqueness
    existing = await UserDocument.find_one(UserDocument.username == data.username)
    if existing and existing.email != user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Update profile
    user.username = data.username
    user.display_name = data.display_name or data.username
    user.age = data.age
    user.bio = data.bio
    user.profile_complete = True
    user.updated_at = now_ist()
    
    await user.save()
    
    return OnboardingResponse(
        message="Profile completed successfully!",
        profile_complete=True,
        redirect_to="/dashboard"
    )


@router.get("/status")
async def get_profile_status(current_user: User = Depends(get_current_user)):
    """
    Check if user profile is complete (for redirect logic).
    
    Protected endpoint - requires valid JWT token.
    """
    user = await UserDocument.find_one(UserDocument.email == current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "profile_complete": user.profile_complete,
        "redirect_to": "/dashboard" if user.profile_complete else "/onboarding"
    }


@router.post("/password")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """
    Change user password.
    
    Requires current password verification.
    Password must be at least 8 characters.
    
    Protected endpoint - requires valid JWT token.
    """
    user = await UserDocument.find_one(UserDocument.email == current_user.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password ONLY if user has one
    if user.hashed_password:
        if not data.current_password:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required"
            )
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
    # If no hashed_password (OAuth user), we skip verification (they are setting it for the first time)
    
    # Validate new password
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Hash and save new password
    user.hashed_password = get_password_hash(data.new_password)
    user.updated_at = now_ist()
    await user.save()
    
    return {"message": "Password changed successfully"}
