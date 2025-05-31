from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, mapped_column
from .base import Base, TimestampMixin, TableNameMixin


class GateBot(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), unique=True, nullable=False)
    token = mapped_column(String(255), nullable=False)
    owner_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = mapped_column(Boolean, default=True, nullable=False, comment="Статус активности Gate-бота (работает/не работает)")

    user_entries = relationship("UserGateEntry", back_populates="gate_bot", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="owned_gate_bots")
