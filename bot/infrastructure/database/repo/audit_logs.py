from typing import List

from sqlalchemy import insert, select

from bot.infrastructure.database.models import AuditLog
from bot.infrastructure.database.repo.base import BaseRepo


class AuditLogRepo(BaseRepo):
    async def create_audit_log(self, user_id: int, action_type: str, action_details: str) -> AuditLog:
        insert_stmt = (
            insert(AuditLog)
            .values(user_id=user_id, action_type=action_type, action_details=action_details)
            .returning(AuditLog)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_audit_logs_for_user(self, user_id: int) -> List[AuditLog]:
        result = await self.session.execute(select(AuditLog).filter_by(user_id=user_id))
        return result.scalars().all()

    async def get_all_audit_logs(self) -> List[AuditLog]:
        result = await self.session.execute(select(AuditLog))
        return result.scalars().all()