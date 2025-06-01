from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from api.infrastructure.database.models import UserSubscription
from api.infrastructure.database.repo.base import BaseRepo


class UserSubscriptionRepo(BaseRepo):
    async def create_subscription(
        self,
        user_id: int,
        product_id: int,
        expires_at: datetime,
        activated_at: Optional[datetime] = None,
        upgraded_from_id: Optional[int] = None,
    ) -> UserSubscription:
        insert_stmt = (
            insert(UserSubscription)
            .values(
                user_id=user_id,
                product_id=product_id,
                expires_at=expires_at,
                activated_at=activated_at or datetime.utcnow(),
                upgraded_from_id=upgraded_from_id,
            )
            .returning(UserSubscription)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_user_id(self, user_id: int) -> List[UserSubscription]:
        stmt = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        stmt = select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.expires_at.isnot(None),
            UserSubscription.expires_at > datetime.utcnow()
        ).order_by(UserSubscription.expires_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def deactivate_subscription(self, subscription_id: int) -> None:
        stmt = (
            update(UserSubscription)
            .where(UserSubscription.id == subscription_id)
            .values(expires_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_subscription(self, subscription_id: int) -> None:
        stmt = delete(UserSubscription).where(UserSubscription.id == subscription_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_users_with_expired_subscriptions(self) -> List[int]:
        stmt = select(UserSubscription.user_id).where(
            UserSubscription.expires_at.isnot(None),
            UserSubscription.expires_at < datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        return list(set(r[0] for r in result.all()))  # Уникальные user_id