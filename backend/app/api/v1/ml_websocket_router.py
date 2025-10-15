"""
WebSocket Router for Phase 4B ML Insights

This module provides WebSocket endpoints for real-time AI insights, notifications,
and live alerts in the Dubai Real Estate RAG System.
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
from auth.middleware import get_current_user_websocket
from websocket_manager import connection_manager

logger = logging.getLogger(__name__)

# Create WebSocket router
ml_websocket_router = APIRouter(
    prefix="/ws/ml",
    tags=["ML WebSocket"],
    responses={404: {"description": "Not found"}},
)


@ml_websocket_router.websocket("/notifications/{user_id}")
async def websocket_notifications_endpoint(
    websocket: WebSocket, user_id: int, token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time ML notifications

    This endpoint establishes a persistent connection for:
    - Smart notifications
    - Market alerts
    - Performance updates
    - Report ready notifications
    - AI insights
    """
    try:
        # Validate user authentication
        if not token:
            await websocket.close(code=4001, reason="Authentication token required")
            return

        # Verify user token and get user info
        try:
            user = await get_current_user_websocket(token)
            if user["id"] != user_id:
                await websocket.close(code=4003, reason="Unauthorized access")
                return
        except Exception as e:
            logger.error(f"Authentication failed for user {user_id}: {e}")
            await websocket.close(code=4001, reason="Authentication failed")
            return

        # Establish WebSocket connection
        connection_id = await connection_manager.connect(websocket, user_id)

        try:
            # Main message handling loop
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    await connection_manager.handle_websocket_message(
                        websocket, message, connection_id
                    )
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from user {user_id}")
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Invalid JSON format",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )
                except Exception as e:
                    logger.error(f"Error processing message from user {user_id}: {e}")
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Internal server error",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket for user {user_id}: {e}")
        finally:
            # Clean up connection
            await connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@ml_websocket_router.websocket("/market-alerts")
async def websocket_market_alerts_endpoint(
    websocket: WebSocket, token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time market alerts

    This endpoint provides live market intelligence updates including:
    - Price changes
    - New listings
    - Market trends
    - Investment opportunities
    """
    try:
        # Validate authentication
        if not token:
            await websocket.close(code=4001, reason="Authentication token required")
            return

        # Verify user token
        try:
            user = await get_current_user_websocket(token)
        except Exception as e:
            logger.error(f"Authentication failed for market alerts: {e}")
            await websocket.close(code=4001, reason="Authentication failed")
            return

        # Establish connection for market alerts
        connection_id = await connection_manager.connect(websocket, user["id"])

        try:
            # Subscribe to market alerts
            await connection_manager.handle_websocket_message(
                websocket,
                {"type": "subscribe", "notification_types": ["market_alert"]},
                connection_id,
            )

            # Send initial market summary
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "market_summary",
                        "message": "Subscribed to market alerts",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )

            # Message handling loop
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    await connection_manager.handle_websocket_message(
                        websocket, message, connection_id
                    )
                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Invalid JSON format",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

        except WebSocketDisconnect:
            logger.info(f"Market alerts WebSocket disconnected for user {user['id']}")
        finally:
            await connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"Failed to establish market alerts WebSocket: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@ml_websocket_router.websocket("/performance-updates/{user_id}")
async def websocket_performance_updates_endpoint(
    websocket: WebSocket, user_id: int, token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time performance updates

    This endpoint provides live performance analytics including:
    - Goal progress updates
    - Performance metrics
    - AI recommendations
    - Achievement notifications
    """
    try:
        # Validate authentication
        if not token:
            await websocket.close(code=4001, reason="Authentication token required")
            return

        # Verify user token and access
        try:
            user = await get_current_user_websocket(token)
            if user["id"] != user_id:
                await websocket.close(code=4003, reason="Unauthorized access")
                return
        except Exception as e:
            logger.error(
                f"Authentication failed for performance updates user {user_id}: {e}"
            )
            await websocket.close(code=4001, reason="Authentication failed")
            return

        # Establish connection
        connection_id = await connection_manager.connect(websocket, user_id)

        try:
            # Subscribe to performance updates
            await connection_manager.handle_websocket_message(
                websocket,
                {"type": "subscribe", "notification_types": ["performance_update"]},
                connection_id,
            )

            # Send initial performance summary
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "performance_summary",
                        "message": "Subscribed to performance updates",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )

            # Message handling loop
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    await connection_manager.handle_websocket_message(
                        websocket, message, connection_id
                    )
                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Invalid JSON format",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

        except WebSocketDisconnect:
            logger.info(
                f"Performance updates WebSocket disconnected for user {user_id}"
            )
        finally:
            await connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"Failed to establish performance updates WebSocket: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@ml_websocket_router.websocket("/ai-insights/{user_id}")
