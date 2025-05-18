import os
import asyncio
import traceback
import uuid
import logging
from typing import Callable, Awaitable, Optional, Literal

from telethon import TelegramClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class EmojiPackUploader:
    def __init__(self, emoji_list: list[str], pack_name_prefix: str = " — создай свой пак", bot_username: str = "YakuzaEmoji_bot"):
        self.bot_username = bot_username
        self.pack_name_prefix = pack_name_prefix
        self.emojis = emoji_list if emoji_list else ["🔥"]

    async def upload(
        self,
        client: TelegramClient,
        user_id: int,
        tiles_dir: str,
        pack_type: Literal["static", "video"] = "static",
        progress_callback: Optional[Callable[[int, int, int, int], Awaitable[None]]] = None,
        cutting_total: int = 0  # <= теперь ожидаем общее число тайлов, использованное для нарезки
    ) -> Optional[str]:
        bot = "@Stickers"
        logger.info(f"📥 Загружаем эмодзи-пак типа {pack_type} для user_id={user_id}")

        try:
            await client.send_message(bot, "/newemojipack")
            await asyncio.sleep(1)

            await client.send_message(bot, "Static emoji" if pack_type == "static" else "Video emoji")
            await asyncio.sleep(0.5)

            await client.send_message(bot, f"@{self.bot_username} {self.pack_name_prefix}")
            await asyncio.sleep(0.5)

            tiles = sorted([
                f for f in os.listdir(tiles_dir)
                if f.lower().endswith(".png") or f.lower().endswith(".webm")
            ])
            if not tiles:
                logger.warning("⚠️ Папка с тайлами пуста.")
                return None

            total = len(tiles)
            emojis = self._shuffled_emojis(total)

            for i, (filename, emoji) in enumerate(zip(tiles, emojis)):
                path = os.path.join(tiles_dir, filename)

                try:
                    logger.info(f"📤 Отправка файла: {filename} с эмодзи {emoji}")
                    await client.send_file(bot, path, force_document=True)
                    await asyncio.sleep(0.5)
                    await client.send_message(bot, emoji)
                    await asyncio.sleep(0.3)

                    if progress_callback:
                        await progress_callback(i + 1, total, cutting_total, phase=2)

                    logger.info(f"[{i + 1}/{total}] ✅ {filename} → {emoji}")
                except Exception as e:
                    logger.exception(f"❌ Ошибка при отправке {filename}: {e}")

            await client.send_message(bot, "/publish")
            await asyncio.sleep(0.5)
            await client.send_message(bot, "/skip")

            short_name = f"{self.bot_username}_{uuid.uuid4().hex[:10]}_{user_id}"
            await client.send_message(bot, short_name)
            await asyncio.sleep(0.5)

            logger.info(f"🎉 Пак успешно создан: https://t.me/addemoji/{short_name}")
            return short_name

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"❌ Ошибка при создании эмодзи-пака: {e}\n{tb}")
            return None

    def _shuffled_emojis(self, total: int) -> list[str]:
        emojis = self.emojis.copy()
        uuid_seed = uuid.uuid4().int
        emojis.sort()
        shuffled = sorted(emojis, key=lambda x: hash((x, uuid_seed)))
        return [shuffled[i % len(shuffled)] for i in range(total)]