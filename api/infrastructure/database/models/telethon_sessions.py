from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class TelethonSession(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    session_name = mapped_column(String(255), unique=True, nullable=False)
    is_active = mapped_column(Boolean, default=True)