from fastapi import APIRouter, HTTPException
from typing import List

from api.webhook.utils.dependencies import get_repo_instance
from api.schemas.request import ReferralCreateRequest, ReferralTransactionCreateRequest
from api.schemas.response import ReferralResponse, ReferralTransactionResponse, ReferralStatsResponse

referral_router = APIRouter(prefix="/referrals", tags=["Referrals"])


@referral_router.post("/", response_model=ReferralResponse)
async def create_referral(data: ReferralCreateRequest):
    repo = get_repo_instance()

    if await repo.referrals.referral_exists(data.referee_id):
        raise HTTPException(status_code=400, detail="Referral already exists for this user")

    referral = await repo.referrals.create_referral(
        referrer_id=data.referrer_id,
        referee_id=data.referee_id,
        product_id=data.product_id,
        bonus_days_granted=data.bonus_days_granted
    )

    await repo.referral_stats.increment_referrals(data.referrer_id, paid=False, bonus_days=data.bonus_days_granted)
    return referral


@referral_router.get("/referrer/{referrer_id}", response_model=List[ReferralResponse])
async def get_referrals_by_referrer(referrer_id: int):
    repo = get_repo_instance()
    return await repo.referrals.get_referrals_by_referrer(referrer_id)


@referral_router.get("/referee/{referee_id}", response_model=List[ReferralResponse])
async def get_referrals_by_referee(referee_id: int):
    repo = get_repo_instance()
    return await repo.referrals.get_referrals_by_referee(referee_id)


@referral_router.get("/stats/{user_id}", response_model=ReferralStatsResponse)
async def get_referral_stats(user_id: int):
    repo = get_repo_instance()
    stats = await repo.referral_stats.get_stats(user_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    return stats


@referral_router.get("/stats/top", response_model=List[ReferralStatsResponse])
async def get_top_referrers(limit: int = 10):
    repo = get_repo_instance()
    return await repo.referral_stats.get_top_referrers(limit=limit)


@referral_router.post("/transactions", response_model=ReferralTransactionResponse)
async def create_referral_transaction(data: ReferralTransactionCreateRequest):
    repo = get_repo_instance()

    transaction = await repo.referral_transactions.create_transaction(
        referral_user_id=data.referral_user_id,
        referred_user_id=data.referred_user_id,
        product_id=data.product_id,
        amount=data.amount,
        bonus=data.bonus,
        transaction_type=data.transaction_type
    )

    # Обновление статистики
    await repo.referral_stats.increment_referrals(user_id=data.referral_user_id, paid=True, bonus_days=data.bonus)

    # Продление подписки
    from datetime import timedelta
    subscription = await repo.user_subscriptions.get_active_subscription(data.referral_user_id)
    if subscription:
        subscription.expires_at += timedelta(days=data.bonus)
        await repo.session.commit()

    return transaction


@referral_router.get("/transactions/{user_id}", response_model=List[ReferralTransactionResponse])
async def get_user_transactions(user_id: int):
    repo = get_repo_instance()
    return await repo.referral_transactions.get_transactions_for_user(user_id)


@referral_router.get("/transactions/latest/{user_id}", response_model=List[ReferralTransactionResponse])
async def get_latest_transactions(user_id: int, limit: int = 5):
    repo = get_repo_instance()
    return await repo.referral_transactions.get_latest_transactions_for_user(user_id=user_id, limit=limit)