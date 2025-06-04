from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column
from .base import Base, TableNameMixin


class ReferralStats(Base, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    referrals_total = mapped_column(Integer, default=0)
    referrals_paid = mapped_column(Integer, default=0)
    earned_days = mapped_column(Integer, default=0)