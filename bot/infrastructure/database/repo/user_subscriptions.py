from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from bot.infrastructure.database.models import UserSubscription
from bot.infrastructure.database.repo.base import BaseRepo


class UserSubscriptionRepo(BaseRepo):
    async def create_subscription(
        self,
        user_id: int,
        product_id: int,
        end_date: datetime,
        access_level: int,
        status: bool = True,
    ) -> UserSubscription:
        insert_stmt = (
            insert(UserSubscription)
            .values(
                user_id=user_id,
                product_id=product_id,
                end_date=end_date,
                access_level=access_level,
                status=status,
            )
            .returning(UserSubscription)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_user_id(self, user_id: int) -> List[UserSubscription]:
        query = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        query = select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.status == True,
            UserSubscription.end_date > datetime.utcnow()
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def deactivate_subscription(self, subscription_id: int) -> None:
        stmt = (
            update(UserSubscription)
            .where(UserSubscription.id == subscription_id)
            .values(status=False)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_subscription(self, subscription_id: int) -> None:
        stmt = delete(UserSubscription).where(UserSubscription.id == subscription_id)
        await self.session.execute(stmt)
        await self.session.commit()
