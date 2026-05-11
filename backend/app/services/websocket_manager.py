"""StartupOS AI — WebSocket Manager

Manages active WebSocket connections per workflow and broadcasts
agent events to connected frontends in real-time.
"""

import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections grouped by workflow_id."""

    def __init__(self):
        # { workflow_id: [websocket_connections] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, workflow_id: str, websocket: WebSocket):
        """Accept a WebSocket connection and register it to a workflow."""
        await websocket.accept()
        if workflow_id not in self.active_connections:
            self.active_connections[workflow_id] = []
        self.active_connections[workflow_id].append(websocket)
        logger.info(f"WebSocket connected: workflow={workflow_id}, total={len(self.active_connections[workflow_id])}")

    def disconnect(self, workflow_id: str, websocket: WebSocket):
        """Remove a WebSocket connection from a workflow."""
        if workflow_id in self.active_connections:
            self.active_connections[workflow_id].remove(websocket)
            if not self.active_connections[workflow_id]:
                del self.active_connections[workflow_id]
            logger.info(f"WebSocket disconnected: workflow={workflow_id}")

    async def broadcast(self, workflow_id: str, event: dict):
        """Send an event to all WebSocket connections for a workflow."""
        if workflow_id not in self.active_connections:
            return

        message = json.dumps(event)
        dead_connections = []

        for connection in self.active_connections[workflow_id]:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for dead in dead_connections:
            self.active_connections[workflow_id].remove(dead)

    async def send_agent_started(self, workflow_id: str, agent_name: str):
        await self.broadcast(workflow_id, {
            "type": "agent_started",
            "agent": agent_name,
        })

    async def send_agent_thinking(self, workflow_id: str, agent_name: str, content: str):
        await self.broadcast(workflow_id, {
            "type": "agent_thinking",
            "agent": agent_name,
            "content": content,
        })

    async def send_agent_tool_call(self, workflow_id: str, agent_name: str, tool: str, query: str):
        await self.broadcast(workflow_id, {
            "type": "agent_tool_call",
            "agent": agent_name,
            "tool": tool,
            "query": query,
        })

    async def send_agent_completed(self, workflow_id: str, agent_name: str, preview: str):
        await self.broadcast(workflow_id, {
            "type": "agent_completed",
            "agent": agent_name,
            "output_preview": preview,
        })

    async def send_inter_agent_message(self, workflow_id: str, sender: str, recipient: str, message: str):
        await self.broadcast(workflow_id, {
            "type": "inter_agent_message",
            "from": sender,
            "to": recipient,
            "message": message,
        })

    async def send_workflow_completed(self, workflow_id: str):
        await self.broadcast(workflow_id, {
            "type": "workflow_completed",
            "download_url": f"/api/v1/projects/report/{workflow_id}",
        })

    async def send_workflow_error(self, workflow_id: str, agent_name: str, error: str):
        await self.broadcast(workflow_id, {
            "type": "workflow_error",
            "agent": agent_name,
            "error": error,
            "recoverable": True,
        })


# Singleton
ws_manager = WebSocketManager()
