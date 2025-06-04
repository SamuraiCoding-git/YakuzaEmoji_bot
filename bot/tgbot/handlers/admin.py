from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..filters.admin import AdminFilter
from ..services.api import APIClient

from ..misc.states import AdminStates

admin_router = Router()
admin_router.message.filter(AdminFilter())
api = APIClient("http://localhost:8000/admin")

# ========== Главная ==========
@admin_router.message(Command("admin"))
async def admin_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.main)
    await message.answer(
        "Добро пожаловать в админ-панель!",
        reply_markup=admin_main_keyboard()
    )

@admin_router.callback_query(F.data == "admin_back")
async def admin_back_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.main)
    await call.message.edit_text(
        "Главное меню админки",
        reply_markup=admin_main_keyboard()
    )

# ========== Продукты ==========

@admin_router.callback_query(F.data == "admin_products")
async def admin_products_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.products)
    products = await api.get("/products") or []
    await call.message.edit_text(
        "🛍️ Список продуктов:",
        reply_markup=products_list_keyboard(products)
    )

# [Эндпоинт] /admin/products (POST) — создать продукт
@admin_router.callback_query(F.data == "add_product")
async def add_product_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_product_name)
    await call.message.edit_text("Введите название продукта:", reply_markup=back_keyboard())

@admin_router.message(AdminStates.waiting_product_name)
async def waiting_product_price(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text)
    await state.set_state(AdminStates.waiting_product_price)
    await message.answer("Укажите цену в рублях:", reply_markup=back_keyboard())

@admin_router.message(AdminStates.waiting_product_price)
async def save_new_product(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Некорректная цена. Введите целое число:")
        return
    data = await state.get_data()
    payload = {
        "product_name": data["product_name"],
        "product_type": "subscription",  # по дефолту, можно добавить выбор типа через FSM
        "price": price,
        "duration": 30,
        "access_level": 1,
        "category_id": 1  # тоже можно выбирать
    }
    product = await api.post("/products", json=payload)
    await state.set_state(AdminStates.products)
    await message.answer(
        f"✅ Продукт {product['product_name']} ({product['price']}₽) добавлен!",
        reply_markup=admin_main_keyboard()
    )

# [Эндпоинт] /admin/products (GET) — получить все продукты (кнопка "Список продуктов")
@admin_router.callback_query(F.data.startswith("product_"))
async def show_product_details(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.replace("product_", ""))
    product = await api.get(f"/products/{product_id}")
    if not product:
        await call.message.edit_text("❌ Продукт не найден.", reply_markup=back_keyboard())
        return
    await call.message.edit_text(
        f"<b>{product['product_name']}</b>\n"
        f"Цена: {product['price']}₽\n"
        f"Тип: {product['product_type']}\n"
        f"Дней: {product['duration']}\n"
        f"Уровень доступа: {product['access_level']}",
        reply_markup=product_detail_keyboard(product['id'])
    )

# [Эндпоинт] /admin/products/{product_id}/price (PATCH) — обновить цену
@admin_router.callback_query(F.data.startswith("edit_price_"))
async def edit_product_price_start(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.replace("edit_price_", ""))
    await state.update_data(product_id=product_id)
    await state.set_state(AdminStates.waiting_product_price)
    await call.message.edit_text("Введите новую цену для продукта:", reply_markup=back_keyboard())

@admin_router.message(AdminStates.waiting_product_price)
async def update_product_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Некорректная цена. Введите целое число:")
        return
    data = await state.get_data()
    product_id = data.get("product_id")
    product = await api.patch(f"/products/{product_id}/price", params={"new_price": price})
    await state.set_state(AdminStates.products)
    await message.answer(
        f"✅ Цена продукта обновлена: {product['product_name']} ({product['price']}₽)",
        reply_markup=admin_main_keyboard()
    )

# [Эндпоинт] /admin/products/{product_id} (GET) — получить продукт по ID
# (см. show_product_details выше)

# [Эндпоинт] /admin/products/by-category/{category_id} (GET) — продукты по категории
# можно добавить по желанию через FSM выбор категории

# ========== Категории ==========

@admin_router.callback_query(F.data == "admin_categories")
async def admin_categories_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.categories)
    categories = await api.get("/categories") or []
    await call.message.edit_text(
        "📁 Список категорий:",
        reply_markup=categories_list_keyboard(categories)
    )

