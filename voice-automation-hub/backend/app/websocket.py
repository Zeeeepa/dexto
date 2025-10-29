"""WebSocket manager for real-time communication."""

import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Accept new WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_id: Unique connection identifier
            user_id: Optional user identifier
            metadata: Optional connection metadata
        """
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

        logger.info(
            f"WebSocket connected: {connection_id} "
            f"(user: {user_id}, total: {len(self.active_connections)})"
        )

        # Send welcome message
        await self.send_personal_message(
            connection_id,
            {
                "type": "connection",
                "status": "connected",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def disconnect(self, connection_id: str):
        """
        Remove connection.

        Args:
            connection_id: Connection identifier
        """
        if connection_id in self.active_connections:
            # Remove from user connections
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

            # Remove connection
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]

            logger.info(
                f"WebSocket disconnected: {connection_id} "
                f"(total: {len(self.active_connections)})"
            )

    async def send_personal_message(
        self, connection_id: str, message: Dict[str, Any]
    ):
        """
        Send message to specific connection.

        Args:
            connection_id: Target connection
            message: Message to send
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        Send message to all connections of a user.

        Args:
            user_id: Target user
            message: Message to send
        """
        if user_id in self.user_connections:
            for connection_id in list(self.user_connections[user_id]):
                await self.send_personal_message(connection_id, message)

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """
        Broadcast message to all connections.

        Args:
            message: Message to broadcast
            exclude: Connection IDs to exclude
        """
        exclude = exclude or set()
        
        for connection_id in list(self.active_connections.keys()):
            if connection_id not in exclude:
                await self.send_personal_message(connection_id, message)

    async def broadcast_workflow_update(
        self, workflow_id: str, update: Dict[str, Any]
    ):
        """
        Broadcast workflow update.

        Args:
            workflow_id: Workflow identifier
            update: Update data
        """
        message = {
            "type": "workflow_update",
            "workflow_id": workflow_id,
            "update": update,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message)

    async def broadcast_agent_status(
        self, agent_name: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast agent status update.

        Args:
            agent_name: Agent identifier
            status: Agent status
            details: Optional details
        """
        message = {
            "type": "agent_status",
            "agent": agent_name,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message)

    async def broadcast_metric_update(self, metrics: Dict[str, Any]):
        """
        Broadcast metrics update.

        Args:
            metrics: Metrics data
        """
        message = {
            "type": "metrics_update",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message)

    def get_active_connections_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)

    def get_user_connections_count(self, user_id: str) -> int:
        """Get number of connections for a user."""
        return len(self.user_connections.get(user_id, set()))

    def get_all_connection_ids(self) -> list:
        """Get all connection IDs."""
        return list(self.active_connections.keys())

    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection metadata."""
        return self.connection_metadata.get(connection_id)


# Global connection manager
connection_manager = ConnectionManager()


class WebSocketEventEmitter:
    """Event emitter for WebSocket notifications."""

    def __init__(self, manager: ConnectionManager):
        """
        Initialize event emitter.

        Args:
            manager: Connection manager instance
        """
        self.manager = manager

    async def emit_workflow_started(self, workflow_id: str, task: str):
        """Emit workflow started event."""
        await self.manager.broadcast_workflow_update(
            workflow_id,
            {
                "event": "started",
                "task": task,
            },
        )

    async def emit_workflow_completed(
        self, workflow_id: str, result: Any, duration: float
    ):
        """Emit workflow completed event."""
        await self.manager.broadcast_workflow_update(
            workflow_id,
            {
                "event": "completed",
                "result": result,
                "duration": duration,
            },
        )

    async def emit_workflow_failed(self, workflow_id: str, error: str):
        """Emit workflow failed event."""
        await self.manager.broadcast_workflow_update(
            workflow_id,
            {
                "event": "failed",
                "error": error,
            },
        )

    async def emit_agent_thinking(self, agent_name: str, thought: str):
        """Emit agent thinking event."""
        await self.manager.broadcast_agent_status(
            agent_name,
            "thinking",
            {"thought": thought},
        )

    async def emit_agent_action(
        self, agent_name: str, action: str, details: Optional[Dict] = None
    ):
        """Emit agent action event."""
        await self.manager.broadcast_agent_status(
            agent_name,
            "action",
            {"action": action, "details": details or {}},
        )

    async def emit_metrics(self, metrics: Dict[str, Any]):
        """Emit metrics update."""
        await self.manager.broadcast_metric_update(metrics)


# Global event emitter
event_emitter = WebSocketEventEmitter(connection_manager)

