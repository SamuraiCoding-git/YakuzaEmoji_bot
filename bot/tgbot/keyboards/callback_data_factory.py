from aiogram.filters.callback_data import CallbackData


class SizeOptions(CallbackData, prefix='size_options'):
    width: int
    height: int
