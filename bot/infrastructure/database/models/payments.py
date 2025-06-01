from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum as PgEnum
from sqlalchemy.orm import relationship, mapped_column
from datetime import datetime
from .base import Base, TimestampMixin, TableNameMixin
import enum

class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class Payment(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = mapped_column(Integer, ForeignKey('products.id'), nullable=False)
    amount = mapped_column(Integer, nullable=False)
    payment_method = mapped_column(String(50), nullable=False)
    status = mapped_column(PgEnum(PaymentStatus, name='payment_status'), default=PaymentStatus.pending)
    transaction_date = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
    product = relationship("Product", back_populates="payments")