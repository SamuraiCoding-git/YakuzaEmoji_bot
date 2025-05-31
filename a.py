import asyncio
from telethon import TelegramClient
from getpass import getpass


async def main():
    print("=== 🔐 Создание Telethon сессии ===")
    api_id = int(input("Введите API ID: ").strip())
    api_hash = input("Введите API Hash: ").strip()
    session_name = input("Введите имя для .session файла: ").strip()

    client = TelegramClient(session_name, api_id, api_hash)

    async with client:
        print("\n📱 Введите номер телефона в формате +1234567890")
        await client.start(phone=lambda: input("Телефон: ").strip(),
                           password=lambda: getpass("Пароль от 2FA (если есть): "))

        me = await client.get_me()
        print(f"\n✅ Успешная авторизация: {me.first_name} (@{me.username}) | Premium: {getattr(me, 'premium', False)}")
        print(f"💾 Сессия сохранена в файле: {session_name}.session")

if __name__ == "__main__":
    asyncio.run(main())