# ==========================================
# File: routers/ws.py
# Description: WebSocket routes for collaborative code editor
# Author: AI Agent
# Created: 2026-08-02
# Changes:
#   - 2026-08-02 (AI Agent): Initial creation
# ==========================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import time

from services.antifraud import evaluate_code_submission

router = APIRouter(
    prefix="/ws",
    tags=["websockets"]
)

class ConnectionManager:
    def __init__(self):
        # room_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # room_id -> start time for anti-fraud
        self.room_start_times: Dict[str, float] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_start_times[room_id] = time.time()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                del self.room_start_times[room_id]

    async def broadcast(self, message: str, room_id: str, exclude: WebSocket = None):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != exclude:
                    await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/editor/{room_id}")
async def websocket_editor_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            event_type = payload.get("type")
            
            if event_type == "code_change":
                # Broadcast the code change to other users in the room (Pair Programming)
                await manager.broadcast(data, room_id, exclude=websocket)
                
            elif event_type == "run_code":
                code = payload.get("code", "")
                start_time = manager.room_start_times.get(room_id, time.time())
                
                # Evaluate via Anti-Fraud
                eval_result = evaluate_code_submission(code, start_time, min_time=5) # 5 seconds for testing
                
                if eval_result["status"] == "rejected":
                    response = {
                        "type": "execution_result",
                        "status": "error",
                        "message": eval_result["reason"]
                    }
                else:
                    response = {
                        "type": "execution_result",
                        "status": "success",
                        "message": "Code executed successfully!",
                        "points": eval_result.get("points_awarded", 0)
                    }
                    
                await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
