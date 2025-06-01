from typing import List

from fastapi import APIRouter, HTTPException, BackgroundTasks

from api.schemas.request import (
    PromoCampaignCreateRequest,
    PromoLogClickRequest,
    PromoLogPurchaseRequest
)
from api.schemas.response import PromoCampaignResponse, PromoInteractionResponse
from api.webhook.utils.dependencies import get_repo_instance
from api.webhook.utils.promo import send_campaign_messages

promo_router = APIRouter(prefix="/promo", tags=["PromoCampaigns"])


# 📤 Создать кампанию
@promo_router.post("/", response_model=PromoCampaignResponse)
async def create_campaign(
    data: PromoCampaignCreateRequest,
    background_tasks: BackgroundTasks,
):
    repo = get_repo_instance()

    campaign = await repo.promo_campaigns.create_campaign(
        title=data.title,
        message_text=data.message_text,
        media=data.media,
        keyboard=data.keyboard,
        total_sent=0
    )

    # ✉️ Запускаем рассылку в фоне, передаём фильтры как словарь
    filter_data = {
        "min_access_level": data.min_access_level,
        "access_levels": data.access_levels,
        "no_subscription": data.no_subscription,
        "interacted_with_promo_id": data.interacted_with_promo_id,
        "clicked_but_not_purchased": data.clicked_but_not_purchased,
        "limit": data.limit,
    }

    background_tasks.add_task(send_campaign_messages, campaign.id, data.token, filter_data)

    return campaign


# 📋 Получить все кампании
@promo_router.get("/", response_model=List[PromoCampaignResponse])
async def list_campaigns(
):
    repo = get_repo_instance()
    return await repo.promo_campaigns.get_all_campaigns()


# 📈 Статистика по кампании
@promo_router.get("/{promo_id}/stats")
async def promo_stats(
    promo_id: int
):
    repo = get_repo_instance()
    campaign = await repo.promo_campaigns.get_campaign_by_id(promo_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {
        "promo_id": promo_id,
        "sent": campaign.total_sent,
        "clicks": await repo.promo_interactions.get_click_count(promo_id),
        "purchases": await repo.promo_interactions.get_purchase_count(promo_id)
    }


# 🖁️ Лог клика
@promo_router.post("/log/click")
async def log_click(
    data: PromoLogClickRequest
):
    repo = get_repo_instance()
    await repo.promo_interactions.log_click(promo_id=data.promo_id, user_id=data.user_id)
    return {"status": "ok"}


# 💳 Лог покупки
@promo_router.post("/log/purchase")
async def log_purchase(
    data: PromoLogPurchaseRequest
):
    repo = get_repo_instance()
    await repo.promo_interactions.log_purchase(
        promo_id=data.promo_id,
        user_id=data.user_id,
        payment_id=data.payment_id
    )
    return {"status": "ok"}


# 📄 Получить все взаимодействия по кампании
@promo_router.get("/{promo_id}/interactions", response_model=List[PromoInteractionResponse])
async def get_all_interactions(
    promo_id: int
):
    repo = get_repo_instance()
    return await repo.promo_interactions.get_all_by_promo(promo_id)
