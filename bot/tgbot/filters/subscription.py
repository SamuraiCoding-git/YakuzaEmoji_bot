from aiogram.filters import BaseFilter
from aiogram.types import Message
from ..config import Config

class SubscriptionFilter(BaseFilter):
    def __init__(self, check_mode=1):
        """
        :param check_mode: Mode of subscription check.
            1 - Check if user is member, admin, or creator.
            2 - Check if user is NOT a subscriber (i.e., non-member).
        """
        self.check_mode = check_mode

    async def __call__(self, obj: Message, config: Config) -> bool:
        user_id = obj.from_user.id

        try:
            member = await obj.bot.get_chat_member(config.misc.channel_id, user_id)

            if self.check_mode == 1:
                # Mode 1: Check if user is a member, administrator, or creator
                if member.status in ['member', 'administrator', 'creator']:
                    return True

            elif self.check_mode == 2:
                # Mode 2: Return True if user is NOT a subscriber (not a member)
                if member.status not in ['member', 'administrator', 'creator']:
                    return True

            return False
        except Exception as e:
            print(f"Error checking subscription: {e}")
            return False