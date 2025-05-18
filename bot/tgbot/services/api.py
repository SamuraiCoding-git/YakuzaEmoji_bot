import aiohttp

API_URL = "localhost:8000"

async def start_generation(request_data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        print("Request Data: ", request_data)
        async with session.post(f"http://{API_URL}/generate", json=request_data) as resp:
            if resp.status != 200:
                raise Exception(f"Ошибка при старте генерации: {resp.status}")
            return await resp.json()

async def get_progress(task_id: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{API_URL}/progress/{task_id}") as resp:
            if resp.status != 200:
                raise Exception("Задача не найдена")
            return await resp.json()