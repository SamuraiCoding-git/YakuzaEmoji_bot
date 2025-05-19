from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class ProductCategory(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    category_name = mapped_column(String(255), unique=True, nullable=False)  # Название категории

    products = relationship("Product", back_populates="category")
