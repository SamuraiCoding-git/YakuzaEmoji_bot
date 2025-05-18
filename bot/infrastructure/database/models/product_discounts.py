from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class ProductDiscount(Base, TimestampMixin, TableNameMixin):
    product_id = mapped_column(Integer, ForeignKey('products.id'), nullable=False, primary_key=True)
    discount_id = mapped_column(Integer, ForeignKey('discounts.id'), nullable=False, primary_key=True)

    product = relationship("Product", backref="product_discounts")
    discount = relationship("Discount", backref="product_discounts")
