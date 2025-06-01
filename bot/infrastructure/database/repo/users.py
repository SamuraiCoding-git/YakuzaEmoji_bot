from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from api.infrastructure.database.models import User, UserSubscription, PromoInteractionLog, Product
from api.infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def get_user_by_referral_code(self, referral_code: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).filter_by(referral_code=referral_code)
        )
        return result.scalar_one_or_none()

    async def create_user(
            self,
            user_id: int,
            full_name: str,
            is_premium: bool,
            username: Optional[str] = None,
            referred_by: Optional[int] = None,
    ) -> User:
        stmt = (
            insert(User)
            .values(
                user_id=user_id,
                full_name=full_name,
                username=username,
                is_premium=is_premium,
                referred_by=referred_by,
            )
            .on_conflict_do_update(
                index_elements=["user_id"],
                set_={
                    "full_name": full_name,
                    "username": username,
                    "is_premium": is_premium,
                    "referred_by": referred_by,
                },
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_user_referrals(self, user_id: int) -> List[User]:
        result = await self.session.execute(
            select(User).filter_by(referred_by=user_id)
        )
        return result.scalars().all()

    async def update_referral_code(
        self, user_id: int, new_referral_code: str
    ) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if user:
            user.referral_code = new_referral_code
            await self.session.commit()
            return user
        return None

    async def get_all_users(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_users_for_promo(
            self,
            min_access_level: Optional[int] = None,
            access_levels: Optional[List[int]] = None,
            no_subscription: bool = False,
            interacted_with_promo_id: Optional[int] = None,
            clicked_but_not_purchased: bool = False,
            limit: Optional[int] = None
    ) -> List[User]:
        stmt = select(User).distinct()

        # Нет подписки
        if no_subscription:
            stmt = stmt.outerjoin(UserSubscription).where(UserSubscription.id.is_(None))

        # По конкретным access_level
        elif access_levels is not None:
            stmt = (
                stmt.join(UserSubscription)
                .join(Product, UserSubscription.product_id == Product.id)
                .where(Product.access_level.in_(access_levels))
            )

        # По минимальному уровню
        elif min_access_level is not None:
            stmt = (
                stmt.join(UserSubscription)
                .join(Product, UserSubscription.product_id == Product.id)
                .where(Product.access_level >= min_access_level)
            )

        # Взаимодействие с кампанией
        if interacted_with_promo_id is not None:
            stmt = stmt.join(PromoInteractionLog).where(PromoInteractionLog.promo_id == interacted_with_promo_id)

            if clicked_but_not_purchased:
                stmt = stmt.where(
                    PromoInteractionLog.clicked_at.isnot(None),
                    PromoInteractionLog.purchased_at.is_(None)
                )

        # Ограничение и сортировка
        if limit:
            stmt = stmt.limit(limit)
        stmt = stmt.order_by(User.id)

        result = await self.session.execute(stmt)
        return result.scalars().all()