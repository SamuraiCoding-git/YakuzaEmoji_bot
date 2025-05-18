from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class AuditLog(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    action_type = mapped_column(String(255), nullable=False)  # Тип действия (например, "создание", "обновление", "удаление")
    action_details = mapped_column(String(255), nullable=True)  # Детали действия
    action_date = mapped_column(DateTime, default=datetime.utcnow)  # Дата и время действия
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)  # Пользователь, совершивший действие

    user = relationship("User", back_populates="audit_logs")
