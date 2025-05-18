from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, insert

from bot.infrastructure.database.models import Discount, ProductDiscount
from bot.infrastructure.database.repo.base import BaseRepo


class DiscountRepo(BaseRepo):
    async def create_discount(self, discount_name: str, discount_type: str, discount_value: int, start_date: datetime, end_date: datetime) -> Discount:
        insert_stmt = (
            insert(Discount)
            .values(discount_name=discount_name, discount_type=discount_type, discount_value=discount_value, start_date=start_date, end_date=end_date)
            .returning(Discount)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_active_discounts(self) -> List[Discount]:
        from sqlalchemy import select
        result = await self.session.execute(select(Discount).filter(Discount.end_date >= datetime.utcnow()))
        return result.scalars().all()

    async def get_discount_by_id(self, discount_id: int) -> Optional[Discount]:
        return await self.session.get(Discount, discount_id)

    async def apply_discount_to_product(self, product_id: int, discount_id: int) -> bool:
        product_discount = ProductDiscount(product_id=product_id, discount_id=discount_id)
        self.session.add(product_discount)
        await self.session.commit()
        return True

    async def get_discounts_for_product(self, product_id: int) -> List[Discount]:
        result = await self.session.execute(
            select(Discount).join(ProductDiscount).filter(ProductDiscount.product_id == product_id)
        )
        return result.scalars().all()