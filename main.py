import asyncio
import uvicorn
from auth import decode_jwt_token
from websocket import ConnectionManager
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from database import notifications_collection, activities_collection

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa na startup
    tasks = [
        asyncio.create_task(monitor_notifications()),
        asyncio.create_task(monitor_activities())
    ]
    yield
    # Executa no shutdown (opcional: você pode cancelar tarefas aqui)
    for task in tasks:
        task.cancel()

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        user_data = decode_jwt_token(token)
        print("Usuário autenticado:", user_data)
    except:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def monitor_notifications():
    async with notifications_collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        async for change in stream:
            print("Nova notificação.")
            await manager.broadcast("nova_notificacao")

async def monitor_activities():
    async with activities_collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        async for change in stream:
            print("Nova atividade.")
            await manager.broadcast("nova_atividade")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
