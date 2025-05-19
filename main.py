import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket import ConnectionManager
from database import collection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
manager = ConnectionManager()

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Mantém a conexão aberta
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Change Stream (executar em uma task separada)
async def watch_insercoes():
    async with collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        async for change in stream:
            print("Nova notificação.")
            await manager.broadcast("nova_notificacao")

# Iniciar a task de escuta quando o app sobe
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(watch_insercoes())