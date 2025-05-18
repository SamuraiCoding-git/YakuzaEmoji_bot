from typing import List, Optional

from sqlalchemy import select, insert

from bot.infrastructure.database.models import Product
from bot.infrastructure.database.repo.base import BaseRepo


class ProductRepo(BaseRepo):
    async def create_product(self, name: str, product_type: str, price: int, duration: int, access_level: int) -> Product:
        insert_stmt = (
            insert(Product)
            .values(product_name=name, product_type=product_type, price=price, duration=duration, access_level=access_level)
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