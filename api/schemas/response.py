from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

class GeneratePackResponse(BaseModel):
    success: bool
    link: str

class BotResponse(BaseModel):
    id: int
    name: str
    token: str
    owner_id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class BotListResponse(BaseModel):
    total: int
    items: List[BotResponse]

class ProductResponse(BaseModel):
    id: int
    product_name: str
    product_type: str
    price: int
    duration: Optional[int]
    access_level: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductCategoryResponse(BaseModel):
    id: int
    category_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]


class DiscountResponse(BaseModel):
    id: int
    discount_name: str
    percentage: int  # или float если %
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProductDiscountListResponse(BaseModel):
    product_id: int
    discounts: List[DiscountResponse]

class ReferralResponse(BaseModel):
    id: int
    referrer_id: int
    referee_id: int
    product_id: Optional[int]
    bonus_days_granted: int
    created_at: datetime

    class Config:
        orm_mode = True


class PromoCampaignResponse(BaseModel):
    id: int
    title: str
    message_text: Optional[str]
    media: Optional[dict]
    keyboard: Optional[list]
    total_sent: int
    created_at: datetime

    class Config:
        orm_mode = True


class PromoInteractionResponse(BaseModel):
    promo_id: int
    user_id: int
    clicked_at: Optional[datetime]
    purchased_at: Optional[datetime]
    payment_id: Optional[int]

    class Config:
        orm_mode = True



class ReferralTransactionResponse(BaseModel):
    id: int
    referral_user_id: int
    referred_user_id: int
    product_id: int
    amount: int
    bonus: int
    transaction_type: str
    transaction_date: datetime

    class Config:
        orm_mode = True


class ReferralStatsResponse(BaseModel):
    user_id: int
    referrals_total: int
    referrals_paid: int
    earned_days: int

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    username: Optional[str] = None
    is_premium: bool
    referred_by: Optional[int] = None
    referral_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ReferredUserResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    username: Optional[str]
    is_premium: bool
    referred_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReferralRelationResponse(BaseModel):
    id: int
    referrer_id: int
    referee_id: int
    product_id: Optional[int]
    bonus_days_granted: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
