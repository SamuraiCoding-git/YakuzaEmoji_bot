import re
import traceback

import httpx
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold, hitalic

from ..config import Config
from ..keyboards.callback_data_factory import SizeOptions
from ..keyboards.inline import generate_size_options_keyboard
from ..misc.states import ForwardState
from ..services.api import APIClient

user_router = Router()
client = APIClient(base_url="http://localhost:8000")
MAX_FILE_SIZE = 15 * 1024 * 1024

# @user_router.message(F.photo)
# async def photo(message: Message):
#     await message.reply(message.photo[-1].file_id)


@user_router.message(Command("forward"))
async def start_forward(message: Message, state: FSMContext):
    await state.set_state(ForwardState.waiting_messages)
    parts = message.text.strip().split(maxsplit=3)
    if len(parts) < 4 or not parts[1].isdigit():
        return await message.answer("⚠️ Используй: /forward {user_id} {pattern} {short_name}")

    user_id = int(parts[1])
    short_name = parts[2]
    pattern_raw = parts[3]
    lines = pattern_raw.strip().split()
    if not lines:
        return await message.answer("⚠️ Укажи хотя бы одну строку эмодзи")

    await state.update_data(
        user_id=user_id,
        short_name=short_name,
        pattern=lines,
        messages={"left": None, "center": None, "right": None}
    )
    await message.answer(f"✅ Готово. Жду 3 сообщения с сеткой для {user_id}")

@user_router.message(ForwardState.waiting_messages)
async def handle_candidate_message(message: Message, state: FSMContext):
    data = await state.get_data()
    content = (message.text or "").strip()

    align = None
    if "по левому краю" in content.lower():
        align = "left"
    elif "по центру" in content.lower():
        align = "center"
    elif "по правому краю" in content.lower():
        align = "right"

    if not align:
        return  # Неизвестный или отсутствующий заголовок

    if data.get("messages", {}).get(align):
        return

    if any(m and m.message_id == message.message_id for m in data.get("messages", {}).values()):
        return

    body = re.split(r"\n{1,2}", content, maxsplit=1)
    if len(body) < 2:
        return await message.reply(f"⚠️ Не могу выделить содержимое сетки ({align})")

    lines = [line.strip() for line in body[1].splitlines() if line.strip()]
    expected = data.get("pattern", [])

    def normalize(lines: list[str]) -> list[str]:
        return [
            "".join(c for c in line if not c.isspace()).strip()
            for line in lines
        ]

    if normalize(lines) != normalize(expected):
        diff = "\n".join(
            f"🔴 Ожидалось: {e}\n🔵 Получено: {l}"
            for e, l in zip(expected, lines)
            if normalize([e])[0] != normalize([l])[0]
        )
        return await message.reply(f"❌ Содержимое не совпадает с паттерном:\n\n{diff}")

    messages = data.get("messages", {})
    messages[align] = message
    await state.update_data(messages=messages)

    await message.reply(f"✅ Принято: {align}")

    updated = await state.get_data()
    messages = updated.get("messages", {})

    if updated.get("done"):
        return

    if all(messages.values()):
        await state.update_data(done=True)
        await message.answer("📤 Все 3 варианта получены. Пересылаю...")

        for align_key in ("left", "center", "right"):
            try:
                await message.bot.forward_message(
                    chat_id=updated["user_id"],
                    from_chat_id=message.chat.id,
                    message_id=messages[align_key].message_id
                )
            except Exception as e:
                await message.reply(f"❌ Ошибка пересылки ({align_key}): {e}")

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Перейти к стикерпаку",
                                      url="https://t.me/addemoji/" + updated["short_name"])]
            ]
        )

        await message.bot.send_message(
            chat_id=updated["user_id"],
            text="✅ Готово! Нажми на кнопку ниже, чтобы открыть стикерпак.",
            reply_markup=keyboard
        )

        await state.clear()

