from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from .base import Base, TimestampMixin, TableNameMixin


class UserSubscription(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    expires_at = mapped_column(DateTime, nullable=True)
    activated_at = mapped_column(DateTime, nullable=False)
    upgraded_from_id = mapped_column(Integer, ForeignKey("products.id"), nullable=True)

    # Связи
    product = relationship("Product", foreign_keys=[product_id])
    upgraded_from = relationship("Product", foreign_keys=[upgraded_from_id])