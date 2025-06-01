from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from api.webhook.utils.dependencies import get_repo_instance


async def send_campaign_messages(
    campaign_id: int,
    token: str,
    data: dict
):
    """
    Отправляет рассылку пользователям по заданной промо-кампании с фильтрами.
    Параметры фильтрации передаются через словарь `data`.
    Поддерживаются:
    - access_levels: List[int]
    - min_access_level: int
    - no_subscription: bool
    - interacted_with_promo_id: int
    - clicked_but_not_purchased: bool
    - limit: int
    """
    repo = get_repo_instance()
    campaign = await repo.promo_campaigns.get_campaign_by_id(campaign_id)

    users = await repo.users.get_users_for_promo(
        access_levels=data.get("access_levels"),
        min_access_level=data.get("min_access_level"),
        no_subscription=data.get("no_subscription", False),
        interacted_with_promo_id=data.get("interacted_with_promo_id"),
        clicked_but_not_purchased=data.get("clicked_but_not_purchased", False),
        limit=data.get("limit")
    )

    bot = Bot(token=token)
    sent_count = 0

    for user in users:
        try:
            text = campaign.message_text
            reply_markup = build_keyboard(campaign.keyboard) if campaign.keyboard else None

            if campaign.media:
                await bot.send_photo(
                    chat_id=user.id,
                    photo=campaign.media,
                    caption=text,
                    reply_markup=reply_markup
                )
            else:
                await bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=reply_markup
                )

            await repo.promo_interactions.log_delivery(
                promo_id=campaign.id,
                user_id=user.id
            )
            sent_count += 1

        except Exception:
            # TODO: логировать ошибку и user.id, если нужно
            continue

    await repo.promo_campaigns.update_total_sent(campaign_id, sent_count)


def build_keyboard(keyboard_data: list[list[dict]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn["text"], url=btn["url"]) for btn in row]
            for row in keyboard_data
        ]
    )