@user_router.message(CommandStart())
async def user_start(message: Message, config: Config, command: CommandObject):
    # repo = await get_repo(config)
    #
    # await repo.users.create_user(
    #     user_id=message.from_user.id,
    #     full_name=message.from_user.full_name,
    #     is_premium=True if message.from_user.is_premium else False,
    #     username=message.from_user.username,
    #     referred_by=command.args
    # )

    caption = (
        hbold(f"💴 Конничива, {message.from_user.first_name}\n"),
        "Отправь фото или видео боту и получи emoji pack ⚔️\n",
    )
    photo = "AgACAgEAAxkBAAIFWGgqNaeGa3aWoFc1ybGIemCPKzQpAAI4sjEb6glRRYk6DU1UChwAAQEAAwIAA3kAAzYE"
    await message.answer_photo(
        photo=photo,
        caption="\n".join(caption)
    )

@user_router.message(F.photo | F.video | F.document)
async def media_handler(message: Message, state: FSMContext):
    media = None
    width = None
    height = None
    media_type = None
    file_id = None

    if message.photo:
        media = message.photo[-1]
        width = media.width
        height = media.height
        media_type = "photo"
        file_id = media.file_id

    elif message.video:
        media = message.video
        width = media.width
        height = media.height
        media_type = "video"
        file_id = media.file_id

    elif message.document:
        doc = message.document
        mime = doc.mime_type or ""
        is_image = mime.startswith("image/")
        is_video = mime.startswith("video/")

        if not (is_image or is_video):
            return await message.answer("⚠️ Только изображения или видео поддерживаются как файлы.")

        if doc.file_size > MAX_FILE_SIZE:
            return await message.answer("⚠️ Размер файла превышает лимит (15MB).")

        width = doc.thumbnail.width
        height = doc.thumbnail.height
        media_type = "photo" if is_image else "video"
        file_id = doc.file_id

    else:
        return await message.answer("⚠️ Не удалось определить тип медиа.")

    if not (width and height and file_id):
        return await message.answer("⚠️ Не удалось определить размер или file_id.")

    await state.update_data(media_type=media_type, file_id=file_id)

    keyboard = generate_size_options_keyboard(width, height)

    text = (
        f"Выбери размер нарезки для {'фото' if media_type == 'photo' else 'видео'}:\n",
        "Например:\n",
        hitalic("4x4 — 4 эмодзи в ширину и 4 в высоту")
    )

    if len(keyboard.inline_keyboard) == 0:
        text = (
            hbold(f"Неподходящие размеры {'фото' if media_type == 'photo' else 'видео'}\n"),
            "Отправьте другое\n",
        )
    await message.answer("\n".join(text), reply_markup=keyboard)


@user_router.callback_query(SizeOptions.filter())
async def size_options_handler(call: CallbackQuery, callback_data: SizeOptions, state: FSMContext, config: Config):
    data = await state.get_data()
    file_id = data.get("file_id")
    media_type = data.get("media_type")
    user_id = call.from_user.id
    width = callback_data.width
    height = callback_data.height

    await call.message.delete()

    if not file_id or not media_type:
        await call.answer("❌ Недостаточно данных для генерации", show_alert=True)
        return

    payload = {
        "file_id": file_id,
        "media_type": media_type,
        "width": width,
        "height": height,
        "user_id": user_id,
    }

    try:
         await client.post_json("stickers/generate", payload)
    except httpx.HTTPStatusError as e:
        await call.message.answer(f"❌ Сервер вернул ошибку: {e.response.text}")
    except Exception:
        tb = traceback.format_exc()
        print(tb)

@user_router.callback_query(F.data == "check_sub")
async def check_sub(call: CallbackQuery, config: Config, state: FSMContext):
    data = await state.get_data()
    # repo = await get_repo(config)
    #
    # await repo.users.create_user(
    #     user_id=call.message.chat.id,
    #     full_name=call.message.chat.full_name,
    #     is_premium=bool(data.get("referred_by")),
    #     username=call.message.chat.username,
    #     referred_by=data.get("referred_by")
    # )

    caption = (
        hbold(f"💴 Конничива, {call.message.chat.first_name}\n"),
        "Отправь фото или видео боту и получи emoji pack ⚔️\n",
    )
    photo = "AgACAgEAAxkBAAIFWGgqNaeGa3aWoFc1ybGIemCPKzQpAAI4sjEb6glRRYk6DU1UChwAAQEAAwIAA3kAAzYE"
    await call.message.answer_photo(
        photo=photo,
        caption="\n".join(caption)
    )
