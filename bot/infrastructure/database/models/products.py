from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from .base import Base, TimestampMixin, TableNameMixin

class Product(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    product_name = mapped_column(String(255), nullable=False)
    product_type = mapped_column(String(50), nullable=False)  # Тип продукта ("подписка", "разовая покупка")
    price = mapped_column(Integer, nullable=False)
    duration = mapped_column(Integer, nullable=True)  # В днях для подписок
    access_level = mapped_column(Integer, nullable=False)  # Уровень доступа
    category_id = mapped_column(Integer, ForeignKey('productcategorys.id'), nullable=False)

    category = relationship("ProductCategory", back_populates="products")
    subscriptions = relationship("UserSubscription", back_populates="product")
    payments = relationship("Payment", back_populates="product")
    transactions = relationship("ReferralTransaction", back_populates="product")
