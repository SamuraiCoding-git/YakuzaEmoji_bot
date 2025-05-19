from datetime import datetime

from sqlalchemy import Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from .base import Base, TimestampMixin, TableNameMixin

class UserSubscription(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = mapped_column(Integer, ForeignKey('products.id'), nullable=False)
    start_date = mapped_column(DateTime, default=datetime.utcnow)
    end_date = mapped_column(DateTime, nullable=False)
    status = mapped_column(Boolean, default=True)  # Статус подписки
    access_level = mapped_column(Integer, nullable=False)  # Уровень доступа

    user = relationship("User", back_populates="subscriptions")
    product = relationship("Product", back_populates="subscriptions")
