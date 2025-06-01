import asyncio
import logging
from aiogram import Bot
from aiogram.enums import StickerFormat

from api.queue.redis_queue import StickerRedisQueue
from api.services.pack_generator import PackGenerator
from api.config import load_config
from api.webhook.utils.dependencies import get_repo_instance

# --- Конфиг ---
WORKER_TOKENS = [
    "7899743037:AAHwdDAY9GNk7m_A8hbHcqaEr5-sZ5jXHqg",
    "7172000332:AAHV8KZPBl5k85qrV5clx15nQcrT9wG-338",
    "7776721117:AAEct-XrfRDgfJnjYKWpbN1ilcV0rkQVQuM",
    "7878723913:AAFju3trW7oux7noxMXshqWN2KjrTeSWVgE",
    "7848210284:AAG5Rl2npWVYZ5KH2LppClgm3tly7bZyAGA"
]


logging.basicConfig(level=logging.INFO)
queue = StickerRedisQueue()
config = load_config(".env")  # Твой конфиг для PackGenerator

async def process_task(bot: Bot, pack_generator: PackGenerator, task: dict):
    user_id = task["user_id"]
    file_id = task["file_id"]
    width = task["width"]
    height = task["height"]
    media_type = task.get("media_type", "photo")
    referral_bot_name = task.get("referral_bot_name")
    repo = get_repo_instance()
    try:
        logging.info(f"▶️ [{bot.token[:10]}...] Генерация стикерпакета: {task}")

        link, duration = await pack_generator.generate_pack(
            user_id,
            file_id,
            width,
            height,
            StickerFormat.STATIC if media_type == "photo" else StickerFormat.VIDEO,
            referral_bot_name
        )

        await repo.stickers.create_sticker(
            user_id,
            link,
            file_id,
            StickerFormat.STATIC if media_type == "photo" else StickerFormat.VIDEO,
            width,
            height,
            {"duration": duration}
        )

        try:
            await bot.send_message(user_id, f"✅ Ваш стикерпак готов: {link}")
        except Exception as e:
            logging.warning(f"Ошибка отправки результата пользователю {user_id}: {e}")

        logging.info(f"✅ Успех! Стикерпак сгенерирован для {user_id}, ссылка: {link}")

    except Exception as e:
        import traceback
        logging.error(f"❌ Ошибка генерации: {traceback.format_exc()}")

async def worker_loop(bot_token: str):
    bot = Bot(token=bot_token)
    pack_generator = PackGenerator(bot=bot, config=config)
    logging.info(f"🚀 Воркер стартовал [{bot_token[:10]}...]")
    while True:
        task = queue.pop()
        if task:
            await process_task(bot, pack_generator, task)
        else:
            await asyncio.sleep(2)  # Ожидание если задач нет

async def main():
    tasks = [worker_loop(token) for token in WORKER_TOKENS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())