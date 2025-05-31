import re
import uuid

from aiogram import Bot
from aiogram.enums import StickerFormat, StickerType
from aiogram.types import InputSticker


class StickerManager:
    def __init__(self, bot: Bot):
        self.bot = bot

    def generate_sticker_set_name(self, bot_username: str, user_id: int) -> str:
        bot_username = bot_username.lower()
        base = uuid.uuid4().hex[:8]

        # Оставим только латиницу, цифры и подчёркивания
        base = re.sub(r"[^a-zA-Z0-9_]", "", base)

        # Начинается с буквы — если нет, добавим 's' в начало
        if not base or not base[0].isalpha():
            base = f"s{base}"

        # Уберём двойные подчёркивания
        base = re.sub(r"__+", "_", base)

        # Отрежем, чтобы с учётом _by_bot длина не превышала 64
        suffix = f"_by_{bot_username}"
        max_base_len = 64 - len(suffix)
        base = base[:max_base_len]

        return f"{base}_{user_id}{suffix}"

    async def create_sticker_set(
        self,
        user_id: int,
        emojis: list[InputSticker],
        sticker_format: StickerFormat,
        sticker_type: str = "custom_emoji",
        name: str = None,
        referral_bot_name: str = None,
    ):
        try:
            if not name:
                name = self.generate_sticker_set_name(referral_bot_name or 'YakuzaEmoji_bot', user_id)

            title = f"@{referral_bot_name if referral_bot_name else 'YakuzaEmoji_bot'} — создай свой пак"

            await self.bot.create_new_sticker_set(
                user_id=user_id,
                name=name,
                title=title,
                stickers=emojis,
                sticker_type=sticker_type,
                sticker_format=sticker_format,
            )
            return name

        except Exception as e:
            raise RuntimeError(f"❌ Failed to create sticker set: {e}")