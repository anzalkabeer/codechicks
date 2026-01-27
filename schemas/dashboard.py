"""
Dashboard Schemas - Pydantic models for dashboard endpoints.

This module defines request/response schemas for the dashboard API,
including user statistics, activity summaries, and pagination.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# --- Nested Response Models ---
class UserStats(BaseModel):
    """User statistics for dashboard."""
    total_users: int = 0
    active_users: int = 0
    new_users_today: int = 0


class ActivitySummary(BaseModel):
    """Recent activity summary."""
    total_sessions: int = 0
    total_time_seconds: int = 0
    average_session_minutes: float = 0.0


class GlobalMetrics(BaseModel):
    """Global platform metrics."""
    total_timer_starts: int = 0
    total_messages_sent: int = 0
    uptime_days: int = 0


# --- Main Response Model ---
class DashboardResponse(BaseModel):
    """Complete dashboard data response."""
    user_stats: UserStats
    activity_summary: ActivitySummary
    global_metrics: GlobalMetrics
    last_updated: datetime


# --- Pagination Models ---
class PaginationParams(BaseModel):
    """Common pagination parameters."""
    page: int = 1
    page_size: int = 10


class PaginatedResponse(BaseModel):
    """Base for paginated responses."""
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
