import logging
import os
import time
from pathlib import Path

from aiogram import Bot
from aiogram.enums import StickerFormat
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from api.clients.session_manager import SessionManager
from api.config import load_config
from api.services.emoji_creator import EmojiCreator
from api.services.emoji_sender import EmojiSender
from api.services.emoji_uploader import EmojiPackUploader
from api.services.media_downloader import MediaDownloader
from api.services.media_processor import MediaProcessor
from api.services.sticker_manager import StickerManager

logger = logging.getLogger("PackGenerator")

class PackGenerator:
    def __init__(self, bot: Bot, config):
        self.config = config
        self.bot = bot
        self.media_processor = MediaProcessor(self.config.media.temp_media_dir)

        sessions_dir = os.path.join(os.getcwd(), self.config.telegram_api.sessions_dir)
        sessions_dir = Path(sessions_dir)

        session_files = [str(p.resolve()) for p in sessions_dir.glob("*.session")]

        self.session_manager = SessionManager(
            session_files=session_files,
            api_id=self.config.telegram_api.api_id,
            api_hash=self.config.telegram_api.api_hash
        )
        self.session_manager_started = False

        self.emoji_creator = EmojiCreator(
            bot=bot,
        )

        self.emoji_sender = EmojiSender(
            session_manager=self.session_manager
        )

        self.sticker_manager = StickerManager(
            bot=bot
        )

        self.media_downloader = MediaDownloader()

        self.emoji_uploader = EmojiPackUploader()


    async def generate_pack(
        self,
        user_id: int,
        file_id: str,
        width: int,
        height: int,
        format: StickerFormat,
        referral_bot_name: str = None
    ) -> tuple[str, float]:
        created = time.time()
        logger.info(f"[PackGenerator] user_id={user_id} | файл: {file_id} | type={format}")

        if not self.session_manager_started:
            await self.session_manager.start_all()
            self.session_manager_started = True

        media_path = await self.media_downloader.download(
            file_id=file_id,
        )

        # Нарезка на тайлы
        if media_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            directory = await self.media_processor.crop_image_to_tiles(
                media_path, width, height
            )
        elif media_path.lower().endswith((".mp4", ".mov", ".webm")):
            directory = await self.media_processor.crop_video_to_webm_tiles(
                media_path, width, height
            )
        else:
            raise ValueError("Неподдерживаемый тип медиа")

        logger.info(f"[PackGenerator] Нарезка завершена: {directory}")

        emojis = await self.emoji_creator.create_from_directory(
            directory,
            format.value
        )

        if int((width * height) / 10000) <= 50:
            link = await self.sticker_manager.create_sticker_set(
                user_id=user_id,
                emojis=emojis,
                sticker_format=format.value,
                referral_bot_name=referral_bot_name
            )
        else:
            client = await self.session_manager.get_client()
            link = await self.emoji_uploader.upload(
                client=client.client,
                user_id=user_id,
                tiles_dir=directory,
                config=self.config,
                bot_username=referral_bot_name,
                pack_type=format.value
            )

            await self.session_manager.release_client(client)
        self.media_processor.cleanup_media(directory)

        if not link:
            raise RuntimeError("Не удалось создать эмодзи-пак")

        duration = time.time() - created

        logger.info(
            f"[PackGenerator] ✅ Пак создан за {duration:.2f} сек"
        )

        # ⬇️ Добавляем отправку emoji-сетки пользователю
        short_name = link

        try:
            # 🧱 Собираем и отправляем сетку (3 выравнивания)
            await self.emoji_sender.send_emoji(
                user_id=user_id,
                short_name=short_name,
                rows=int(height / 100),
                cols=int(width / 100)
            )

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔗 Перейти к стикерпаку",
                                          url=link)]
                ]
            )

            await self.bot.send_message(
                chat_id=user_id,
                text="✅ Готово! Нажми на кнопку ниже, чтобы открыть стикерпак.",
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"[PackGenerator] ⚠️ Не удалось отправить emoji-сетку: {e}")

        return f"https://t.me/addemoji/{link}", duration