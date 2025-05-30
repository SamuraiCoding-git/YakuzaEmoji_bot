import logging
import time
from typing import Optional, Callable, Awaitable, Tuple

from stickers.clients.session_manager import SessionManager
from stickers.config import load_config
from stickers.services.emoji_sender import EmojiSender  # ⬅️ Новый импорт
from stickers.services.emoji_uploader import EmojiPackUploader
from stickers.services.media_processor import MediaProcessor

logger = logging.getLogger("PackGenerator")

class PackGenerator:
    def __init__(self):
        self.config = load_config()
        self.media_processor = MediaProcessor(self.config.media.temp_media_dir)
        self.uploader = EmojiPackUploader(
            bot_username=self.config.emoji_uploader.bot_username,
            emoji_list=self.config.emoji_uploader.emoji_list,
            pack_name_prefix=self.config.emoji_uploader.pack_name_prefix,
        )

        session_files = [str(p) for p in self.config.telegram_api.sessions_dir.glob("*.session")]
        self.session_manager = SessionManager(
            session_files=session_files,
            api_id=self.config.telegram_api.api_id,
            api_hash=self.config.telegram_api.api_hash
        )
        self.session_manager_started = False

        self.emoji_sender = EmojiSender(
            session_manager=self.session_manager
        )  # ⬅️ Инициализация emoji sender

    async def generate_pack(
        self,
        media_path: str,
        user_id: int,
        width: int,
        height: int,
        pack_type: str = "static",
        queue_started: Optional[float] = None,
        progress_callback: Optional[Callable[[int, int], Awaitable[None]]] = None
    ) -> tuple[str, float, float | None]:
        created = time.time()
        logger.info(f"[PackGenerator] user_id={user_id} | файл: {media_path} | type={pack_type}")

        if not self.session_manager_started:
            await self.session_manager.start_all()
            self.session_manager_started = True

        # Нарезка на тайлы
        if media_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            tiles_dir = await self.media_processor.crop_image_to_tiles(
                media_path, width, height, progress_callback=progress_callback
            )
        elif media_path.lower().endswith((".mp4", ".mov", ".webm")):
            tiles_dir = await self.media_processor.crop_video_to_webm_tiles(
                media_path, width, height, progress_callback=progress_callback
            )
        else:
            raise ValueError("Неподдерживаемый тип медиа")

        logger.info(f"[PackGenerator] Нарезка завершена: {tiles_dir}")

        client = await self.session_manager.get_client()

        # Загрузка в Telegram
        link = await self.uploader.upload(
            client=client.client,
            user_id=user_id,
            tiles_dir=tiles_dir,
            pack_type=pack_type,
            progress_callback=progress_callback,
        )

        await self.session_manager.release_client(client)
        self.media_processor.cleanup_media(tiles_dir)

        if not link:
            raise RuntimeError("Не удалось создать эмодзи-пак")

        duration = time.time() - created
        queued = created - queue_started if queue_started else None

        logger.info(
            f"[PackGenerator] ✅ Пак создан за {duration:.2f} сек. Очередь: {queued:.2f} сек"
            if queued else f"[PackGenerator] ✅ Пак создан за {duration:.2f} сек"
        )

        short_name = link

        try:
            # 🧱 Собираем и отправляем сетку (3 выравнивания)
            await self.emoji_sender.send_emoji(
                user_id=user_id,
                short_name=short_name,
                rows=int(height / 100),
                cols=int(width / 100)
            )

        except Exception as e:
            logger.error(f"[PackGenerator] ⚠️ Не удалось отправить emoji-сетку: {e}")

        return f"https://t.me/addemoji/{link}", duration, queued