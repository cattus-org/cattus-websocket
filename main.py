import asyncio
import json
import asyncpg
from websocket import ConnectionManager
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from database import init_db, DATABASE_URL
from auth import decode_jwt_token

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa na startup
    await init_db()
    
    tasks = [
        asyncio.create_task(monitor_activities())
    ]
    yield
    # Executa no shutdown (opcional: você pode cancelar tarefas aqui)
    for task in tasks:
        task.cancel()

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/activities")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None), cameraId: int = Query(...), userId: int = Query(None)):
    await manager.connect(websocket, camera_id=cameraId, user_id=userId)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def monitor_activities():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('LISTEN activity_changes')
    print("Começou a monitorar atividades usando LISTEN/NOTIFY")
    queue = asyncio.Queue()

    def listener(connection, pid, channel, payload):
        queue.put_nowait(payload)

    await conn.add_listener('activity_changes', listener)

    while True:
        try:
            payload_str = await queue.get()
            payload = json.loads(payload_str)
            print(f"Evento detectado na tabela Activity: {payload}")
            camera_id = payload.get("cameraId")
            cat_id = payload.get("catId")
            activity_id = payload.get("id")
            await manager.broadcast(json.dumps({
                "type": "activity",
                "data": payload,
                "catId": cat_id,
                "cameraId": camera_id,
                "activityId": activity_id
            }), camera_id=camera_id)
        except Exception as e:
            print(f"Error monitoring activities: {e}")
            await asyncio.sleep(5)
            try:
                conn = await asyncpg.connect(DATABASE_URL)
                await conn.execute('LISTEN activity_changes')
                await conn.add_listener('activity_changes', listener)
            except:
                print("Failed to reconnect to database")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)