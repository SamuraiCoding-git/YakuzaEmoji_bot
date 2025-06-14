from fastapi import APIRouter, HTTPException
from api.webhook.utils.dependencies import get_repo_instance
from api.config import load_config

config = load_config()
access_router = APIRouter(prefix="/access", tags=["Access"])

@access_router.get("/broadcast/{user_id}", response_model=dict)
async def check_broadcast_access(user_id: int):
    repo = get_repo_instance()

    # Проверка на админа
    if user_id in config.telegram_api.admin_ids:
        return {"access": True}

    # Проверка подписки
    subscriptions = await repo.user_subscriptions.get_by_user_id(user_id)
    for sub in subscriptions:
        if sub.product and (
            (sub.product.duration == 365) or
            (sub.product.is_lifetime) or
            (sub.product.duration is None)  # None = lifetime
        ):
            return {"access": True}

    return {"access": False}