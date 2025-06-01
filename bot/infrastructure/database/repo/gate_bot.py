from typing import Optional, List

from sqlalchemy import select, and_, update
from sqlalchemy.dialects.postgresql import insert

from api.infrastructure.database.models import GateBot
from api.infrastructure.database.repo.base import BaseRepo


class GateBotRepo(BaseRepo):
    async def get_by_id(self, gate_bot_id: int) -> Optional[GateBot]:
        return await self.session.get(GateBot, gate_bot_id)

    async def get_by_name(self, name: str) -> Optional[GateBot]:
        result = await self.session.execute(select(GateBot).filter_by(name=name))
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Optional[GateBot]:
        result = await self.session.execute(select(GateBot).filter_by(token=token))
        return result.scalar_one_or_none()

    async def create_gate_bot(
        self,
        name: str,
        token: str,
        owner_id: int,
        main_bot_url: str,
        owner_channel_url: str | None = None,
        welcome_payload: dict | None = None
    ) -> GateBot:
        if not welcome_payload:
            buttons = []
            if main_bot_url:
                buttons.append({
                    "text": "🔥 Перейти в основной бот",
                    "url": main_bot_url
                })

            if owner_channel_url and owner_channel_url != main_bot_url:
                buttons.append({
                    "text": "📢 Подписаться на канал",
                    "url": owner_channel_url
                })

            welcome_payload = {
                "text": (
                    "👋 Добро пожаловать!\n\n"
                    "Ты на правильном пути — впереди полезные инструменты, закрытые материалы и постоянный рост.\n\n"
                    "👇 Жми на кнопку и погнали!"
                ),
                "buttons": buttons
            }

        insert_stmt = (
            insert(GateBot)
            .values(
                name=name,
                token=token,
                owner_id=owner_id,
                is_active=True,
                main_bot_url=main_bot_url,
                welcome_payload=welcome_payload
            )
            .returning(GateBot)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_token(self, gate_bot_id: int, new_token: str) -> Optional[GateBot]:
        gate_bot = await self.get_by_id(gate_bot_id)
        if gate_bot:
            gate_bot.token = new_token
            gate_bot.is_active = True  # При обновлении токена считаем бот активным
            await self.session.commit()
            return gate_bot
        return None

    async def deactivate_gate_bot(self, gate_bot_id: int) -> Optional[GateBot]:
        gate_bot = await self.get_by_id(gate_bot_id)
        if gate_bot:
            gate_bot.is_active = False
            await self.session.commit()
            return gate_bot
        return None

    async def get_all_active(self) -> List[GateBot]:
        result = await self.session.execute(select(GateBot).filter_by(is_active=True))
        return result.scalars().all()

    async def get_all(self) -> List[GateBot]:
        result = await self.session.execute(select(GateBot))
        return result.scalars().all()

    async def filter_bots(self, owner_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[GateBot]:
        filters = []

        if owner_id is not None:
            filters.append(GateBot.owner_id == owner_id)
        if is_active is not None:
            filters.append(GateBot.is_active == is_active)

        stmt = select(GateBot)
        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_welcome_payload(self, gate_bot_id: int, payload: dict) -> GateBot:
        stmt = (
            update(GateBot)
            .where(GateBot.id == gate_bot_id)
            .values(welcome_payload=payload)
            .returning(GateBot)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()