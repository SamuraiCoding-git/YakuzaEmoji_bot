from typing import Optional, List

from sqlalchemy import insert, select

from api.infrastructure.database.models import ProductCategory, Product
from api.infrastructure.database.repo.base import BaseRepo


class ProductCategoryRepo(BaseRepo):
    async def create_category(self, category_name: str) -> ProductCategory:
        insert_stmt = (
            insert(ProductCategory)
            .values(category_name=category_name)
            .returning(ProductCategory)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_category_by_id(self, category_id: int) -> Optional[ProductCategory]:
        return await self.session.get(ProductCategory, category_id)

    async def get_all_categories(self) -> List[ProductCategory]:
        result = await self.session.execute(select(ProductCategory))
        return result.scalars().all()

    async def assign_category_to_product(self, product_id: int, category_id: int) -> bool:
        product = await self.session.get(Product, product_id)
        if product:
            product.category_id = category_id
            await self.session.commit()
            return True
        return False