import redis
import json
import time

class StickerRedisQueue:
    def __init__(self, redis_url="redis://localhost:6379/0", queue_name="sticker_generate_priority"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = queue_name

    def put(self, task: dict, priority: int):
        # Чем ниже priority, тем выше приоритет
        score = priority
        task["created_at"] = int(time.time())
        self.redis.zadd(self.queue_name, {json.dumps(task): score})

    def pop(self) -> dict | None:
        result = self.redis.zrange(self.queue_name, 0, 0, withscores=False)
        if result:
            task_json = result[0]
            self.redis.zrem(self.queue_name, task_json)
            return json.loads(task_json)
        return None