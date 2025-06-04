from sqlalchemy import Integer, String, BIGINT, JSON
from sqlalchemy.orm import mapped_column
from .base import Base, TimestampMixin, TableNameMixin

class Sticker(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    sticker_name = mapped_column(String, nullable=False)  # Увеличено с 50 до 255
    sticker_type = mapped_column(String, nullable=False)
    file_id = mapped_column(String, nullable=False)       # Увеличено с 50 до 255
    user_id = mapped_column(BIGINT, nullable=False)
    width = mapped_column(Integer, nullable=True)
    height = mapped_column(Integer, nullable=True)
    durations = mapped_column(JSON, nullable=True)