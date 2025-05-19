from sqlalchemy import Integer, String, BIGINT, JSON
from sqlalchemy.testing.schema import mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class Sticker(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    sticker_name = mapped_column(String(255), nullable=False)  # Название стикера
    sticker_type = mapped_column(String(50), nullable=False)  # Тип стикера ("статический", "анимированный")
    file_id = mapped_column(String(255), nullable=False)  # File ID для хранения стикера в Telegram
    user_id = mapped_column(BIGINT, nullable=False)  # Пользователь, который создал стикер
    width = mapped_column(Integer, nullable=True)  # Ширина стикера
    height = mapped_column(Integer, nullable=True)  # Высота стикера
    durations = mapped_column(JSON, nullable=True)  # Длительности: {"queue": float, "creation": float}