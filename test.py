from aiogram import Bot
from aiogram.types import InputSticker, FSInputFile
from PIL import Image
import asyncio

API_TOKEN = "7848210284:AAG5Rl2npWVYZ5KH2LppClgm3tly7bZyAGA"

async def create_custom_emoji_set(bot: Bot, user_id: int, bot_username: str, sticker_path: str):
    input_sticker = InputSticker(
        sticker=FSInputFile(sticker_path),
        format="static",        # Для PNG
        emoji_list=["😎"],      # Обязательно список эмодзи
    )

    set_name = f"prem_emoji_by_{bot_username}".lower()

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
    input_file = "durov.png"         # Исходный файл

    bot = Bot(token=API_TOKEN)
    user_id = 422999166                 # Твой user_id
    bot_username = await bot.get_me()
    bot_username = bot_username.username # Имя бота без @

    await create_custom_emoji_set(bot, user_id, bot_username, input_file)
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())