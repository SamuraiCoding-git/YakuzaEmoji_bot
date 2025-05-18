from datetime import datetime, timedelta

import aioredis

TIER_LIMITS = {
    "basic": {"daily_limit": 5, "cooldown": 30},
    "premium": {"daily_limit": 15, "cooldown": 10},
    "yakuza": {"daily_limit": 50, "cooldown": 2},  # fair-use
}

class RedisLimiter:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    def _daily_key(self, user_id: int):
        return f"user:{user_id}:daily_count"

    def _cooldown_key(self, user_id: int):
        return f"user:{user_id}:last_gen"

    async def can_generate(self, user_id: int, tier: str) -> tuple[bool, str]:
        limits = TIER_LIMITS.get(tier)
        if not limits:
            return False, "Неизвестный уровень доступа."

        now = datetime.utcnow()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        ttl = int((midnight - now).total_seconds())

        cooldown_key = self._cooldown_key(user_id)
        daily_key = self._daily_key(user_id)

        # Проверка кулдауна
        last_gen = await self.redis.get(cooldown_key)
        if last_gen:
            elapsed = now.timestamp() - float(last_gen)
            if elapsed < limits["cooldown"]:
                wait_time = round(limits["cooldown"] - elapsed)
                return False, f"⏱ Подожди ещё {wait_time} сек."

        # Проверка суточного лимита
        daily_count = await self.redis.get(daily_key)
        if daily_count and int(daily_count) >= limits["daily_limit"]:
            return False, "❌ Исчерпан суточный лимит генераций."

        # Обновление счётчиков
        pipe = self.redis.pipeline()
        pipe.set(cooldown_key, now.timestamp())
        pipe.expire(cooldown_key, ttl)
        pipe.incr(daily_key)
        pipe.expire(daily_key, ttl)
        await pipe.execute()

        return True, "OK"

    async def get_usage(self, user_id: int) -> dict:
        return {
            "count": int(await self.redis.get(self._daily_key(user_id)) or 0),
            "last": float(await self.redis.get(self._cooldown_key(user_id)) or 0.0),
        }
