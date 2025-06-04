from aiogram.filters import BaseFilter
from aiogram.types import Message
from ..config import Config
import logging

logger = logging.getLogger(__name__)

class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message, config: Config) -> bool:
        user_id = obj.from_user.id
        is_admin = user_id in config.tg_bot.admin_ids
        result = is_admin == self.is_admin
        logger.debug(f"AdminFilter: user_id={user_id}, is_admin={is_admin}, result={result}")
        return result