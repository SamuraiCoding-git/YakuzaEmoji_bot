import logging
import time

import redis
from aiogram import Bot
from fastapi import APIRouter, HTTPException

from api.queue.redis_queue import StickerRedisQueue
from api.schemas.request import GeneratePackRequest
from api.schemas.response import GeneratePackResponse
from api.services.pack_generator import PackGenerator
from api.config import load_config
from api.webhook.utils.dependencies import get_repo_instance

logging.basicConfig(level=logging.INFO)

stickers_router = APIRouter(prefix="/stickers")
config = load_config(".env")
queue = StickerRedisQueue()
bot = Bot(config.telegram_api.token)
pack_generator = PackGenerator(
    bot=bot,
    config=config
)

redis_client = redis.from_url("redis://localhost:6379/0")

COOLDOWN_SECONDS = 5 * 60  # 5 минут

def is_admin(user_id: int):
    return user_id in config.telegram_api.admin_ids

@stickers_router.post("/generate", response_model=GeneratePackResponse)
async def generate_pack(request: GeneratePackRequest):
    repo = get_repo_instance()
    try:
        # Проверяем подписку
        is_free = True
        if is_admin(request.user_id):
            priority = 0
            is_free = False
        else:
            subs = await repo.user_subscriptions.get_active_subscription(request.user_id)
            if subs:
                priority = getattr(request, "priority", 5)
                is_free = False
            else:
                priority = getattr(request, "priority", 5)
                is_free = True

        # Кулдаун для бесплатных
        if is_free:
            key = f"cooldown:{request.user_id}"
            last_ts = redis_client.get(key)
            now = int(time.time())
            if last_ts and now - int(last_ts) < COOLDOWN_SECONDS:
                seconds_left = COOLDOWN_SECONDS - (now - int(last_ts))
                minutes = seconds_left // 60
                seconds = seconds_left % 60
                raise HTTPException(
                    status_code=429,
                    detail=f"Бесплатная генерация доступна раз в 5 минут. Повторите через {minutes} мин {seconds} сек."
                )
            # Устанавливаем новый кулдаун
            redis_client.set(key, now)

        # Постановка задачи
        task = {
            "user_id": request.user_id,
            "file_id": request.file_id,
            "width": request.width,
            "height": request.height,
            "media_type": request.media_type,
            "referral_bot_name": request.referral_bot_name,
        }
        queue.put(task, priority)
        return GeneratePackResponse(success=True, message="Задача поставлена в очередь")

    except HTTPException:
        raise  # прокидываем дальше
    except Exception as e:
        import traceback
        logging.error(f"❌ Ошибка постановки задачи: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to enqueue sticker pack task")
