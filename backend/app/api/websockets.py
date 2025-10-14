"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: dict[UUID, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: UUID) -> None:
        """Connect a client to a conversation's WebSocket.

        Args:
            websocket: WebSocket connection
            conversation_id: ID of the conversation
        """
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: UUID) -> None:
        """Disconnect a client from a conversation's WebSocket.

        Args:
            websocket: WebSocket connection
            conversation_id: ID of the conversation
        """
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def broadcast_to_conversation(
        self, conversation_id: UUID, message: dict[str, Any]
    ) -> None:
        """Broadcast a message to all clients connected to a conversation.

        Args:
            conversation_id: ID of the conversation
            message: Message to broadcast
        """
        if conversation_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, conversation_id)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/logs/{conversation_id}")
async def websocket_logs(websocket: WebSocket, conversation_id: UUID) -> None:
    """WebSocket endpoint for real-time log streaming.

    Args:
        websocket: WebSocket connection
        conversation_id: ID of the conversation to stream logs from
    """
    await manager.connect(websocket, conversation_id)
    db: Session = SessionLocal()

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "conversation_id": str(conversation_id),
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (e.g., filter updates)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "subscribe":
                    # Client wants to subscribe to updates
                    await websocket.send_json(
                        {"type": "subscribed", "conversation_id": str(conversation_id)}
                    )

            except asyncio.TimeoutError:
                # Send periodic ping to keep connection alive
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        # Log error and disconnect
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, conversation_id)
    finally:
        db.close()


@router.websocket("/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: UUID) -> None:
    """WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        conversation_id: ID of the conversation
    """
    await manager.connect(websocket, conversation_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "conversation_id": str(conversation_id),
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "message":
                    # Broadcast message to all connected clients
                    await manager.broadcast_to_conversation(
                        conversation_id,
                        {
                            "type": "message",
                            "content": message.get("content"),
                            "role": message.get("role"),
                            "timestamp": message.get("timestamp"),
                        },
                    )

            except asyncio.TimeoutError:
                # Send periodic ping to keep connection alive
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, conversation_id)


# Utility function to broadcast logs from service layer
async def broadcast_log(conversation_id: UUID, log_data: dict[str, Any]) -> None:
    """Broadcast a log entry to all connected clients.

    Args:
        conversation_id: ID of the conversation
        log_data: Log data to broadcast
    """
    await manager.broadcast_to_conversation(
        conversation_id, {"type": "log", "data": log_data}
    )
