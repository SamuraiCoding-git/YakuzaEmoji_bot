from aiogram import Router, F
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from ..config import Config
from ..filters.subscription import SubscriptionFilter
from ..keyboards.inline import sub_keyboard

channel_router = Router()
channel_router.message.filter(SubscriptionFilter(check_mode=2))
channel_router.callback_query.filter(SubscriptionFilter(check_mode=2))

@channel_router.message(CommandStart())
async def channel_sub(message: Message, config: Config, state: FSMContext, command: CommandObject):
    await state.update_data(referred_by=command.args)
    await state.update_data(is_premium=True if message.from_user.is_premium else False)
    photo = "AgACAgEAAxkBAAIFWmgqNdpI0Kcl1TJLq1sLYU3ovh32AAI6sjEb6glRRbb7aN3REK06AQADAgADeQADNgQ"
    caption = hbold("Подпишись на канал, чтобы использовать бота 🐉")
    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=sub_keyboard(config.misc.channel_username)
    )

@channel_router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery):
    await call.answer("Вы не подписаны 👺", show_alert=True)

@channel_router.message()
async def channel_sub(message: Message, config: Config, state: FSMContext, command: CommandObject):
    await state.update_data(referred_by=command.args)
    photo = "AgACAgEAAxkBAAIFWmgqNdpI0Kcl1TJLq1sLYU3ovh32AAI6sjEb6glRRbb7aN3REK06AQADAgADeQADNgQ"
    caption = hbold("Подпишись на канал, чтобы использовать бота 🐉")
    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=sub_keyboard(config.misc.channel_username)
    )
