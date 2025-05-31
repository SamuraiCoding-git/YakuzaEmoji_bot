from aiogram.enums import StickerFormat
from aiogram.types import FSInputFile, InputSticker


class Emoji(InputSticker):
    def __init__(self, document: FSInputFile, format: StickerFormat, emoji: str, keywords: str | None = None):
        super().__init__(
            sticker=document,
            format=format,
            emoji_list=[emoji],
            keywords=keywords)


