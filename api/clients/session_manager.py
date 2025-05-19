import asyncio
import logging
import random
from typing import List
from pathlib import Path

from api.clients.telethon_client import TelethonClientWrapper

logger = logging.getLogger("SessionManager")


class SessionManager:
    def __init__(self, session_files: List[str], api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self._clients: List[TelethonClientWrapper] = []
        self._lock = asyncio.Lock()

        for f in session_files:
            p = Path(f)
            if p.exists() and p.suffix == ".session":
                client = TelethonClientWrapper(str(p), api_id, api_hash)
                client.in_use = False  # добавляем состояние
                self._clients.append(client)
            else:
                logger.warning(f"⚠️ Пропущен невалидный .session файл: {f}")

        if not self._clients:
            raise RuntimeError("❌ Нет ни одного валидного .session файла")

    async def start_all(self):
        await asyncio.gather(*(c.start() for c in self._clients))
        logger.info(f"✅ Запущено {len(self._clients)} клиентов")

    async def disconnect_all(self):
        await asyncio.gather(*(c.disconnect() for c in self._clients))
        logger.info("❎ Все клиенты отключены")

    async def get_client(self) -> TelethonClientWrapper:
        async with self._lock:
            for client in self._clients:
                if not client.in_use:
                    try:
                        if not await client.is_connected():
                            await client.start()
                        client.in_use = True
                        return client
                    except Exception as e:
                        logger.warning(f"⚠️ Не удалось стартовать клиент {client.session_file.name}: {e}")
                        continue
            raise RuntimeError("❌ Нет доступных клиентов")

    async def get_premium_client(self) -> TelethonClientWrapper:
        """Возвращает случайного доступного premium-клиента (уже запущенного и с is_premium=True)"""
        async with self._lock:
            logger.info("[SessionManager] 🔍 Поиск доступного premium-клиента...")

            for client in self._clients:
                logger.debug(
                    f"[SessionManager] Клиент {client.session_file.name}: "
                    f"is_premium={client.is_premium}"
                )

            premium_candidates = [
                client for client in self._clients
                if not client.in_use and client.is_premium is True
            ]

            logger.info(f"[SessionManager] 🔎 Найдено {len(premium_candidates)} доступных premium-клиентов")

            if not premium_candidates:
                raise RuntimeError("❌ Нет доступных premium клиентов")

            chosen = random.choice(premium_candidates)
            chosen.in_use = True

            logger.info(
                f"[SessionManager] ✅ Выбран premium-клиент: {chosen.session_file.name}"
            )
            return chosen

    async def release_client(self, client: TelethonClientWrapper):
        """Освобождает клиента (можно вызывать после использования)"""
        client.in_use = False
