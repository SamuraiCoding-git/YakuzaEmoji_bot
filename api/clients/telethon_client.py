from pathlib import Path

from requests import session
from telethon import TelegramClient


class TelethonClientWrapper:
    def __init__(self, session_file: str, api_id: int, api_hash: str):
        self.session_file = Path(session_file)
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient(self.session_file.resolve(), self.api_id, self.api_hash)
        self.in_use = False
        self.is_premium = False

    async def start(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError(f"Клиент {self.session_file.stem} не авторизован")

        me = await self.client.get_me()
        self.is_premium = getattr(me, "premium", False)

    async def disconnect(self):
        await self.client.disconnect()

    async def is_connected(self) -> bool:
        return await self.client.is_user_authorized()