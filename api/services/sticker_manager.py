import re
import uuid

from aiogram import Bot
from aiogram.enums import StickerFormat
from aiogram.types import InputSticker


class StickerManager:
    def __init__(self, bot: Bot, max_stickers: int = 50):
        self.bot = bot
        self.max_stickers = max_stickers

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

            title = f"@{referral_bot_name or 'YakuzaEmoji_bot'} — создай свой пак"

            first_batch = emojis[:self.max_stickers]
            rest_batch = emojis[self.max_stickers:]

            await self.bot.create_new_sticker_set(
                user_id=user_id,
                name=name,
                title=title,
                stickers=first_batch,
                sticker_type=sticker_type,
                sticker_format=sticker_format,
            )

            if rest_batch:
                await self._add_extra_emojis(user_id, name, rest_batch)

            return name

        except Exception as e:
            raise RuntimeError(f"❌ Failed to create sticker set: {e}")

    async def _add_extra_emojis(self, user_id: int, name: str, emojis: list[InputSticker]):
        for emoji in emojis:
            try:
                await self.bot.add_sticker_to_set(
                    user_id=user_id,
                    name=name,
                    sticker=emoji
                )
            except Exception as e:
                raise RuntimeError(f"❌ Failed to add sticker to set: {e}")