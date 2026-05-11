"""StartupOS AI — WebSocket Endpoint"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/ws/{workflow_id}")
async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow updates.

    Frontend connects here immediately after starting a workflow.
    Events are pushed as agents run.
    """
    await ws_manager.connect(workflow_id, websocket)
    try:
        # Keep connection alive, listen for any client messages (e.g., ping)
        while True:
            data = await websocket.receive_text()
            # Client can send "ping" to keep alive
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(workflow_id, websocket)
