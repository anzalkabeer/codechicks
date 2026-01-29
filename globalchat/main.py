"""
Global Chat WebSocket Module

Implements a real-time global chat room using WebSockets with the following logic:
1. Connection Logic - WebSocket handshake (accept)
2. Storage Logic - Connection Manager to track active connections
3. Listening Loop - Async while True to receive messages
4. Broadcasting Logic - Send to all connected clients
5. Disconnect Logic - Cleanup on connection close
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
from datetime import datetime
from database.models import MessageDocument
from beanie import PydanticObjectId
from utils.timezone import now_ist
from fastapi import Query
from jose import jwt, JWTError
from auth.utils import SECRET_KEY, ALGORITHM
from auth.schemas import TokenData
from database.models import UserDocument

# ============================================================
# 2. THE STORAGE LOGIC (Connection Manager)
# ============================================================
class ConnectionManager:
    """
    Manages all active WebSocket connections.
    """
    
    def __init__(self):
        # Global list of all active WebSocket connections
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Adds the WebSocket connection to our registry (Assume already accepted)."""
        # await websocket.accept()  <-- Moved to endpoint
        self.active_connections.append(websocket)
        print(f"✅ New connection! Total active: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Removes the websocket from active connections."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔌 Connection closed. Total active: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        """Iterates through all active connections and sends the message."""
        connections_to_remove = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"⚠️ Failed to send to a connection: {e}")
                connections_to_remove.append(connection)
        
        for conn in connections_to_remove:
            self.disconnect(conn)

# Create a single global instance of the connection manager
manager = ConnectionManager()

# Create router for the chat endpoints
router = APIRouter(prefix="/ws", tags=["websocket"])


# ============================================================
# WEBSOCKET ENDPOINT - THE MAIN CHAT ROOM
# ============================================================
@router.websocket("/chat")
async def websocket_chat_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    Main WebSocket endpoint for the global chat room.
    Requires 'token' query parameter for authentication.
    """
    # 1. CONNECTION & AUTH CHECK
    await websocket.accept() # User requested to accept before auth checks
    
    if not token:
        await websocket.close(code=4003, reason="Authentication required")
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            await websocket.close(code=4003, reason="Invalid token")
            return
    except JWTError:
        await websocket.close(code=4003, reason="Invalid token")
        return
        
    # Get user from DB
    user = await UserDocument.find_one(UserDocument.email == email)
    if not user:
        await websocket.close(code=4003, reason="User not found")
        return
        
    # Validated Identity
    current_user_email = user.email
    current_user_name = user.display_name or user.username or user.email.split("@")[0]

    # 2. CONNECTION
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for message
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                action_type = message_data.get("type", "message")
                
                # Metadata - FORCED from authenticated user (ignore client claims)
                username = current_user_name
                sender_id = current_user_email
                
                # --- CASE 1: NEW MESSAGE ---
                if action_type == "message":
                    content = message_data.get("message", "")
                    
                    # Reply data
                    reply_to_id = message_data.get("reply_to_id")
                    reply_to_username = message_data.get("reply_to_username")
                    reply_to_content = message_data.get("reply_to_content")

                    if content:
                        # 1. Save to DB
                        new_msg = MessageDocument(
                            sender_id=sender_id,
                            sender_name=username,
                            content=content,
                            room_id="global",
                            message_type="text",
                            timestamp=now_ist(),
                            reply_to_id=reply_to_id,
                            reply_to_username=reply_to_username,
                            reply_to_content=reply_to_content
                        )
                        await new_msg.insert()
                        
                        # 2. Broadcast with ID & Reply Info
                        await manager.broadcast(json.dumps({
                            "type": "message",
                            "id": str(new_msg.id),
                            "username": username,
                            "sender_id": sender_id,
                            "message": content,
                            "timestamp": new_msg.timestamp.isoformat(),
                            "reply_to_id": reply_to_id,
                            "reply_to_username": reply_to_username,
                            "reply_to_content": reply_to_content
                        }))
                
                # --- CASE 2: EDIT MESSAGE ---
                elif action_type == "edit":
                    msg_id = message_data.get("id")
                    new_content = message_data.get("message")
                    
                    if msg_id and new_content:
                        # 1. Find message
                        msg = await MessageDocument.get(PydanticObjectId(msg_id))
                        
                        # 2. Verify ownership and update
                        if msg and msg.sender_id == sender_id and not msg.is_deleted:
                            msg.content = new_content
                            await msg.save()
                            
                            # 3. Broadcast update
                            await manager.broadcast(json.dumps({
                                "type": "edit",
                                "id": str(msg.id),
                                "message": new_content
                            }))
                            
                # --- CASE 3: DELETE MESSAGE ---
                elif action_type == "delete":
                    msg_id = message_data.get("id")
                    
                    if msg_id:
                        # 1. Find message
                        msg = await MessageDocument.get(PydanticObjectId(msg_id))
                        
                        # 2. Verify ownership and delete
                        if msg and msg.sender_id == sender_id:
                            msg.is_deleted = True
                            await msg.save()
                            
                            # 3. Broadcast deletion
                            await manager.broadcast(json.dumps({
                                "type": "delete",
                                "id": str(msg.id)
                            }))

            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"❌ Error processing message: {e}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)
