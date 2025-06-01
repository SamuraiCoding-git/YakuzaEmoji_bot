from typing import List, Optional

from sqlalchemy import select, insert, distinct
from api.infrastructure.database.models import Product, UserSubscription
from api.infrastructure.database.repo.base import BaseRepo


class ProductRepo(BaseRepo):
    async def create_product(
        self,
        name: str,
        product_type: str,
        price: int,
        duration: Optional[int],
        access_level: int,
        category_id: int,
        queue_priority: int = 5,
        simultaneous_packs: int = 1,
        gate_bot_access: bool = False,
        gate_bot_customization: bool = False,
        personal_bot_enabled: bool = False,
        broadcast_enabled: bool = False,
        lifetime_broadcast_enabled: bool = False,
        bonus_days: int = 0,
        is_lifetime: bool = False,
    ) -> Product:
        insert_stmt = (
            insert(Product)
            .values(
                product_name=name,
                product_type=product_type,
                price=price,
                duration=duration,
                access_level=access_level,
                category_id=category_id,
                queue_priority=queue_priority,
                simultaneous_packs=simultaneous_packs,
                gate_bot_access=gate_bot_access,
                gate_bot_customization=gate_bot_customization,
                personal_bot_enabled=personal_bot_enabled,
                broadcast_enabled=broadcast_enabled,
                lifetime_broadcast_enabled=lifetime_broadcast_enabled,
                bonus_days=bonus_days,
                is_lifetime=is_lifetime,
            )
            .returning(Product)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return await self.session.get(Product, product_id)

    async def get_all_products(self) -> List[Product]:
        result = await self.session.execute(select(Product))
        return result.scalars().all()

    async def update_product_price(self, product_id: int, new_price: int) -> Optional[Product]:
        product = await self.get_product_by_id(product_id)
        if product:
            product.price = new_price
            await self.session.commit()
            return product
        return None

    async def get_products_by_category(self, category_id: int) -> List[Product]:
        result = await self.session.execute(select(Product).filter_by(category_id=category_id))
        return result.scalars().all()

    async def get_product_by_name(self, name: str) -> Optional[Product]:
        result = await self.session.execute(select(Product).filter_by(product_name=name))
        return result.scalar_one_or_none()

    async def get_active_access_levels(self) -> list[int]:
        stmt = (
            select(distinct(Product.access_level))
            .join(UserSubscription, UserSubscription.product_id == Product.id)
        )
        result = await self.session.execute(stmt)
        return [r[0] for r in result.all()]