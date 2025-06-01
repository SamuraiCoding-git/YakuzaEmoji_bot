from fastapi import APIRouter, Request, HTTPException
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from api.webhook.utils.dependencies import get_repo_instance
from api.infrastructure.database.models import GateBot
from api.webhook.utils.handlers_gate import setup_handlers_for_bot

bots_router = APIRouter(prefix="/bots", tags=["Bots"])

dispatchers: dict[str, Dispatcher] = {}
bots: dict[str, Bot] = {}


@bots_router.post("/{bot_token}/webhook")
async def telegram_webhook(bot_token: str, request: Request):
    repo = get_repo_instance()
    gate_bot: GateBot | None = await repo.gate_bots.get_by_token(bot_token)

    if not gate_bot or not gate_bot.is_active:
        raise HTTPException(status_code=403, detail="Invalid or inactive bot")

    try:
        json_data = await request.json()
        update = Update.model_validate(json_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid update payload")

    # Создание бота, если его ещё нет
    if bot_token not in bots:
        bots[bot_token] = Bot(token=bot_token, parse_mode="HTML")

    bot = bots[bot_token]

    # Создание диспетчера, если его ещё нет
    if bot_token not in dispatchers:
        dp = Dispatcher()
        setup_handlers_for_bot(dp)
        dispatchers[bot_token] = dp

    dp = dispatchers[bot_token]

    # Обработка события
    await dp.feed_update(bot=bot, update=update)

    return {"status": "ok"}


@bots_router.get("/active")
async def list_active_bots():
    repo = get_repo_instance()
    bots = await repo.gate_bots.get_all_active()
    return [{"id": b.id, "name": b.name, "token": b.token} for b in bots]