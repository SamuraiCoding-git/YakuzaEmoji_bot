from typing import Optional, List

from sqlalchemy import select, func, insert

from bot.infrastructure.database.models import ReferralTransaction
from bot.infrastructure.database.repo.base import BaseRepo


class ReferralTransactionRepo(BaseRepo):
    async def create_transaction(self, referral_user_id: int, referred_user_id: int, product_id: int, amount: int, bonus: int, transaction_type: str) -> ReferralTransaction:
        insert_stmt = (
            insert(ReferralTransaction)
            .values(referral_user_id=referral_user_id, referred_user_id=referred_user_id, product_id=product_id, amount=amount, bonus=bonus, transaction_type=transaction_type)
            .returning(ReferralTransaction)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_transaction_by_id(self, transaction_id: int) -> Optional[ReferralTransaction]:
        return await self.session.get(ReferralTransaction, transaction_id)

    async def get_transactions_for_user(self, referral_user_id: int) -> List[ReferralTransaction]:
        result = await self.session.execute(select(ReferralTransaction).filter_by(referral_user_id=referral_user_id))
        return result.scalars().all()

    async def get_transactions_for_product(self, product_id: int) -> List[ReferralTransaction]:
        result = await self.session.execute(select(ReferralTransaction).filter_by(product_id=product_id))
        return result.scalars().all()

    async def get_total_revenue_for_product(self, product_id: int) -> int:
        result = await self.session.execute(select(func.sum(ReferralTransaction.amount)).filter_by(product_id=product_id))
        return result.scalar_one() or 0

    async def get_total_bonus_for_user(self, referral_user_id: int) -> int:
        result = await self.session.execute(select(func.sum(ReferralTransaction.bonus)).filter_by(referral_user_id=referral_user_id))
        return result.scalar_one() or 0