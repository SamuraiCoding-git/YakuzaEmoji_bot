from sqlalchemy import BigInteger, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, mapped_column

from api.infrastructure.database.models import Base
from api.infrastructure.database.models.base import TimestampMixin, TableNameMixin


class PromoInteractionLog(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(BigInteger, primary_key=True)
    promo_id = mapped_column(Integer, ForeignKey("promocampaigns.id"), nullable=False, index=True)
    user_id = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)

    clicked_at = mapped_column(DateTime, nullable=True)
    purchased_at = mapped_column(DateTime, nullable=True)
    payment_id = mapped_column(BigInteger, ForeignKey("payments.id"), nullable=True)

    promo = relationship("PromoCampaign", back_populates="interactions")
    payment = relationship("Payment")