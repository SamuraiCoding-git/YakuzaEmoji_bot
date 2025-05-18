from datetime import datetime
from typing import List, Optional

from sqlalchemy import insert, select

from bot.infrastructure.database.models import Report
from bot.infrastructure.database.repo.base import BaseRepo


class ReportRepo(BaseRepo):
    async def create_report(self, report_name: str, report_type: str, start_date: datetime, end_date: datetime, data: str, user_id: Optional[int] = None) -> Report:
        insert_stmt = (
            insert(Report)
            .values(report_name=report_name, report_type=report_type, start_date=start_date, end_date=end_date, data=data, user_id=user_id)
            .returning(Report)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_report_by_id(self, report_id: int) -> Optional[Report]:
        return await self.session.get(Report, report_id)

    async def get_reports_for_user(self, user_id: int) -> List[Report]:
        result = await self.session.execute(select(Report).filter_by(user_id=user_id))
        return result.scalars().all()

    async def get_all_reports(self) -> List[Report]:
        result = await self.session.execute(select(Report))
        return result.scalars().all()