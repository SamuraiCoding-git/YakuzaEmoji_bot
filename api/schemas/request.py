from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict

from pydantic.v1 import root_validator, HttpUrl


class GeneratePackRequest(BaseModel):
    media_type: Literal["photo", "video", "document"]
    file_id: str
    width: Optional[int] = Field(default=100, ge=100, le=1200)
    height: Optional[int] = Field(default=100, ge=100, le=10000)
    user_id: int
    referral_bot_name: Optional[str] = None
    # priority: int = Field(default=5, ge=0, le=9, description="0 - наивысший, 9 - низший приоритет")


class BotRequest(BaseModel):
    token: str
    owner_id: int
    # main_bot_url: HttpUrl
    owner_channel_url: str = None
    welcome_payload: Optional[dict] = None

    @root_validator(pre=True)
    def set_default_welcome_payload(cls, values):
        if not values.get("welcome_payload") and values.get("main_bot_url"):
            values["welcome_payload"] = {
                "text": "👋 Добро пожаловать! Здесь начинается ваше путешествие.",
                "buttons": [
                    {
                        "text": "🚀 Перейти в основной бот",
                        "url": str(values["main_bot_url"])
                    },
                    {
                        "text": "🚀 Перейти в основной бот",
                        "url": "https://t.me/MatveyDoroshenko"
                    }
                ]
            }
        return values

class BotQueryRequest(BaseModel):
    current_user_id: int
    owner_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductRequest(BaseModel):
    product_name: str = Field(..., max_length=255)
    product_type: str = Field(..., max_length=50)
    price: int = Field(..., ge=0)
    duration: Optional[int] = Field(None, ge=0, description="Для подписок — в днях")
    access_level: int = Field(..., ge=0)
    category_id: int = Field(..., description="ID категории")

class ProductCategoryRequest(BaseModel):
    category_name: str = Field(..., max_length=255)

class DiscountLinkRequest(BaseModel):
    product_id: int
    discount_id: int

class ReferralCreateRequest(BaseModel):
    referrer_id: int
    referee_id: int
    product_id: Optional[int] = None
    bonus_days_granted: int = 0

class PromoCampaignCreateRequest(BaseModel):
    title: str
    message_text: str
    media: Optional[str] = None
    keyboard: Optional[List[List[dict]]] = None
    token: str

    # Фильтры
    min_access_level: Optional[int] = None
    access_levels: Optional[List[int]] = None
    no_subscription: Optional[bool] = False
    interacted_with_promo_id: Optional[int] = None
    clicked_but_not_purchased: Optional[bool] = False
    limit: Optional[int] = None

    @root_validator
    def validate_conflicts(cls, values):
        min_access_level = values.get("min_access_level")
        access_levels = values.get("access_levels")
        no_subscription = values.get("no_subscription")
        clicked = values.get("clicked_but_not_purchased")
        interacted = values.get("interacted_with_promo_id")

        if no_subscription and (min_access_level or access_levels):
            raise ValueError("Нельзя фильтровать одновременно по отсутствию подписки и по access level.")

        if clicked and not interacted:
            raise ValueError("Поле 'clicked_but_not_purchased' требует 'interacted_with_promo_id'.")

        if access_levels and not all(isinstance(x, int) for x in access_levels):
            raise ValueError("Все значения в 'access_levels' должны быть числами.")

        return values

class PromoLogClickRequest(BaseModel):
    promo_id: int
    user_id: int

class PromoLogPurchaseRequest(BaseModel):
    promo_id: int
    user_id: int
    payment_id: int

class ReferralTransactionCreateRequest(BaseModel):
    referral_user_id: int = Field(..., description="ID пользователя, пригласившего друга")
    referred_user_id: int = Field(..., description="ID приглашённого пользователя")
    product_id: int = Field(..., description="ID продукта, по которому была совершена покупка")
    amount: int = Field(..., description="Сумма покупки")
    bonus: int = Field(..., description="Бонусные дни или иная награда")
    transaction_type: str = Field(..., description="Тип транзакции (например: 'purchase', 'upgrade')")

class UserCreateRequest(BaseModel):
    user_id: int
    full_name: str
    username: Optional[str] = None
    is_premium: bool
    referred_by: Optional[int] = None


class GateBotWelcomeUpdateRequest(BaseModel):
    welcome_payload: Dict
