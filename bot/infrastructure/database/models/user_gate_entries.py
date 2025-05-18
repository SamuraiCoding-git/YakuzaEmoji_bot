from sqlalchemy import Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, mapped_column
from datetime import datetime
from .base import Base, TimestampMixin, TableNameMixin


class UserGateEntry(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    gate_bot_id = mapped_column(Integer, ForeignKey("gatebots.id"), nullable=False)
    first_touch_date = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    has_entered_main_bot = mapped_column(Boolean, default=False)
    enter_main_bot_date = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="gate_entries")
    gate_bot = relationship("GateBot", back_populates="user_entries")