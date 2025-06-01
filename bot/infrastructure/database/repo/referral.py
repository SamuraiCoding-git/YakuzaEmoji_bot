from typing import Optional, List

from sqlalchemy import select, insert, func
from sqlalchemy.orm import joinedload

from api.infrastructure.database.models import Referral
from api.infrastructure.database.repo.base import BaseRepo


class ReferralRepo(BaseRepo):
    async def create_referral(
        self,
        referrer_id: int,
        referee_id: int,
        product_id: Optional[int] = None,
        bonus_days_granted: int = 0
    ) -> Referral:
        insert_stmt = (
            insert(Referral)
            .values(
                referrer_id=referrer_id,
                referee_id=referee_id,
                product_id=product_id,
                bonus_days_granted=bonus_days_granted,
            )
            .returning(Referral)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_referral_by_id(self, referral_id: int) -> Optional[Referral]:
        return await self.session.get(Referral, referral_id)

    async def get_referrals_by_referrer(self, referrer_id: int) -> List[Referral]:
        result = await self.session.execute(
            select(Referral)
            .filter_by(referrer_id=referrer_id)
            .options(joinedload(Referral.referee), joinedload(Referral.product))
        )
        return result.scalars().all()

    async def get_referrals_by_referee(self, referee_id: int) -> List[Referral]:
        result = await self.session.execute(
            select(Referral)
            .filter_by(referee_id=referee_id)
            .options(joinedload(Referral.referrer), joinedload(Referral.product))
        )
        return result.scalars().all()

    async def get_total_bonus_days_for_user(self, referrer_id: int) -> int:
        result = await self.session.execute(
            select(func.sum(Referral.bonus_days_granted)).filter_by(referrer_id=referrer_id)
        )
        return result.scalar_one() or 0

    async def referral_exists(self, referee_id: int) -> bool:
        result = await self.session.execute(
            select(Referral).filter_by(referee_id=referee_id)
        )
        return result.first() is not None