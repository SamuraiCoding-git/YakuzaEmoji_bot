from typing import Optional, List
from sqlalchemy import select, insert, func

from api.infrastructure.database.models import PromoInteractionLog
from api.infrastructure.database.repo.base import BaseRepo


class PromoInteractionLogRepo(BaseRepo):
    async def log_click(self, promo_id: int, user_id: int) -> None:
        existing = await self.get_by_promo_and_user(promo_id, user_id)
        if not existing:
            stmt = (
                insert(PromoInteractionLog)
                .values(promo_id=promo_id, user_id=user_id, clicked_at=func.now())
            )
            await self.session.execute(stmt)
        else:
            existing.clicked_at = func.now()
        await self.session.commit()

    async def log_purchase(self, promo_id: int, user_id: int, payment_id: int) -> None:
        existing = await self.get_by_promo_and_user(promo_id, user_id)
        if existing:
            existing.purchased_at = func.now()
            existing.payment_id = payment_id
        else:
            stmt = (
                insert(PromoInteractionLog)
                .values(
                    promo_id=promo_id,
                    user_id=user_id,
                    payment_id=payment_id,
                    purchased_at=func.now()
                )
            )
            await self.session.execute(stmt)
        await self.session.commit()

    async def get_by_promo_and_user(self, promo_id: int, user_id: int) -> Optional[PromoInteractionLog]:
        result = await self.session.execute(
            select(PromoInteractionLog).filter_by(promo_id=promo_id, user_id=user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_promo(self, promo_id: int) -> List[PromoInteractionLog]:
        result = await self.session.execute(
            select(PromoInteractionLog).filter_by(promo_id=promo_id)
        )
        return result.scalars().all()

    async def get_click_count(self, promo_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(PromoInteractionLog).where(PromoInteractionLog.promo_id == promo_id, PromoInteractionLog.clicked_at.isnot(None))
        )
        return result.scalar_one() or 0

    async def get_purchase_count(self, promo_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(PromoInteractionLog).where(PromoInteractionLog.promo_id == promo_id, PromoInteractionLog.purchased_at.isnot(None))
        )
        return result.scalar_one() or 0