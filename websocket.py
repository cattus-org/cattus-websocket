from fastapi import WebSocket
from typing import List, Dict, Any

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket, camera_id: int = None, user_id: int = None):
        await websocket.accept()
        self.active_connections.append({
            "websocket": websocket,
            "cameraId": camera_id,
            "userId": user_id
        })

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [conn for conn in self.active_connections if conn["websocket"] != websocket]

    async def broadcast(self, message: str, camera_id: int = None):
        disconnected = []
        for conn in self.active_connections:
            ws = conn["websocket"]
            if camera_id is None or conn.get("cameraId") == camera_id:
                try:
                    await ws.send_text(message)
                except Exception as e:
                    print(f"[WS] Erro ao enviar mensagem: {e}")
                    disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)
