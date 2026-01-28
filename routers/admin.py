"""
Admin Router - Admin-only endpoints for managing the application.

Provides stats, user management, and moderation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from auth.router import get_current_admin
from auth.schemas import User
from database.models import UserDocument, MessageDocument, UserRole

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_admin_stats(current_user: User = Depends(get_current_admin)):
    """
    Get admin dashboard statistics.
    
    Admin-only endpoint.
    """
    # Count all users
    total_users = await UserDocument.count()
    
    # Count active users (not disabled)
    active_users = await UserDocument.find(
        UserDocument.disabled == False
    ).count()
    
    # Count admins
    admin_count = await UserDocument.find(
        UserDocument.role == UserRole.ADMIN
    ).count()
    
    # Count total messages
    total_messages = await MessageDocument.count()
    
    # Count new users today
    from datetime import datetime, timedelta
    from utils.timezone import now_ist
    
    today_start = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)
    new_users_today = await UserDocument.find(
        UserDocument.created_at >= today_start
    ).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_count": admin_count,
        "total_messages": total_messages,
        "new_users_today": new_users_today
    }


@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_admin)
):
    """
    Get list of all users.
    
    Admin-only endpoint.
    """
    users = await UserDocument.find_all().skip(skip).limit(limit).to_list()
    
    return [
        {
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role.value,
            "disabled": user.disabled,
            "profile_complete": user.profile_complete,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]


@router.patch("/users/{email}/role")
async def update_user_role(
    email: str,
    role: str,
    current_user: User = Depends(get_current_admin)
):
    """
    Update a user's role.
    
    Admin-only endpoint.
    """
    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'user' or 'admin'"
        )
    
    user = await UserDocument.find_one(UserDocument.email == email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = UserRole(role)
    await user.save()
    
    return {"message": f"User role updated to {role}", "email": email, "role": role}


@router.patch("/users/{email}/disable")
async def toggle_user_disabled(
    email: str,
    current_user: User = Depends(get_current_admin)
):
    """
    Toggle a user's disabled status.
    
    Admin-only endpoint.
    """
    user = await UserDocument.find_one(UserDocument.email == email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from disabling themselves
    if user.email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )
    
    user.disabled = not user.disabled
    await user.save()
    
    status_text = "disabled" if user.disabled else "enabled"
    return {"message": f"User {status_text}", "email": email, "disabled": user.disabled}


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_admin)
):
    """
    Delete a chat message (moderation).
    
    Admin-only endpoint.
    """
    from beanie import PydanticObjectId
    
    try:
        message = await MessageDocument.get(PydanticObjectId(message_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message ID"
        )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    await message.delete()
    
    return {"message": "Message deleted", "message_id": message_id}
