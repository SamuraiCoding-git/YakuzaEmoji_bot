from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from api.infrastructure.database.models import UserGateEntry
from api.infrastructure.database.repo.base import BaseRepo


class UserGateEntryRepo(BaseRepo):
    async def get_by_id(self, entry_id: int) -> Optional[UserGateEntry]:
        return await self.session.get(UserGateEntry, entry_id)

    async def get_entries_by_user_id(self, user_id: int) -> List[UserGateEntry]:
        result = await self.session.execute(select(UserGateEntry).filter_by(user_id=user_id))
        return result.scalars().all()

    async def update_or_create_transition_by_user(
            self,
            user_id: int,
            gate_bot_id: int,
            has_entered_main_bot: bool = False,
            enter_main_bot_date: datetime | None = None
    ) -> UserGateEntry:
        # Проверяем, есть ли запись для этого пользователя и gate_bot
        result = await self.session.execute(
            select(UserGateEntry)
            .where(
                UserGateEntry.user_id == user_id,
                UserGateEntry.gate_bot_id == gate_bot_id
            )
        )
        entry = result.scalar_one_or_none()

        if entry:
            # Обновляем существующую запись
            entry.has_entered_main_bot = has_entered_main_bot
            entry.enter_main_bot_date = enter_main_bot_date or datetime.utcnow()
        else:
            # Создаём новую запись
            entry = UserGateEntry(
                user_id=user_id,
                gate_bot_id=gate_bot_id,
                first_touch_date=datetime.utcnow(),
                has_entered_main_bot=has_entered_main_bot,
                enter_main_bot_date=enter_main_bot_date or datetime.utcnow()
            )
            self.session.add(entry)

        await self.session.commit()
        await self.session.refresh(entry)
        return entry