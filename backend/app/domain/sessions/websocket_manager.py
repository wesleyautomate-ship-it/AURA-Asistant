"""
WebSocket Manager for Phase 4B Real-time Notifications

This module manages WebSocket connections for real-time AI insights, notifications,
and live alerts across the Dubai Real Estate RAG System.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy import text
from database_manager import get_db_connection

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages"""

    def __init__(self):
        self.active_connections: Dict[
            int, List[WebSocket]
        ] = {}  # user_id -> [websockets]
        self.connection_metadata: Dict[
            str, Dict[str, Any]
        ] = {}  # connection_id -> metadata
        self.user_connections: Dict[
            int, Set[str]
        ] = {}  # user_id -> set of connection_ids

    async def connect(
        self, websocket: WebSocket, user_id: int, connection_id: str = None
    ):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()

            if not connection_id:
                connection_id = str(uuid.uuid4())

            # Store connection metadata
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "websocket": websocket,
                "connected_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow(),
                "ip_address": websocket.client.host
                if hasattr(websocket, "client")
                else None,
                "user_agent": websocket.headers.get("user-agent", "Unknown"),
            }

            # Add to active connections
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)

            # Track user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

            # Store connection in database
            await self._store_connection(user_id, connection_id, websocket)

            # Send welcome message
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "connection_established",
                        "connection_id": connection_id,
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Connected to Phase 4B AI Insights",
                    }
                )
            )

            logger.info(
                f"WebSocket connected: user_id={user_id}, connection_id={connection_id}"
            )

            return connection_id

        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
            raise

    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        try:
            if connection_id in self.connection_metadata:
                metadata = self.connection_metadata[connection_id]
                user_id = metadata["user_id"]
                websocket = metadata["websocket"]

                # Remove from active connections
                if user_id in self.active_connections:
                    if websocket in self.active_connections[user_id]:
                        self.active_connections[user_id].remove(websocket)

                    # Clean up empty user connections
                    if not self.active_connections[user_id]:
                        del self.active_connections[user_id]

                # Remove from user connections tracking
                if user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]

                # Update database
                await self._update_connection_status(connection_id, "disconnected")

                # Clean up metadata
                del self.connection_metadata[connection_id]

                logger.info(f"WebSocket disconnected: connection_id={connection_id}")

        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            disconnected_websockets = []

            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    disconnected_websockets.append(websocket)

            # Clean up disconnected websockets
            for websocket in disconnected_websockets:
                if user_id in self.active_connections:
                    self.active_connections[user_id].remove(websocket)

    async def broadcast_to_agents(self, message: dict, exclude_user_id: int = None):
        """Broadcast a message to all connected agents"""
        for user_id in list(self.active_connections.keys()):
            if exclude_user_id and user_id == exclude_user_id:
                continue

            await self.send_personal_message(message, user_id)

    async def send_notification(self, notification: dict, user_id: int):
        """Send a smart notification to a specific user"""
        message = {
            "type": "notification",
            "notification": notification,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_personal_message(message, user_id)

        # Log the notification
        await self._log_notification_delivery(notification["id"], user_id, "websocket")

    async def send_market_alert(self, alert: dict, target_users: List[int] = None):
        """Send market alert to target users or all agents"""
        message = {
            "type": "market_alert",
            "alert": alert,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if target_users:
            for user_id in target_users:
                await self.send_personal_message(message, user_id)
        else:
            await self.broadcast_to_agents(message)

    async def send_performance_update(self, update: dict, user_id: int):
        """Send performance update to a specific user"""
        message = {
            "type": "performance_update",
            "update": update,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_personal_message(message, user_id)

    async def send_report_ready(self, report: dict, user_id: int):
        """Send report ready notification"""
        message = {
            "type": "report_ready",
            "report": report,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_personal_message(message, user_id)

    async def handle_websocket_message(
        self, websocket: WebSocket, message: dict, connection_id: str
    ):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")

            if message_type == "ping":
                # Respond to ping with pong
                await websocket.send_text(
                    json.dumps(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )
                )

                # Update heartbeat
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id][
                        "last_heartbeat"
                    ] = datetime.utcnow()
                    await self._update_heartbeat(connection_id)

            elif message_type == "mark_read":
                # Mark notification as read
                notification_id = message.get("notification_id")
                if notification_id:
                    await self._mark_notification_read(notification_id, connection_id)

            elif message_type == "mark_all_read":
                # Mark all notifications as read for user
                if connection_id in self.connection_metadata:
                    user_id = self.connection_metadata[connection_id]["user_id"]
                    await self._mark_all_notifications_read(user_id)

            elif message_type == "dismiss":
                # Dismiss notification
                notification_id = message.get("notification_id")
                if notification_id:
                    await self._dismiss_notification(notification_id, connection_id)

            elif message_type == "subscribe":
                # Subscribe to specific notification types
                notification_types = message.get("notification_types", [])
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id][
                        "subscribed_types"
                    ] = notification_types

            elif message_type == "unsubscribe":
                # Unsubscribe from specific notification types
                notification_types = message.get("notification_types", [])
                if connection_id in self.connection_metadata:
                    current_types = self.connection_metadata[connection_id].get(
                        "subscribed_types", []
                    )
                    for ntype in notification_types:
                        if ntype in current_types:
                            current_types.remove(ntype)

            else:
                logger.warning(f"Unknown WebSocket message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def get_connection_stats(self) -> dict:
        """Get current connection statistics"""
        total_connections = sum(
            len(connections) for connections in self.active_connections.values()
        )
        total_users = len(self.active_connections)

        return {
            "total_connections": total_connections,
            "total_users": total_users,
            "active_connections": self.active_connections,
            "connection_metadata": len(self.connection_metadata),
        }

    async def cleanup_stale_connections(self):
        """Clean up stale connections that haven't sent heartbeats"""
        try:
            current_time = datetime.utcnow()
            stale_connections = []

            for connection_id, metadata in self.connection_metadata.items():
                last_heartbeat = metadata["last_heartbeat"]
                if current_time - last_heartbeat > timedelta(
                    minutes=5
                ):  # 5 minutes timeout
                    stale_connections.append(connection_id)

            for connection_id in stale_connections:
                logger.warning(f"Cleaning up stale connection: {connection_id}")
                await self.disconnect(connection_id)

        except Exception as e:
            logger.error(f"Error cleaning up stale connections: {e}")

    # Database operations
    async def _store_connection(
        self, user_id: int, connection_id: str, websocket: WebSocket
    ):
        """Store WebSocket connection in database"""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO ml_websocket_connections (
                        connection_id, user_id, connection_status, 
                        ip_address, user_agent, connection_metadata
                    ) VALUES (
                        :connection_id, :user_id, 'connected',
                        :ip_address, :user_agent, :metadata
                    )
                """
                    ),
                    {
                        "connection_id": connection_id,
                        "user_id": user_id,
                        "ip_address": websocket.client.host
                        if hasattr(websocket, "client")
                        else None,
                        "user_agent": websocket.headers.get("user-agent", "Unknown"),
                        "metadata": json.dumps(
                            {
                                "connected_at": datetime.utcnow().isoformat(),
                                "protocol": "websocket",
                            }
                        ),
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store connection in database: {e}")

    async def _update_connection_status(self, connection_id: str, status: str):
        """Update connection status in database"""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    UPDATE ml_websocket_connections 
                    SET connection_status = :status, disconnected_at = :disconnected_at
                    WHERE connection_id = :connection_id
                """
                    ),
                    {
                        "status": status,
                        "disconnected_at": datetime.utcnow()
                        if status == "disconnected"
                        else None,
                        "connection_id": connection_id,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to update connection status: {e}")

    async def _update_heartbeat(self, connection_id: str):
        """Update connection heartbeat in database"""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    UPDATE ml_websocket_connections 
                    SET last_heartbeat = :heartbeat
                    WHERE connection_id = :connection_id
                """
                    ),
                    {"heartbeat": datetime.utcnow(), "connection_id": connection_id},
                )

        except Exception as e:
            logger.error(f"Failed to update heartbeat: {e}")

    async def _mark_notification_read(self, notification_id: str, connection_id: str):
        """Mark notification as read"""
        try:
            if connection_id in self.connection_metadata:
                user_id = self.connection_metadata[connection_id]["user_id"]

                with get_db_connection() as conn:
                    conn.execute(
                        text(
                            """
                        UPDATE ml_smart_notifications 
                        SET read = TRUE, read_at = :read_at
                        WHERE notification_id = :notification_id AND user_id = :user_id
                    """
                        ),
                        {
                            "read_at": datetime.utcnow(),
                            "notification_id": notification_id,
                            "user_id": user_id,
                        },
                    )

        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")

    async def _mark_all_notifications_read(self, user_id: int):
        """Mark all notifications as read for a user"""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    UPDATE ml_smart_notifications 
                    SET read = TRUE, read_at = :read_at
                    WHERE user_id = :user_id AND read = FALSE
                """
                    ),
                    {"read_at": datetime.utcnow(), "user_id": user_id},
                )

        except Exception as e:
            logger.error(f"Failed to mark all notifications as read: {e}")

    async def _dismiss_notification(self, notification_id: str, connection_id: str):
        """Dismiss notification"""
        try:
            if connection_id in self.connection_metadata:
                user_id = self.connection_metadata[connection_id]["user_id"]

                with get_db_connection() as conn:
                    conn.execute(
                        text(
                            """
                        UPDATE ml_smart_notifications 
                        SET dismissed = TRUE, dismissed_at = :dismissed_at
                        WHERE notification_id = :notification_id AND user_id = :user_id
                    """
                        ),
                        {
                            "dismissed_at": datetime.utcnow(),
                            "notification_id": notification_id,
                            "user_id": user_id,
                        },
                    )

        except Exception as e:
            logger.error(f"Failed to dismiss notification: {e}")

    async def _log_notification_delivery(
        self, notification_id: str, user_id: int, delivery_method: str
    ):
        """Log notification delivery for analytics"""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO ml_insights_log (
                        insight_type, user_id, insight_data
                    ) VALUES (
                        'notification_delivery', :user_id, :data
                    )
                """
                    ),
                    {
                        "user_id": user_id,
                        "data": json.dumps(
                            {
                                "notification_id": notification_id,
                                "delivery_method": delivery_method,
                                "delivered_at": datetime.utcnow().isoformat(),
                            }
                        ),
                    },
                )

        except Exception as e:
            logger.error(f"Failed to log notification delivery: {e}")


# Global connection manager instance
connection_manager = ConnectionManager()

# Background task for cleanup
async def cleanup_task():
    """Background task to clean up stale connections"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await connection_manager.cleanup_stale_connections()
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")


# Start cleanup task
def start_cleanup_task():
    """Start the background cleanup task"""
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_task())
