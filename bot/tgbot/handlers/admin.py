from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("admin"))
async def admin_start(message: Message):
    await message.answer("Привет, админ!")