async def websocket_ai_insights_endpoint(
    websocket: WebSocket, user_id: int, token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time AI insights

    This endpoint provides live AI-powered insights including:
    - Market opportunities
    - Lead nurturing alerts
    - Client insights
    - Predictive analytics
    """
    try:
        # Validate authentication
        if not token:
            await websocket.close(code=4001, reason="Authentication token required")
            return

        # Verify user token and access
        try:
            user = await get_current_user_websocket(token)
            if user["id"] != user_id:
                await websocket.close(code=4003, reason="Unauthorized access")
                return
        except Exception as e:
            logger.error(f"Authentication failed for AI insights user {user_id}: {e}")
            await websocket.close(code=4001, reason="Authentication failed")
            return

        # Establish connection
        connection_id = await connection_manager.connect(websocket, user_id)

        try:
            # Subscribe to AI insights
            await connection_manager.handle_websocket_message(
                websocket,
                {"type": "subscribe", "notification_types": ["ai_insight"]},
                connection_id,
            )

            # Send initial AI insights summary
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "ai_insights_summary",
                        "message": "Subscribed to AI insights",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )

            # Message handling loop
            while True:
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    await connection_manager.handle_websocket_message(
                        websocket, message, connection_id
                    )
                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Invalid JSON format",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

        except WebSocketDisconnect:
            logger.info(f"AI insights WebSocket disconnected for user {user_id}")
        finally:
            await connection_manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"Failed to establish AI insights WebSocket: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


# REST endpoints for WebSocket management
@ml_websocket_router.get("/connections/stats")
async def get_connection_stats():
    """Get current WebSocket connection statistics"""
    try:
        stats = await connection_manager.get_connection_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Failed to get connection stats: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get connection statistics"
        )


@ml_websocket_router.get("/connections/user/{user_id}")
async def get_user_connections(user_id: int):
    """Get active connections for a specific user"""
    try:
        if user_id in connection_manager.user_connections:
            connections = list(connection_manager.user_connections[user_id])
            return JSONResponse(
                content={
                    "user_id": user_id,
                    "active_connections": connections,
                    "connection_count": len(connections),
                }
            )
        else:
            return JSONResponse(
                content={
                    "user_id": user_id,
                    "active_connections": [],
                    "connection_count": 0,
                }
            )
    except Exception as e:
        logger.error(f"Failed to get user connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user connections")


@ml_websocket_router.post("/notifications/send")
async def send_notification_via_websocket(notification: dict, target_users: list[int]):
    """Send a notification to specific users via WebSocket"""
    try:
        sent_count = 0
        for user_id in target_users:
            try:
                await connection_manager.send_notification(notification, user_id)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")

        return JSONResponse(
            content={
                "message": f"Notification sent to {sent_count} users",
                "target_users": target_users,
                "sent_count": sent_count,
            }
        )
    except Exception as e:
        logger.error(f"Failed to send notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notifications")


@ml_websocket_router.post("/market-alerts/broadcast")
async def broadcast_market_alert(alert: dict):
    """Broadcast a market alert to all connected agents"""
    try:
        await connection_manager.send_market_alert(alert)
        return JSONResponse(
            content={"message": "Market alert broadcasted successfully", "alert": alert}
        )
    except Exception as e:
        logger.error(f"Failed to broadcast market alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast market alert")


# Import datetime for timestamp generation
from datetime import datetime
