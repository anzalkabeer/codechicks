"""
Chat Router - Provides global chat functionality.

This module implements endpoints for the global chat feature,
with CRUD operations for messages using MongoDB via Beanie.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime
from typing import Optional

from schemas.chat import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageListResponse,
    ChatStatusResponse
)
from database.models import MessageDocument
from auth.router import get_current_user
from auth.schemas import User
from beanie import PydanticObjectId

router = APIRouter(prefix="/api/chat", tags=["chat"])


# --- Helper Functions ---
def message_to_response(msg: MessageDocument) -> MessageResponse:
    """Convert MessageDocument to MessageResponse with IST timestamp."""
    from utils.timezone import utc_to_ist
    
    # MongoDB stores dates in UTC, convert back to IST for display
    ist_timestamp = utc_to_ist(msg.timestamp) if msg.timestamp else msg.timestamp
    
    return MessageResponse(
        id=str(msg.id),
        sender_id=msg.sender_id,
        sender_name=msg.sender_name,
        content=msg.content,
        timestamp=ist_timestamp,
        room_id=msg.room_id,
        message_type=msg.message_type,
        reply_to_id=msg.reply_to_id,
        reply_to_username=msg.reply_to_username,
        reply_to_content=msg.reply_to_content
    )


# --- Endpoints ---
@router.get("/messages", response_model=MessageListResponse)
async def get_messages(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Messages per page"),
    room_id: str = Query("global", description="Chat room ID")
):
    """
    Retrieve paginated chat message history.

    - **page**: Page number (1-indexed)
    - **page_size**: Number of messages per page (max 100)
    - **room_id**: Filter by chat room (default: 'global')

    Protected endpoint - requires valid JWT token.
    """
    # Query MongoDB for messages
    query = MessageDocument.find(
        MessageDocument.room_id == room_id,
        MessageDocument.is_deleted == False
    ).sort(-MessageDocument.timestamp)
    
    # Get total count
    total_count = await query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    messages = await query.skip(skip).limit(page_size).to_list()

    return MessageListResponse(
        messages=[message_to_response(m) for m in messages],
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_more=(skip + page_size) < total_count
    )


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Send a new chat message.

    The message will be associated with the authenticated user.
    Supports replying to another message.

    Protected endpoint - requires valid JWT token.
    """
    # Use display_name, fallback to username, then email prefix
    sender_display = (
        current_user.display_name
        or current_user.username
        or current_user.email.split("@")[0]
    )
    
    new_message = MessageDocument(
        sender_id=current_user.email,
        sender_name=sender_display,
        content=message.content,
        room_id=message.room_id,
        message_type="text",
        reply_to_id=message.reply_to_id,
        reply_to_username=message.reply_to_username,
        reply_to_content=message.reply_to_content
    )

    await new_message.insert()

    return message_to_response(new_message)


@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific message by ID.

    Protected endpoint - requires valid JWT token.
    """
    try:
        msg = await MessageDocument.get(PydanticObjectId(message_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if not msg or msg.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return message_to_response(msg)


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    update_data: MessageUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a message content.
    
    Protected endpoint - requires valid JWT token.
    """
    try:
        msg = await MessageDocument.get(PydanticObjectId(message_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if not msg or msg.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
        
    # Only allow sender to edit their own messages
    if msg.sender_id != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own messages"
        )

    if update_data.content:
        msg.content = update_data.content
        msg.updated_at = datetime.now()
        await msg.save()
        
    return message_to_response(msg)


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a message (only by the sender).

    Protected endpoint - requires valid JWT token.
    """
    try:
        msg = await MessageDocument.get(PydanticObjectId(message_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if not msg or msg.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Only allow sender to delete their own messages
    if msg.sender_id != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages"
        )

    msg.is_deleted = True
    await msg.save()
    return None


@router.get("/status", response_model=ChatStatusResponse)
async def get_chat_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current chat system status.

    Returns information about online users, message count,
    and WebSocket readiness.

    Protected endpoint - requires valid JWT token.
    """
    total_messages = await MessageDocument.find(
        MessageDocument.is_deleted == False
    ).count()

    return ChatStatusResponse(
        online_users=0,  # TODO: Implement with WebSocket connections
        total_messages=total_messages,
        websocket_ready=False  # TODO: Set to True when WebSockets implemented
    )
