from telethon import TelegramClient
from pathlib import Path

class TelethonClientWrapper:
    def __init__(self, session_file: str, api_id: int, api_hash: str):
        self.session_file = Path(session_file)
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient(str(self.session_file), api_id, api_hash)
        self.in_use = False
        self.is_premium = None
        self.is_restricted = False

    async def start(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError(f"❌ Клиент {self.session_file.name} не авторизован")
        me = await self.client.get_me()
        self.is_premium = me.premium
        self.is_restricted = me.restricted

    async def disconnect(self):
        await self.client.disconnect()

    async def is_connected(self) -> bool:
        return self.client.is_connected()

    def __getattr__(self, item):
        return getattr(self.client, item)