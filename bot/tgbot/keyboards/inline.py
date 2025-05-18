from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data_factory import SizeOptions
from ..misc.size_options import generate_size_options


def generate_size_options_keyboard(width: int, height: int) -> InlineKeyboardMarkup:
    """
    Создаёт InlineKeyboardBuilder с кнопками для каждого варианта размера.

    :return: InlineKeyboardBuilder с кнопками по одной в ряд (вертикально)

    Args:
        height:
        width:
    """

    options = generate_size_options(width, height)

    builder = InlineKeyboardBuilder()

    for option in options:
        width = option["width"]
        height = option["height"]
        text = f"{int(width / 100)}×{int(height / 100)} 🗡️"
        callback_data = SizeOptions(width=width, height=height).pack()
        builder.button(text=text, callback_data=callback_data)
    builder.adjust(1)

    return builder.as_markup()


def sub_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подписаться на канал 🥷🏻",
                url=f"https://t.me/{channel_username}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Проверить подписку 🉐",
                callback_data="check_sub"
            )
        ]
    ])
    return keyboard

def main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Профиль 👤",
                callback_data="profile"
            )
        ]
    ])
    return keyboard