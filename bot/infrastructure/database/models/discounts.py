from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class Discount(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    discount_name = mapped_column(String(255), unique=True, nullable=False)
    discount_type = mapped_column(String(50), nullable=False)  # Тип скидки ("фиксированная", "процентная")
    discount_value = mapped_column(Integer, nullable=False)  # Значение скидки
    start_date = mapped_column(DateTime, nullable=False)
    end_date = mapped_column(DateTime, nullable=False)
