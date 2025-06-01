from aiogram.fsm.state import StatesGroup, State


class ForwardState(StatesGroup):
    waiting_messages = State()

class AdminStates(StatesGroup):
    main = State()
    products = State()
    categories = State()
    bots = State()
    discounts = State()
    stats = State()
    waiting_product_name = State()
    waiting_category_name = State()
    waiting_bot_token = State()
    waiting_product_price = State()

class BroadcastStates(StatesGroup):
    waiting_text = State()
    waiting_media = State()
    preview = State()


class AudienceSelectionStates(StatesGroup):
    choosing_filters = State()                # Главное меню выбора фильтров
    choosing_min_access_level = State()       # Выбор min access_level (только из существующих, через кнопки)
    choosing_access_levels = State()          # Выбор списка уровней (только из существующих, можно мультивыбор)
    set_no_subscription = State()             # Фильтр "без подписки"
    entering_prev_promo_id = State()          # Ввод promo_id кампании
    set_clicked_not_purchased = State()       # Флаг "кликал, но не купил"
    entering_limit = State()                  # Ввод лимита
    confirm = State()                        # Подтверждение выбранных фильтров
    cancel = State()                         # Отмена выбора


class PaymentStates(StatesGroup):
    choosing_method = State()
    waiting_screenshot = State()
    waiting_comment = State()