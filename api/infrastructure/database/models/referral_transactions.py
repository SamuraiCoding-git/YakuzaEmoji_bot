from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from .base import Base, TimestampMixin, TableNameMixin

class ReferralTransaction(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    referral_user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    referred_user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = mapped_column(Integer, ForeignKey('products.id'), nullable=False)
    transaction_date = mapped_column(DateTime, default=datetime.utcnow)
    amount = mapped_column(Integer, nullable=False)
    bonus = mapped_column(Integer, nullable=False)
    transaction_type = mapped_column(String(50), nullable=False)

    referral_user = relationship("User", foreign_keys=[referral_user_id], back_populates="referral_transactions")
    referred_user = relationship("User", foreign_keys=[referred_user_id], back_populates="referred_transactions")
    product = relationship(
        "Product",
        back_populates="transactions",
        foreign_keys=[product_id]
    )
