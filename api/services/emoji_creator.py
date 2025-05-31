from pathlib import Path
from typing import List

from aiogram import Bot
from aiogram.enums import StickerFormat
from aiogram.types import FSInputFile

from api.config import load_config
from api.functions._emoji import Emoji


class EmojiCreator:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = load_config()

    async def create_emoji_from_file(self, file_path: Path, emoji: str, format: StickerFormat) -> Emoji:
        file = FSInputFile(file_path)

        return Emoji(file, format, emoji)

    async def create_from_directory(self, directory_path: str, format: StickerFormat) -> List[Emoji]:
        path = Path(directory_path)
        files = sorted(path.glob("*.*"))  # любые файлы по порядку
        emoji_list = self.config.pack_generator.emoji_list

        if len(files) > len(emoji_list):
            raise ValueError("❌ Недостаточно эмодзи в config.pack_generator.emoji_list")

        items = []
        for file_path, emoji in zip(files, emoji_list):
            emoji_obj = await self.create_emoji_from_file(file_path, emoji, format)
            items.append(emoji_obj)

        return items