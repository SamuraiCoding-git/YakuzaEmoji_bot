from aiogram.fsm.state import StatesGroup, State


class ForwardState(StatesGroup):
    waiting_messages = State()