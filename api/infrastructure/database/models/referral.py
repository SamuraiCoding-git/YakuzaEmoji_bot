from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, mapped_column

from api.infrastructure.database.models.base import TimestampMixin, TableNameMixin, Base


class Referral(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    referrer_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    referee_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    bonus_days_granted = mapped_column(Integer, default=0)

