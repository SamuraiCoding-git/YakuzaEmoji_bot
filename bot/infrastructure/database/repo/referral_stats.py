from typing import Optional, List

from sqlalchemy import select, insert, desc

from api.infrastructure.database.models import ReferralStats
from api.infrastructure.database.repo.base import BaseRepo


class ReferralStatsRepo(BaseRepo):
    async def get_or_create_stats(self, user_id: int) -> ReferralStats:
        """Получить или создать статистику для пользователя"""
        result = await self.session.execute(
            select(ReferralStats).filter_by(user_id=user_id)
        )
        stats = result.scalar_one_or_none()

        if stats:
            return stats

        insert_stmt = (
            insert(ReferralStats)
            .values(user_id=user_id)
            .returning(ReferralStats)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def increment_referrals(self, user_id: int, paid: bool = False, bonus_days: int = 0) -> ReferralStats:
        """Увеличить общее количество и, при необходимости, оплаченные и бонусы"""
        stats = await self.get_or_create_stats(user_id)

        stats.referrals_total += 1
        if paid:
            stats.referrals_paid += 1
            stats.earned_days += bonus_days

        await self.session.commit()
        return stats

    async def add_bonus_days(self, user_id: int, days: int) -> ReferralStats:
        """Добавить дни без увеличения количества рефералов"""
        stats = await self.get_or_create_stats(user_id)
        stats.earned_days += days
        await self.session.commit()
        return stats

    async def get_stats(self, user_id: int) -> Optional[ReferralStats]:
        """Получить статистику без создания"""
        result = await self.session.execute(
            select(ReferralStats).filter_by(user_id=user_id)
        )
        return result.scalar_one_or_none()

    async def get_top_referrers(self, limit: int = 10, sort_by: str = "referrals_paid") -> List[ReferralStats]:
        """Получить топ рефереров по выбранному критерию"""
        if sort_by not in {"referrals_paid", "earned_days"}:
            raise ValueError("Invalid sort_by field. Must be 'referrals_paid' or 'earned_days'")

        stmt = select(ReferralStats).order_by(desc(getattr(ReferralStats, sort_by))).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()