import asyncio
import logging
from math import ceil, floor

from telethon.tl.functions.messages import GetStickerSetRequest, InstallStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, DocumentAttributeCustomEmoji

from api.config import load_config
from api.clients.session_manager import SessionManager
from api.services.parse_mode import CustomParseMode

logger = logging.getLogger(__name__)


class EmojiSender:
    def __init__(self, session_manager: SessionManager):
        config = load_config()

        session_dir = config.telegram_api.sessions_dir
        all_sessions = list(session_dir.glob("*.session"))
        premium_sessions = [str(p) for p in all_sessions if p.name.endswith("_premium.session")]

        if not premium_sessions:
            raise RuntimeError("❌ Нет доступных premium сессий (*.session с суффиксом _premium)")

        self.session_manager = session_manager
        self.started = False

    async def send_emoji(self, user_id: int, short_name: str, rows: int, cols: int) -> dict:
        """
        Собирает emoji-сетку и отправляет три отдельных сообщения:
        - с выравниванием по левому краю
        - по центру
        - по правому краю

        Возвращает dict с сообщениями: {"left": msg1, "center": msg2, "right": msg3}
        """
        try:
            grid_variants = await self.build_emoji_grid(short_name, rows, cols)

            client = await self.session_manager.get_premium_client()
            client.client.parse_mode = CustomParseMode('markdown')
            await client.client.get_dialogs()

            await client.client.send_message("@YakuzaEmoji_bot", f"/forward {user_id} {grid_variants['right'].replace(' ', '')}")

            await asyncio.sleep(1)

            for align, title in [
                ("left", "🔹 Выравнивание по левому краю\n"),
                ("center", "🔹 Выравнивание по центру\n"),
                ("right", "🔹 Выравнивание по правому краю\n"),
            ]:
                message = f"{title}\n{grid_variants[align]}"
                await client.client.send_message("@YakuzaEmoji_bot", message)
                logger.info(f"[EmojiSender] ✅ Отправлено: {align}")

            await self.session_manager.release_client(client)
        except Exception as e:
            logger.error(f"[EmojiSender] ❌ Ошибка при отправке emoji-сетки: {e}")
            return {}

    async def build_emoji_grid(self, short_name: str, rows: int, cols: int) -> dict:
        """
        Возвращает три варианта сетки (left, center, right), каждая строка — 15 emoji wide.
        """
        assert cols <= 15, "❌ Максимум 15 колонок для Telegram"

        client = await self.session_manager.get_premium_client()
        client.client.parse_mode = CustomParseMode('markdown')

        try:
            await client.client(InstallStickerSetRequest(
                stickerset=InputStickerSetShortName(short_name),
                archived=True
            ))

            result = await client.client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(short_name),
                hash=0
            ))

            logger.info(f"[EmojiSender] 📦 Emoji-pack: {result.set.title}")
            docs = [
                (doc, next((a for a in doc.attributes if isinstance(a, DocumentAttributeCustomEmoji)), None))
                for doc in result.documents
            ]
            docs = [(doc, attr) for doc, attr in docs if attr]
            lines = []

            count = 0
            for i in range(rows):
                row_docs = docs[count:count + cols]
                count += cols
                if not row_docs:
                    break

                line = [
                    f"[{attr.alt or '😀'}](emoji/{doc.id})"
                    for doc, attr in row_docs
                ]
                lines.append(line)

            def format_line(line: list[str], align: str) -> str:
                pad = 12 - len(line)
                if pad <= 0:
                    return "".join(line)

                blank = "    "  # invisible padding emoji

                if align == "left":
                    return "".join(line + [blank] * ceil(pad))
                elif align == "right":
                    return "".join([blank] * ceil(pad) + line)
                elif align == "center":
                    left_pad = floor(pad) // 2
                    right_pad = ceil(pad) - left_pad
                    return "".join([blank] * left_pad + line + [blank] * right_pad)
                else:
                    raise ValueError(f"Unknown align: {align}")

            return {
                "left": "\n".join(format_line(line, "left") for line in lines),
                "center": "\n".join(format_line(line, "center") for line in lines),
                "right": "\n".join(format_line(line, "right") for line in lines),
            }

        finally:
            await self.session_manager.release_client(client)