# [Эндпоинт] /admin/categories (POST) — создать категорию
@admin_router.callback_query(F.data == "add_category")
async def add_category_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_category_name)
    await call.message.edit_text("Введите название категории:", reply_markup=back_keyboard())

@admin_router.message(AdminStates.waiting_category_name)
async def save_new_category(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Введите непустое название!")
        return
    payload = {"category_name": name}
    category = await api.post("/categories", json=payload)
    await state.set_state(AdminStates.categories)
    await message.answer(
        f"✅ Категория <b>{category['category_name']}</b> добавлена!",
        reply_markup=admin_main_keyboard()
    )

# [Эндпоинт] /admin/categories (GET) — получить все категории
# (см. admin_categories_handler выше)

# [Эндпоинт] /admin/categories/{category_id} (GET) — получить категорию по ID
@admin_router.callback_query(F.data.startswith("category_"))
async def show_category_details(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.replace("category_", ""))
    category = await api.get(f"/categories/{category_id}")
    await call.message.edit_text(
        f"Категория: <b>{category['category_name']}</b>",
        reply_markup=back_keyboard()
    )

# ========== Боты ==========

@admin_router.callback_query(F.data == "admin_bots")
async def admin_bots_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.bots)
    # [Эндпоинт] /admin/bots/filter (POST)
    # Для примера: отобразить список ботов, создать/удалить/остановить и т.д.
    await call.message.edit_text(
        "Управление ботами (создать/удалить/остановить/включить)",
        reply_markup=back_keyboard()
    )

# ========== Скидки ==========

@admin_router.callback_query(F.data == "admin_discounts")
async def admin_discounts_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.discounts)
    await call.message.edit_text(
        "Управление скидками (назначить, добавить)",
        reply_markup=back_keyboard()
    )

# ========== Статистика ==========

@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(call: CallbackQuery, state: FSMContext):
    products = await api.get("/products") or []
    top = sorted(products, key=lambda p: p["price"], reverse=True)[:3]
    txt = "\n".join([f"#{i+1}. {p['product_name']} ({p['price']}₽)" for i, p in enumerate(top)])
    await state.set_state(AdminStates.stats)
    await call.message.edit_text(f"📊 TOP продукты:\n{txt}", reply_markup=back_keyboard())

# =======================
# Клавиатуры
# =======================

def admin_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍️ Продукты", callback_data="admin_products")
    builder.button(text="📁 Категории", callback_data="admin_categories")
    builder.button(text="🤖 Боты", callback_data="admin_bots")
    builder.button(text="🎟️ Скидки", callback_data="admin_discounts")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.adjust(2)
    return builder.as_markup()

def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])

def products_list_keyboard(products):
    builder = InlineKeyboardBuilder()
    for prod in products:
        builder.button(
            text=f"{prod['product_name']} ({prod['price']}₽)",
            callback_data=f"product_{prod['id']}"
        )
    builder.button(text="➕ Добавить продукт", callback_data="add_product")
    builder.button(text="⬅️ Назад", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()

def product_detail_keyboard(product_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="💲 Изменить цену", callback_data=f"edit_price_{product_id}")
    builder.button(text="⬅️ Назад", callback_data="admin_products")
    builder.adjust(1)
    return builder.as_markup()

def categories_list_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=cat["category_name"],
            callback_data=f"category_{cat['id']}"
        )
    builder.button(text="➕ Добавить категорию", callback_data="add_category")
    builder.button(text="⬅️ Назад", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()