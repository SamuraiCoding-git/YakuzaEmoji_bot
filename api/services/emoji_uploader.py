import os
import asyncio
import traceback
import uuid
import logging
from typing import Optional, Literal

from telethon import TelegramClient

from api.config import load_config, Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EmojiPackUploader:
    async def upload(
        self,
        client: TelegramClient,
        user_id: int,
        tiles_dir: str,
        config: Config = load_config(),
        pack_name_prefix: str = " — создай свой пак",
        pack_type: Literal["static", "video"] = "static",
        bot_username: str = "YakuzaEmoji_bot"
    ) -> Optional[str]:
        bot = "@Stickers"
        logger.info(f"📥 Загружаем эмодзи-пак типа {pack_type} для user_id={user_id}")

        try:
            await client.send_message(bot, "/newemojipack")
            await asyncio.sleep(1)

            await client.send_message(bot, "Static emoji" if pack_type == "static" else "Video emoji")
            await asyncio.sleep(0.5)

            await client.send_message(bot, f"@{bot_username if bot_username else 'YakuzaEmoji_bot'} {pack_name_prefix}")
            await asyncio.sleep(0.5)

            tiles = sorted([
                f for f in os.listdir(tiles_dir)
                if f.lower().endswith(".png") or f.lower().endswith(".webm")
            ])
            if not tiles:
                logger.warning("⚠️ Папка с тайлами пуста.")
                return None

            total = len(tiles)
            emojis = self._shuffled_emojis(total, config.pack_generator.emoji_list)

            for i, (filename, emoji) in enumerate(zip(tiles, emojis)):
                path = os.path.join(tiles_dir, filename)

                try:
                    logger.info(f"📤 Отправка файла: {filename} с эмодзи {emoji}")
                    await client.send_file(bot, path, force_document=True)
                    await asyncio.sleep(0.5)
                    await client.send_message(bot, emoji)
                    await asyncio.sleep(0.7)

                    logger.info(f"[{i + 1}/{total}] ✅ {filename} → {emoji}")
                except Exception as e:
                    logger.exception(f"❌ Ошибка при отправке {filename}: {e}")

            await client.send_message(bot, "/publish")
            await asyncio.sleep(0.5)
            await client.send_message(bot, "/skip")

            short_name = f"{bot_username}_{uuid.uuid4().hex[:10]}_{user_id}"
            await client.send_message(bot, short_name)
            await asyncio.sleep(0.5)

            logger.info(f"🎉 Пак успешно создан: https://t.me/addemoji/{short_name}")
            return short_name

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"❌ Ошибка при создании эмодзи-пака: {e}\n{tb}")
            return None

    def _shuffled_emojis(self, total: int, emojis: list[str]) -> list[str]:
        emojis = emojis.copy()
        uuid_seed = uuid.uuid4().int
        emojis.sort()
        shuffled = sorted(emojis, key=lambda x: hash((x, uuid_seed)))
        return [shuffled[i % len(shuffled)] for i in range(total)]