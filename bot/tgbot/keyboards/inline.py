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

# def admin_main_keyboard():
#     builder = InlineKeyboardBuilder()
#     builder.button(text="🛍️ Продукты", callback_data="admin_products")
#     builder.button(text="📁 Категории", callback_data="admin_categories")
#     builder.button(text="🤖 Боты", callback_data="admin_bots")
#     builder.button(text="🎟️ Скидки", callback_data="admin_discounts")
#     builder.button(text="📊 Статистика", callback_data="admin_stats")
#     builder.adjust(2)
#     return builder.as_markup()
#
# def back_keyboard():
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
#     ])
#
# def products_list_keyboard(products):
#     builder = InlineKeyboardBuilder()
#     for prod in products:
#         builder.button(
#             text=f"{prod['product_name']} ({prod['price']}₽)",
#             callback_data=f"product_{prod['id']}"
#         )
#     builder.button(text="➕ Добавить продукт", callback_data="add_product")
#     builder.button(text="⬅️ Назад", callback_data="admin_back")
#     builder.adjust(1)
#     return builder.as_markup()
#
# def product_detail_keyboard(product_id):
#     builder = InlineKeyboardBuilder()
#     builder.button(text="💲 Изменить цену", callback_data=f"edit_price_{product_id}")
#     builder.button(text="⬅️ Назад", callback_data="admin_products")
#     builder.adjust(1)
#     return builder.as_markup()
#
# def categories_list_keyboard(categories):
#     builder = InlineKeyboardBuilder()
#     for cat in categories:
#         builder.button(
#             text=cat["category_name"],
#             callback_data=f"category_{cat['id']}"
#         )
#     builder.button(text="➕ Добавить категорию", callback_data="add_category")
#     builder.button(text="⬅️ Назад", callback_data="admin_back")
#     builder.adjust(1)
#     return builder.as_markup()
#
# def audience_main_keyboard():
#     builder = InlineKeyboardBuilder()
#     builder.button(text="✅ По минимальному уровню", callback_data="set_min_access_level")
#     builder.button(text="✅ По списку уровней", callback_data="set_access_levels")
#     builder.button(text="📭 Без подписки", callback_data="set_no_subscription")
#     builder.button(text="💡 Взаимодействовал с кампанией", callback_data="set_interacted")
#     builder.button(text="🛒 Кликал, но не купил", callback_data="set_clicked_not_purchased")
#     builder.button(text="🔢 Лимит рассылки", callback_data="set_limit")
#     builder.button(text="➡️ Далее", callback_data="audience_confirm")
#     builder.button(text="❌ Отмена", callback_data="audience_cancel")
#     builder.adjust(2, 2, 2)
#     return builder.as_markup()
#
# def access_levels_keyboard(
#     levels: list[int],  # Список доступных уровней (например, [1, 6, 12, 99])
#     multi: bool = False,
#     selected: set[int] = None,
# ) -> InlineKeyboardBuilder:
#     selected = selected or set()
#     builder = InlineKeyboardBuilder()
#     for level in sorted(levels):
#         mark = "✅ " if level in selected else ""
#         cb = f"toggle_access_{level}" if multi else f"choose_access_{level}"
#         builder.button(text=f"{mark}Уровень {level}", callback_data=cb)
#     if multi:
#         builder.button(text="Готово", callback_data="access_levels_done")
#     builder.button(text="⬅️ Назад", callback_data="audience_back")
#     builder.adjust(1)
#     return builder.as_markup()

def payment_method_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 USDT (TRC20)", callback_data="pay_usdt_trc20")],
        [InlineKeyboardButton(text="💳 Карта / СБП", callback_data="pay_card")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
    ])

def admin_approve_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить платёж", callback_data=f"approve_payment_{user_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_payment_{user_id}")]
    ])

def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
    ])
