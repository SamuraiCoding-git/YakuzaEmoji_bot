import logging

from aiogram import Bot
from aiogram.enums import StickerFormat
from fastapi import APIRouter, HTTPException

from api.schemas.request import GeneratePackRequest
from api.schemas.response import GeneratePackResponse
from api.services.pack_generator import PackGenerator
from api.config import load_config

logging.basicConfig(level=logging.INFO)

stickers_router = APIRouter(prefix="/stickers")
config = load_config(".env")
bot = Bot(config.telegram_api.token)
pack_generator = PackGenerator(
    bot=bot,
    config=config
)

@stickers_router.post("/generate", response_model=GeneratePackResponse)
async def generate_pack(request: GeneratePackRequest):
    try:
        logging.info(f"🔧 Генерация стикерпакета для пользователя: {request.user_id}")

        link, duration = await pack_generator.generate_pack(
            request.user_id,
            request.file_id,
            request.width,
            request.height,
            StickerFormat.STATIC if request.media_type == "photo" else StickerFormat.VIDEO,
            request.referral_bot_name
        )

        logging.info(f"✅ Сгенерировано {int((request.width * request.height) / 10000)} стикеров")

        return GeneratePackResponse(
            success=True,
            link=link
        )

    except Exception as e:
        import traceback
        logging.error(f"❌ Ошибка генерации стикерпака: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to generate sticker pack")
