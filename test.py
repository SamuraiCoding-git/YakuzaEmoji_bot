from aiogram import Bot
from aiogram.types import InputSticker, FSInputFile
from PIL import Image
import asyncio

API_TOKEN = "7848210284:AAG5Rl2npWVYZ5KH2LppClgm3tly7bZyAGA"

def prepare_sticker(input_path: str, output_path: str):
    img = Image.open(input_path).convert("RGBA")  # Конвертируем с прозрачностью
    img.save(output_path, format="PNG", optimize=True)

async def create_custom_emoji_set(bot: Bot, user_id: int, bot_username: str, sticker_path: str):
    input_sticker = InputSticker(
        sticker=FSInputFile(sticker_path),
        format="static",        # Для PNG
        emoji_list=["😎"],      # Обязательно список эмодзи
    )

    set_name = f"emoji_by_{bot_username}".lower()

    try:
        result = await bot.create_new_sticker_set(
                user_id=user_id,
                name=set_name,
                title="Custom Emoji Sticker Set",
                stickers=[input_sticker],
                sticker_type="custom_emoji",
        )
        if result:
            print("Custom emoji стикерсет создан успешно!")
        else:
            print("Не удалось создать custom emoji стикерсет.")
    except Exception as e:
        print(f"Ошибка: {e}")

async def main():
    input_file = "yakuza.jpg"         # Исходный файл
    output_file = "yakuza_64x64.png"  # Для Telegram

    prepare_sticker(input_file, output_file)

    bot = Bot(token=API_TOKEN)
    user_id = 422999166                 # Твой user_id
    bot_username = "YakuzaEmoji_bot"   # Имя бота без @

    await create_custom_emoji_set(bot, user_id, bot_username, output_file)
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())