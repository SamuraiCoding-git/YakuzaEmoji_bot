import asyncio
from typing import Callable, Any, Awaitable


class TaskQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.worker_running = False

    async def add_task(
        self,
        coro: Callable[..., Awaitable[Any]],
        *args,
        priority: int = 1,
        **kwargs
    ):
        await self.queue.put((priority, coro, args, kwargs))
        if not self.worker_running:
            asyncio.create_task(self._worker())

    async def _worker(self):
        self.worker_running = True
        while not self.queue.empty():
            priority, coro, args, kwargs = await self.queue.get()
            try:
                await coro(*args, **kwargs)
            except Exception as e:
                print(f"[TaskQueue] Ошибка при выполнении задачи с приоритетом {priority}: {e}")
            finally:
                self.queue.task_done()
        self.worker_running = False
