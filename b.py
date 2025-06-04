import unittest
import datetime
import asyncio
import logging

from aiogram.types import User, Chat, Message
from types import SimpleNamespace

from bot.tgbot.filters.admin import AdminFilter

# Настройка логгера
logger = logging.getLogger("AdminFilterTest")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class TestAdminFilter(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.admin_id = 422999166
        self.non_admin_id = 222222222

        self.config = SimpleNamespace(tg_bot=SimpleNamespace(admin_ids=[self.admin_id]))
        logger.info("Setup complete. Admin ID: %s, Non-admin ID: %s", self.admin_id, self.non_admin_id)

    async def test_admin_passes_filter(self):
        msg = Message(
            message_id=1,
            from_user=User(id=self.admin_id, is_bot=False, first_name="Admin"),
            chat=Chat(id=self.admin_id, type="private"),
            date=datetime.datetime.now(),
            text="/start"
        )

        admin_filter = AdminFilter()
        result = await admin_filter(msg, config=self.config)
        logger.debug("Checking admin_id=%s — result: %s", self.admin_id, result)
        self.assertTrue(result)

    async def test_non_admin_fails_filter(self):
        msg = Message(
            message_id=2,
            from_user=User(id=self.non_admin_id, is_bot=False, first_name="User"),
            chat=Chat(id=self.non_admin_id, type="private"),
            date=datetime.datetime.now(),
            text="/start"
        )

        admin_filter = AdminFilter()
        result = await admin_filter(msg, config=self.config)
        logger.debug("Checking non_admin_id=%s — result: %s", self.non_admin_id, result)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()