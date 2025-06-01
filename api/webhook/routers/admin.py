import logging
import traceback
from typing import List

from aiogram import Bot
from fastapi import APIRouter, HTTPException

from api.config import load_config
from api.schemas.request import BotRequest, BotQueryRequest, DiscountLinkRequest, ProductCategoryRequest, ProductRequest
from api.schemas.response import BotResponse, BotListResponse, ProductResponse, ProductCategoryResponse
from api.webhook.utils.dependencies import get_repo_instance

logging.basicConfig(level=logging.INFO)

config = load_config()

admin_router = APIRouter(prefix="/admin")

@admin_router.post("/bot", response_model=BotResponse)
async def create_bot(request: BotRequest) -> BotResponse:
    repo = get_repo_instance()
    try:
        # Проверка токена и получение имени бота
        bot = Bot(token=request.token)
        me = await bot.get_me()

        # Валидация: ссылка должна вести на Telegram
        if not str(request.main_bot_url).startswith("https://t.me/"):
            raise HTTPException(status_code=400, detail="main_bot_url должен быть ссылкой на Telegram-бота")

        # Создание гейт-бота
        gate_bot = await repo.gate_bots.create_gate_bot(
            name=me.username,
            token=request.token,
            owner_id=request.owner_id,
            welcome_payload=request.welcome_payload,
            main_bot_url=request.main_bot_url
        )

        return BotResponse(
            id=gate_bot.id,
            name=gate_bot.name,
            token=gate_bot.token,
            owner_id=gate_bot.owner_id,
            is_active=gate_bot.is_active,
            created_at=gate_bot.created_at,
            welcome_payload=gate_bot.welcome_payload,
            main_bot_url=gate_bot.main_bot_url
        )

    except Exception as e:
        logging.error(f"❌ Ошибка создания гейт-бота: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Не удалось создать гейт-бота")



@admin_router.post("/bots/filter", response_model=BotListResponse)
async def filter_bots(
    request: BotQueryRequest
):
    repo = get_repo_instance()
    is_admin = request.current_user_id in config.telegram_api.admin_ids

    if not is_admin:
        if request.owner_id is not None and request.owner_id != request.current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        request.owner_id = request.current_user_id

    bots = await repo.gate_bots.filter_bots(
        owner_id=request.owner_id,
        is_active=request.is_active
    )

    return BotListResponse(
        total=len(bots),
        items=[BotResponse.from_attributes(bot) for bot in bots]
    )

@admin_router.post("/products", response_model=ProductResponse)
async def create_product(
    request: ProductRequest
):
    repo = get_repo_instance()
    product = await repo.products.create_product(
        name=request.product_name,
        product_type=request.product_type,
        price=request.price,
        duration=request.duration,
        access_level=request.access_level,
        category_id=request.category_id
    )
    return ProductResponse.from_attributes(product)

# 📦 Получить все продукты
@admin_router.get("/products", response_model=List[ProductResponse])
async def get_all_products():
    repo = get_repo_instance()
    products = await repo.products.get_all_products()
    return [ProductResponse.from_attributes(p) for p in products]

# 🔍 Получить продукт по ID
@admin_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: int):
    repo = get_repo_instance()
    product = await repo.products.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.from_attributes(product)

# 💸 Обновить цену продукта
@admin_router.patch("/products/{product_id}/price", response_model=ProductResponse)
async def update_product_price(product_id: int, new_price: int):
    repo = get_repo_instance()
    product = await repo.products.update_product_price(product_id, new_price)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.from_attributes(product)

# 📁 Получить продукты по категории
@admin_router.get("/products/by-category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(category_id: int):
    repo = get_repo_instance()
    products = await repo.products.get_products_by_category(category_id)
    return [ProductResponse.from_attributes(p) for p in products]

# 🔍 Поиск по имени
@admin_router.get("/products/by-name/{name}", response_model=ProductResponse)
async def get_product_by_name(name: str):
    repo = get_repo_instance()
    product = await repo.products.get_product_by_name(name)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.from_attributes(product)

# ➕ Создать категорию
@admin_router.post("/categories", response_model=ProductCategoryResponse)
async def create_category(
    request: ProductCategoryRequest
):
    repo = get_repo_instance()
    category = await repo.product_categories.create_category(request.category_name)
    return ProductCategoryResponse.from_attributes(category)

# 📄 Получить все категории
@admin_router.get("/categories", response_model=List[ProductCategoryResponse])
async def get_categories():
    repo = get_repo_instance()
    categories = await repo.product_categories.get_all_categories()
    return [ProductCategoryResponse.from_attributes(cat) for cat in categories]

# 🎯 Получить по ID
@admin_router.get("/categories/{category_id}", response_model=ProductCategoryResponse)
async def get_category(category_id: int):
    repo = get_repo_instance()
    category = await repo.product_categories.get_category_by_id(category_id)
    if not category:
        raise HTTPException(404, detail="Category not found")
    return ProductCategoryResponse.from_attributes(category)

# 🔄 Назначить категорию продукту
@admin_router.patch("/products/{product_id}/category/{category_id}", response_model=bool)
async def assign_category(product_id: int, category_id: int):
    repo = get_repo_instance()
    success = await repo.product_categories.assign_category_to_product(product_id, category_id)
    if not success:
        raise HTTPException(404, detail="Product not found")
    return True

@admin_router.post("/products/discounts", response_model=bool)
async def link_discount(
    request: DiscountLinkRequest
):
    repo = get_repo_instance()
    return await repo.product_discounts.create_product_discount(
        product_id=request.product_id,
        discount_id=request.discount_id
    )

# ❌ Удалить скидку
@admin_router.delete("/products/discounts", response_model=bool)
async def unlink_discount(
    request: DiscountLinkRequest
):
    repo = get_repo_instance()
    return await repo.product_discounts.remove_product_discount(
        product_id=request.product_id,
        discount_id=request.discount_id
    )

# 📦 Получить скидки продукта
@admin_router.get("/products/{product_id}/discounts")
async def get_product_discounts(
    product_id: int
):
    repo = get_repo_instance()
    discounts = await repo.product_discounts.get_product_discounts(product_id)
    return discounts
