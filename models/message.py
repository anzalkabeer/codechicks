"""
Message Model - Database model for chat messages.

This module defines the data structure for chat messages,
compatible with both in-memory storage and future MongoDB integration.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4


class MessageInDB(BaseModel):
    """Database model for chat messages."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    sender_id: str  # User email
    sender_name: Optional[str] = None
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    room_id: str = "global"  # For future room support
    message_type: str = "text"  # text, system, etc.
    is_deleted: bool = False
