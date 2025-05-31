import asyncio
import logging
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
                client.in_use = False
                self._clients.append(client)
            else:
                logger.warning(f"⚠️ Пропущен невалидный .session файл: {f}")

        if not self._clients:
            raise RuntimeError("❌ Нет ни одного валидного .session файла")

    async def start_all(self):
        await asyncio.gather(*(c.start() for c in self._clients))
        premium_count = sum(1 for c in self._clients if c.is_premium)
        logger.info(f"✅ Запущено {len(self._clients)} клиентов ({premium_count} премиум)")

    async def disconnect_all(self):
        await asyncio.gather(*(c.disconnect() for c in self._clients))
        logger.info("❎ Все клиенты отключены")

    async def get_client(self) -> TelethonClientWrapper:
        """
        Возвращает первый свободный клиент (любой, в том числе non-premium)
        """
        return await self._get_client_internal(premium_only=False)

    async def get_premium_client(self) -> TelethonClientWrapper:
        """
        Возвращает только премиум-клиента
        """
        return await self._get_client_internal(premium_only=True)

    async def _get_client_internal(self, premium_only: bool) -> TelethonClientWrapper:
        async with self._lock:
            for client in self._clients:
                if client.in_use:
                    continue
                if premium_only and not client.is_premium:
                    continue
                try:
                    if not await client.is_connected():
                        await client.start()
                    client.in_use = True
                    logger.info(f"📲 Выдан клиент {client.session_file.name} (premium={client.is_premium})")
                    return client
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось стартовать клиент {client.session_file.name}: {e}")
                    continue
            raise RuntimeError("❌ Нет доступных клиентов" + (" (только премиум)" if premium_only else ""))

    async def release_client(self, client: TelethonClientWrapper):
        client.in_use = False