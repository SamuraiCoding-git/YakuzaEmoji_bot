import asyncio
import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.schemas.request import GeneratePackRequest
from api.schemas.response import GeneratePackResponse, ProgressResponse
from api.webhook.utils.generate import schedule_task

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Sticker Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate", response_model=GeneratePackResponse)
async def generate_pack(request: GeneratePackRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    progress_store[task_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Задача поставлена в очередь",
        "sticker_pack_url": None
    }
    background_tasks.add_task(schedule_task, task_id, request)
    return GeneratePackResponse(success=True, task_id=task_id, status_url=f"/progress/{task_id}")

@app.get("/progress/{task_id}", response_model=ProgressResponse)
async def get_progress(task_id: str):
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return ProgressResponse(**progress_store[task_id])

@app.websocket("/ws/progress/{task_id}")
async def websocket_progress(websocket: WebSocket, task_id: str):
    await websocket.accept()
    logging.info(f"🔌 WebSocket подключен: {task_id}")

    if task_id not in websocket_connections:
        websocket_connections[task_id] = []
    websocket_connections[task_id].append(websocket)

    if task_id in progress_store:
        await websocket.send_json(progress_store[task_id])

    async def ping():
        while True:
            try:
                await websocket.send_json({"ping": time.time()})
                await asyncio.sleep(10)
            except:
                break

    ping_task = asyncio.create_task(ping())

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logging.info(f"❌ WebSocket отключён: {task_id}")
        websocket_connections[task_id].remove(websocket)
        ping_task.cancel()
