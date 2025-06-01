from typing import List

from sqlalchemy import select

from api.infrastructure.database.models import ProductDiscount, Discount
from api.infrastructure.database.repo.base import BaseRepo


class ProductDiscountRepo(BaseRepo):
    async def create_product_discount(self, product_id: int, discount_id: int) -> bool:
        """Создание связи между продуктом и скидкой"""
        product_discount = ProductDiscount(product_id=product_id, discount_id=discount_id)
        self.session.add(product_discount)
        await self.session.commit()
        return True

    async def get_product_discounts(self, product_id: int) -> List[Discount]:
        """Получить скидки для конкретного продукта"""
        result = await self.session.execute(
            select(Discount).join(ProductDiscount).filter(ProductDiscount.product_id == product_id)
        )
        return result.scalars().all()

    async def remove_product_discount(self, product_id: int, discount_id: int) -> bool:
        """Удалить скидку для продукта"""
        product_discount = await self.session.execute(
            select(ProductDiscount).filter_by(product_id=product_id, discount_id=discount_id)
        )
        product_discount = product_discount.scalar_one_or_none()
        if product_discount:
            await self.session.delete(product_discount)
            await self.session.commit()
            return True
        return False