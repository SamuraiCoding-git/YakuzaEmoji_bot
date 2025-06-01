import logging
import os
import time
from pathlib import Path

from aiogram import Bot
from aiogram.enums import StickerFormat

from api.clients.session_manager import SessionManager
from api.services.emoji_creator import EmojiCreator
from api.services.emoji_sender import EmojiSender
from api.services.emoji_uploader import EmojiPackUploader
from api.services.media_downloader import MediaDownloader
from api.services.media_processor import MediaProcessor
from api.services.sticker_manager import StickerManager

logger = logging.getLogger("PackGenerator")


def make_progress_bar(step: int, total: int, start_time: float) -> str:
    bar_length = 15
    percent = step / total
    exact_fill = bar_length * percent
    filled = int(exact_fill)
    partials = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]
    remainder_index = int((exact_fill - filled) * (len(partials)))

    bar = "█" * filled
    if remainder_index and filled < bar_length:
        bar += partials[remainder_index]
    bar = bar.ljust(bar_length, "░")

    elapsed = time.time() - start_time
    eta = (elapsed / step) * (total - step) if step else 0

    return (
        f"[{bar}] {percent:.1%}\n"
        f"⏳ Осталось: {int(eta)}s"
    )

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
        total_steps = 6
        progress = 0

        logger.info(f"[PackGenerator] user_id={user_id} | файл: {file_id} | type={format}")

        if not self.session_manager_started:
            await self.session_manager.start_all()
            self.session_manager_started = True

        message = await self.bot.send_message(
            chat_id=user_id,
            text="⚙️ Генерируем эмодзи-пак..."
        )

        async def update_status(msg: str):
            bar = make_progress_bar(progress, total_steps, created)
            await self.bot.edit_message_text(
                chat_id=user_id,
                message_id=message.message_id,
                text=f"{msg}\n\n{bar}"
            )

        # Step 1: Загрузка файла
        await update_status("📥 Загружаем медиафайл...")
        media_path = await self.media_downloader.download(file_id=file_id)
        progress += 1

        # Step 2: Нарезка
        await update_status("✂️ Нарезаем на тайлы...")
        if media_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            directory = await self.media_processor.crop_image_to_tiles(media_path, width, height)
        elif media_path.lower().endswith((".mp4", ".mov", ".webm")):
            directory = await self.media_processor.crop_video_to_webm_tiles(media_path, width, height)
        else:
            raise ValueError("Неподдерживаемый тип медиа")
        progress += 1
        logger.info(f"[PackGenerator] Нарезка завершена: {directory}")

        # Step 3: Генерация эмодзи
        await update_status("🎨 Генерация эмодзи...")
        emojis = await self.emoji_creator.create_from_directory(directory, format.value)
        progress += 1

        # Step 4: Создание стикерпакета
        await update_status("🧱 Создание эмодзи-пака...")
        link = await self.sticker_manager.create_sticker_set(
            user_id=user_id,
            emojis=emojis,
            sticker_format=format.value,
            referral_bot_name=referral_bot_name
        )
        if not link:
            raise RuntimeError("Не удалось создать эмодзи-пак")
        progress += 1

        # Step 5: Очистка
        await update_status("🧹 Очистка временных файлов...")
        self.media_processor.cleanup_media(directory)
        progress += 1

        # Step 6: Отправка сетки
        await update_status("📤 Отправляем полный пак...")
        try:
            await self.emoji_sender.send_emoji(
                user_id=user_id,
                bot=self.bot,
                short_name=link,
                rows=int(height / 100),
                cols=int(width / 100)
            )
        except Exception as e:
            logger.error(f"[PackGenerator] ⚠️ Не удалось отправить emoji-сетку: {e}")
        progress += 1

        duration = time.time() - created

        text = (
            "✅ Эмодзи-пак создан!",
            f"⏱️ Время: {duration:.2f} сек",
            f"⚙️ Размер: {int(width / 100)}x{int(height / 100)}"
        )

        await self.bot.edit_message_text(
            chat_id=user_id,
            message_id=message.message_id,
            text="\n".join(text)
        )

        logger.info(f"[PackGenerator] ✅ Пак создан за {duration:.2f} сек")
        return f"https://t.me/addemoji/{link}", duration