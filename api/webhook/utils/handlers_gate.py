from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from api.webhook.utils.dependencies import get_repo_instance


def setup_handlers_for_bot(router: Router):
    @router.message(CommandStart())
    async def handle_start_plain(message: Message):
        repo = get_repo_instance()
        user_id = message.from_user.id
        gate_bot = await repo.gate_bots.get_by_token(message.bot.token)

        await repo.user_gate_entries.update_or_create_transition_by_user(
            user_id=user_id,
            gate_bot_id=gate_bot.id,
        )

        welcome = gate_bot.welcome_payload or {}
        text = welcome.get("text", "👋 Добро пожаловать!")
        keyboard_data = welcome.get("buttons", [])
        reply_markup = build_keyboard(keyboard_data) if keyboard_data else None

        await message.answer(text, reply_markup=reply_markup)


def build_keyboard(keyboard_data: list[dict]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn["text"], url=btn["url"])] for btn in keyboard_data
        ]
    )