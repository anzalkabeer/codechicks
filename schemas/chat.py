"""
Chat Schemas - Pydantic models for chat endpoints.

This module defines request/response schemas for the chat API,
including message creation, updates, and paginated responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# --- Request Schemas ---
class MessageCreate(BaseModel):
    """Schema for creating a new chat message."""
    content: str = Field(..., min_length=1, max_length=2000)
    room_id: str = "global"


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: Optional[str] = Field(None, min_length=1, max_length=2000)


# --- Response Schemas ---
class MessageResponse(BaseModel):
    """Schema for single message response."""
    id: str
    sender_id: str
    sender_name: Optional[str]
    content: str
    timestamp: datetime
    room_id: str
    message_type: str
    
    # Reply info
    reply_to_id: Optional[str] = None
    reply_to_username: Optional[str] = None
    reply_to_content: Optional[str] = None


class MessageListResponse(BaseModel):
    """Paginated list of messages."""
    messages: List[MessageResponse]
    total_count: int
    page: int
    page_size: int
    has_more: bool


class ChatStatusResponse(BaseModel):
    """Chat system status."""
    online_users: int = 0
    total_messages: int = 0
    websocket_ready: bool = False  # TODO: Future WebSocket integration
