import asyncio
import json
import logging

import aiohttp
import time

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..services.progressbar import generate_progress_bar

from aiogram.exceptions import TelegramBadRequest

async def safe_edit_message_text(bot, url=None, *args, **kwargs):
    try:
        if url:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔰 Добавить пак",
                        url=url
                    )
                ]
            ])
            return await bot.edit_message_text(*args, **kwargs, reply_markup=keyboard)
        else:
            return await bot.edit_message_text(*args, **kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Ничего не меняем — просто пропускаем
            logging.info("💬 Пропущено редактирование: message is not modified")
            return
        raise  # другие ошибки — пробрасываем

async def smooth_progress_updater(bot, chat_id, msg_id, ws_url):
    current = 0.0
    target = 0.0
    started_at = time.time()
    done_event = asyncio.Event()
    final_data = {}
    last_update = time.time()
    predicted_total = 20.0

    async def websocket_listener():
        nonlocal target, final_data, last_update
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                async for msg in ws:
                    data = json.loads(msg.data)
                    print("Data: ", data)

                    new_target = float(data.get("progress", 0))
                    target = max(target, new_target)
                    last_update = time.time()
                    final_data = data

                    if data.get("status") in ["done", "error"]:
                        done_event.set()
                        return

    async def animator():
        nonlocal current, predicted_total
        while True:
            await asyncio.sleep(1)

            if done_event.is_set():
                current = max(current, target, 100.0)

            # адаптивный прирост
            if target - current > 0.0001:
                delta = min((target - current) * 0.5, 5.0)
                current += delta
                current = min(current, target)

                # обновляем предсказанное общее время
                elapsed = time.time() - started_at
                if current > 0:
                    predicted_total = (elapsed / current) * 100
                    eta = max(0, int(predicted_total - elapsed))
                else:
                    eta = 0

                display = generate_progress_bar(current, started_at, eta)
                await safe_edit_message_text(
                    bot=bot,
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=display
                )

            if done_event.is_set():
                status = final_data.get("status")
                if status == "done":
                    await safe_edit_message_text(
                        bot=bot,
                        url=final_data['sticker_pack_url'],
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=f"✅ Пак готов!"
                    )
                elif status == "error":
                    await safe_edit_message_text(
                        bot=bot,
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=f"❌ Ошибка: {final_data.get('message')}"
                    )
                return

    await asyncio.gather(websocket_listener(), animator())
    return final_data.get("sticker_pack_url")