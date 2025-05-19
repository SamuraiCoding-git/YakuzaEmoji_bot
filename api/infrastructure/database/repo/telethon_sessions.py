from sqlalchemy.future import select
from sqlalchemy import insert, update
from typing import Optional, List
from .base import BaseRepo
from api.infrastructure.database.models.telethon_sessions import TelethonSession

class TelethonSessionRepo(BaseRepo):
    async def add_session(self, session_name: str) -> TelethonSession:
        insert_stmt = (
            insert(TelethonSession)
            .values(session_name=session_name)
            .returning(TelethonSession)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_session_by_name(self, session_name: str) -> Optional[TelethonSession]:
        result = await self.session.execute(select(TelethonSession).filter_by(session_name=session_name))
        return result.scalar_one_or_none()

    async def get_all_sessions(self) -> List[TelethonSession]:
        result = await self.session.execute(select(TelethonSession))
        return result.scalars().all()

    async def set_active(self, session_id: int, active: bool) -> bool:
        stmt = (
            update(TelethonSession)
            .where(TelethonSession.id == session_id)
            .values(is_active=active)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def delete_session(self, session_id: int) -> bool:
        session = await self.session.get(TelethonSession, session_id)
        if session:
            await self.session.delete(session)
            await self.session.commit()
            return True
        return False