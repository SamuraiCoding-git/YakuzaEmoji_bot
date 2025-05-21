import hashlib
from io import BytesIO
from random import randint

from PIL import Image
from telethon.errors import PackShortNameOccupiedError, BadRequestError, StickersetInvalidError
from telethon.functions import stickers, messages
from telethon.tl import types as tl_types
from telethon.tl.functions.messages import UploadMediaRequest
from telethon.types import Chat, Channel
from telethon.utils import get_input_document

from stickers.functions._emoji import Emoji


class EmojiSetCreator:
    def __init__(self, bot, mask_path='mask.png'):
        self.bot = bot
        self.mask_image = Image.open(mask_path).convert('L')

    async def create_set(self, chat: Chat | Channel, user_id: int, *, existing: bool, bot_username: str, pack_name_prefix: str) -> bool:
        title = f"@{bot_username} {pack_name_prefix}"
        link = get_set_link(chat.id, self.bot.me.username)

        emojis = await self._create_emoji_items(chat)

        if not existing:
            request = stickers.CreateStickerSetRequest(user_id, title, link, emojis, emojis=True)
            try:
                await self.bot(request)
            except PackShortNameOccupiedError:
                pass
            else:
                return True

        get_set_request = messages.GetStickerSetRequest(
            tl_types.InputStickerSetShortName(link),
            hash=randint(1, 10 ** 9)
        )
        try:
            emoji_set: tl_types.messages.StickerSet = await self.bot(get_set_request)
        except StickersetInvalidError:
            return await self.create_set(chat, user_id, existing=False)

        input_emoji_set = tl_types.InputStickerSetShortName(link)

        if emoji_set.set.title != title:
            update_title_request = stickers.RenameStickerSetRequest(input_emoji_set, title)
            await self.bot(update_title_request)

        for emoji in emojis:
            add_request = stickers.AddStickerToSetRequest(input_emoji_set, emoji)
            await self.bot(add_request)

        for document in emoji_set.documents:
            remove_request = stickers.RemoveStickerFromSetRequest(get_input_document(document))
            try:
                await self.bot(remove_request)
            except BadRequestError:
                pass

        return True

    async def _create_emoji_items(self, chat: Chat | Channel) -> list[Emoji]:
        items = []

        if chat.photo:
            photo = await self.bot.download_profile_photo(chat, bytes)
            items.append(await self._create_emoji(photo))

        async for user in self.bot.iter_participants(chat):
            if user.is_self or user.photo is None or isinstance(user.photo, tl_types.UserProfilePhotoEmpty):
                continue

            photo = await self.bot.download_profile_photo(user, bytes)
            items.append(await self._create_emoji(photo, keywords=user.username or None))

            if len(items) == 120:
                break

        return items

    async def _create_emoji(self, original_photo_bytes: bytes, *, keywords: str = None) -> Emoji:
        new_photo_bytes_io = BytesIO()
        image = Image.open(BytesIO(original_photo_bytes)).resize((90, 90))
        image.putalpha(self.mask_image)

        container_image = Image.new('RGBA', (100, 100), (255, 0, 0, 0))
        container_image.paste(image, (5, 5))
        container_image.save(new_photo_bytes_io, format='webp')

        file = await self.bot.upload_file(new_photo_bytes_io.getvalue())
        uploaded_document = tl_types.InputMediaUploadedDocument(file, 'image/webp', [])
        media = await self.bot(UploadMediaRequest(tl_types.InputPeerSelf(), uploaded_document))
        input_document = get_input_document(media)

        return Emoji(input_document, '🟣', new_photo_bytes_io.getvalue(), keywords=keywords)

    async def get_emoji_set_hash_set(self, emoji_set: tl_types.messages.StickerSet):
        hash_set = set()
        for document in emoji_set.documents:
            emoji_bytes = await self.bot.download_file(document, bytes)
            emoji_hash = hashlib.sha256(emoji_bytes).hexdigest()
            hash_set.add(emoji_hash)
        return hash_set