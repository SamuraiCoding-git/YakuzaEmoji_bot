from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from ..config import Config
from ..filters.subscription import SubscriptionFilter
from ..keyboards.inline import sub_keyboard

channel_router = Router()
channel_router.message.filter(SubscriptionFilter(check_mode=2))
channel_router.callback_query.filter(SubscriptionFilter(check_mode=2))

@channel_router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):
    await call.answer("Вы не подписаны 👺", show_alert=True)

@channel_router.message()
async def channel_sub(message: Message, config: Config):
    photo = "AgACAgQAAxkBAAIBz2gow7zO7PiYFgmVQkinZN-2xPCwAALFxjEbE2hBUZ9eCRaGgrdbAQADAgADeQADNgQ"
    caption = hbold("Подпишись на канал, чтобы использовать бота 🐉")
    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=sub_keyboard(config.misc.channel_username)
    )
