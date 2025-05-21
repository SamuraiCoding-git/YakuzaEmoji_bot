from telethon.tl.types import InputStickerSetItem, TypeInputDocument


class Emoji(InputStickerSetItem):
    def __init__(self, document: TypeInputDocument, emoji: str, bytes_: bytes, keywords: str | None = None):
        self.bytes = bytes_
        super().__init__(document, emoji, keywords=keywords)