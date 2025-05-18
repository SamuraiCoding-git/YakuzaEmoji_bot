from typing import Optional

from sqlalchemy import func
from sqlalchemy.future import select

from bot.infrastructure.database.models import Payment
from .base import BaseRepo


class PaymentRepo(BaseRepo):
    async def process_payment(self, user_id: int, product_id: int, amount: int, payment_method: str) -> bool:
        """Обработка платежа"""
        payment = Payment(user_id=user_id, product_id=product_id, amount=amount, payment_method=payment_method)
        self.session.add(payment)
        await self.session.commit()
        return True

    async def refund_payment(self, transaction_id: int) -> bool:
        """Возврат платежа"""
        payment = await self.session.get(Payment, transaction_id)
        if payment:
            payment.status = "failed"
            await self.session.commit()
            return True
        return False

    async def get_payment_status(self, transaction_id: int) -> Optional[str]:
        """Получить статус платежа"""
        payment = await self.session.get(Payment, transaction_id)
        return payment.status if payment else None

    async def get_payments_for_user(self, user_id: int) -> list:
        """Получить все платежи пользователя"""
        result = await self.session.execute(select(Payment).filter_by(user_id=user_id))
        return result.scalars().all()

    async def get_payments_for_product(self, product_id: int) -> list:
        """Получить все платежи для продукта"""
        result = await self.session.execute(select(Payment).filter_by(product_id=product_id))
        return result.scalars().all()

    async def get_total_revenue_for_product(self, product_id: int) -> int:
        """Получить общую выручку по продукту"""
        result = await self.session.execute(select(func.sum(Payment.amount)).filter_by(product_id=product_id))
        return result.scalar_one() or 0