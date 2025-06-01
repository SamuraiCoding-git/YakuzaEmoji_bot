from redis.asyncio import Redis
import json

REDIS_URL = "redis://localhost:6379/0"
QUEUE_NAME = "sticker_generate_queue"

class StickerRedisQueue:
    def __init__(self):
        self.redis = Redis.from_url(REDIS_URL)

    async def put(self, payload: dict):
        await self.redis.rpush(QUEUE_NAME, json.dumps(payload))

    async def get(self):
        # blpop возвращает (queue_name, data)
        item = await self.redis.blpop(QUEUE_NAME, timeout=5)
        if item:
            return json.loads(item[1])
        return None

    async def close(self):
        await self.redis.close()