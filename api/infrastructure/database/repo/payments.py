from typing import Optional, List
from sqlalchemy import func, select, update
from api.infrastructure.database.models import Payment, PaymentStatus
from api.infrastructure.database.repo.base import BaseRepo


class PaymentRepo(BaseRepo):
    async def process_payment(
        self,
        user_id: int,
        product_id: int,
        amount: int,
        payment_method: str,
        status: PaymentStatus = PaymentStatus.completed
    ) -> Payment:
        """Создание нового платежа"""
        payment = Payment(
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            payment_method=payment_method,
            status=status
        )
        self.session.add(payment)
        await self.session.commit()
        return payment

    async def refund_payment(self, transaction_id: int) -> bool:
        """Возврат платежа (отметка как failed)"""
        payment = await self.session.get(Payment, transaction_id)
        if payment and payment.status != PaymentStatus.failed:
            payment.status = PaymentStatus.failed
            await self.session.commit()
            return True
        return False

    async def get_payment_status(self, transaction_id: int) -> Optional[str]:
        """Получить статус по ID"""
        payment = await self.session.get(Payment, transaction_id)
        return payment.status.value if payment else None

    async def get_payments_for_user(self, user_id: int) -> List[Payment]:
        result = await self.session.execute(select(Payment).filter_by(user_id=user_id))
        return result.scalars().all()

    async def get_payments_for_product(self, product_id: int) -> List[Payment]:
        result = await self.session.execute(select(Payment).filter_by(product_id=product_id))
        return result.scalars().all()

    async def get_total_revenue_for_product(self, product_id: int) -> int:
        result = await self.session.execute(
            select(func.sum(Payment.amount)).filter_by(product_id=product_id, status=PaymentStatus.completed)
        )
        return result.scalar_one() or 0