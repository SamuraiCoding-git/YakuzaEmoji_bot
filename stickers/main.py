import asyncio
import time
import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from stickers.config import load_config
from stickers.infrastructure.database.setup import get_repo
from stickers.schemas.request import GeneratePackRequest
from stickers.schemas.response import GeneratePackResponse, ProgressResponse
from stickers.services.media_downloader import MediaDownloader
from stickers.services.pack_generator import PackGenerator
from stickers.tasks.queue import TaskQueue

app = FastAPI(title="Sticker Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация
task_queue = TaskQueue()
media_downloader = MediaDownloader()
pack_generator = PackGenerator()
config = load_config()
progress_store: Dict[str, Dict] = {}
websocket_connections: Dict[str, List[WebSocket]] = {}


async def notify_clients(task_id: str, payload: dict):
    connections = websocket_connections.get(task_id, [])
    for ws in connections:
        try:
            await ws.send_json(payload)
        except Exception:
            pass


async def process_generate_pack(task_id: str, request: GeneratePackRequest):
    start_queue_time = time.time()
    repo = await get_repo(config)

    try:
        progress_store[task_id] = {
            "status": "accepted",
            "progress": 0,
            "message": "Задача получена и принята в обработку",
            "sticker_pack_url": None
        }
        await notify_clients(task_id, progress_store[task_id])

        progress_store[task_id]["status"] = "processing"
        progress_store[task_id]["message"] = "Начинаем скачивание медиа..."
        await notify_clients(task_id, progress_store[task_id])

        media_path = await media_downloader.download(request.file_id, request.media_type)

        async def progress_callback(done: int, total: int, cutting: int, phase: int):
            if phase == 1:
                # 0–9%: этап нарезки
                progress = int((cutting / total) * 9)
                message = f"Нарезка {cutting}/{total}"
            else:
                # 10–99%: этап загрузки
                progress = 10 + int((done / total) * 90)
                message = f"Загружено {done}/{total}"
            payload = {
                "status": "processing",
                "progress": progress,
                "message": message,
                "sticker_pack_url": None
            }
            progress_store[task_id] = payload
            await notify_clients(task_id, payload)

        pack_url, duration, queued = await pack_generator.generate_pack(
            media_path,
            request.user_id,
            request.width,
            request.height,
            "static" if request.media_type == "photo" else "video",
            start_queue_time,
            progress_callback
        )

        await repo.stickers.create_sticker(
            user_id=request.user_id,
            sticker_name=pack_url,
            sticker_type="static" if request.media_type == "photo" else "video",
            file_id=request.file_id,
            width=request.width,
            height=request.height,
            durations={
                "queued": queued,
                "duration": duration
            }
        )

        progress_store[task_id]["progress"] = 100
        progress_store[task_id]["status"] = "done"
        progress_store[task_id]["message"] = "Пак успешно создан!"
        progress_store[task_id]["sticker_pack_url"] = pack_url
        await notify_clients(task_id, progress_store[task_id])

    except Exception as e:
        progress_store[task_id]["status"] = "error"
        progress_store[task_id]["message"] = f"Ошибка: {str(e)}"
        progress_store[task_id]["progress"] = 0
        await notify_clients(task_id, progress_store[task_id])


async def schedule_task(task_id: str, request):
    asyncio.create_task(task_queue.add_task(process_generate_pack, task_id, request))


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
        websocket_connections[task_id].remove(websocket)
        ping_task.cancel()
