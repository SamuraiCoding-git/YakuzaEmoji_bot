from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from bot.infrastructure.database.models import GateBot
from bot.infrastructure.database.repo.base import BaseRepo


class GateBotRepo(BaseRepo):
    async def get_by_id(self, gate_bot_id: int) -> Optional[GateBot]:
        return await self.session.get(GateBot, gate_bot_id)

    async def get_by_name(self, name: str) -> Optional[GateBot]:
        result = await self.session.execute(select(GateBot).filter_by(name=name))
        return result.scalar_one_or_none()

    async def create_gate_bot(self, name: str, token: str, owner_id: int) -> GateBot:
        insert_stmt = (
            insert(GateBot)
            .values(name=name, token=token, owner_id=owner_id, is_active=True)
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