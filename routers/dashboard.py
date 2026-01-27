"""
Dashboard Router - Provides dashboard data endpoints.

This module implements endpoints for the dashboard feature,
returning aggregated statistics from MongoDB.
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta

from schemas.dashboard import (
    DashboardResponse,
    UserStats,
    ActivitySummary,
    GlobalMetrics,
)
from database.models import UserDocument, MessageDocument
from auth.router import get_current_user
from auth.schemas import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# --- Database Query Functions ---
async def get_user_stats() -> UserStats:
    """Get user statistics from MongoDB."""
    total_users = await UserDocument.count()
    
    # Count users created in the last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_users_today = await UserDocument.find(
        UserDocument.created_at >= yesterday
    ).count()
    
    # Active users = users who are not disabled
    active_users = await UserDocument.find(
        UserDocument.disabled == False
    ).count()
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        new_users_today=new_users_today
    )


async def get_activity_summary() -> ActivitySummary:
    """Get activity summary from MongoDB."""
    # TODO: Implement session tracking
    return ActivitySummary(
        total_sessions=0,
        total_time_seconds=0,
        average_session_minutes=0.0
    )


async def get_global_metrics() -> GlobalMetrics:
    """Get global platform metrics from MongoDB."""
    total_messages = await MessageDocument.find(
        MessageDocument.is_deleted == False
    ).count()
    
    return GlobalMetrics(
        total_timer_starts=0,  # TODO: Track timer usage
        total_messages_sent=total_messages,
        uptime_days=0  # TODO: Calculate from startup time
    )


# --- Endpoints ---
@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Retrieve dashboard data for the authenticated user.

    Returns aggregated statistics including:
    - User stats (total, active, new users)
    - Activity summary (sessions, time spent)
    - Global platform metrics

    Protected endpoint - requires valid JWT token.
    """
    return DashboardResponse(
        user_stats=await get_user_stats(),
        activity_summary=await get_activity_summary(),
        global_metrics=await get_global_metrics(),
        last_updated=datetime.utcnow()
    )


@router.get("/me")
async def get_user_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard data specific to the current user.
    """
    # Count user's messages
    user_message_count = await MessageDocument.find(
        MessageDocument.sender_id == current_user.email,
        MessageDocument.is_deleted == False
    ).count()
    
    return {
        "user_email": current_user.email,
        "total_messages_sent": user_message_count,
        "joined_at": None  # TODO: Add to user query
    }
