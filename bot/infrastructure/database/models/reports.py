from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class Report(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    report_name = mapped_column(String(255), nullable=False)  # Название отчета
    report_type = mapped_column(String(50), nullable=False)  # Тип отчета (например, "статистика продаж", "активность пользователя")
    start_date = mapped_column(DateTime, nullable=False)  # Начало периода для отчета
    end_date = mapped_column(DateTime, nullable=False)  # Конец периода для отчета
    data = mapped_column(String, nullable=False)  # Данные отчета (в формате JSON или строке)

    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=True)  # Кто создал отчет (опционально)
    user = relationship("User", back_populates="reports")
