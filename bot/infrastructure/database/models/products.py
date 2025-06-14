from sqlalchemy import Integer, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship, mapped_column
from .base import Base, TimestampMixin, TableNameMixin

class Product(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    product_name = mapped_column(String(255), nullable=False)
    product_type = mapped_column(String(50), nullable=False)  # "subscription", "one_time"
    price = mapped_column(Integer, nullable=False)
    duration = mapped_column(Integer, nullable=True)  # В днях, None = lifetime
    access_level = mapped_column(Integer, nullable=False)
    category_id = mapped_column(Integer, ForeignKey('productcategorys.id'), nullable=False)

    # Преимущества по тарифу
    queue_priority = mapped_column(Integer, nullable=False, default=5)  # 0 = высший
    simultaneous_packs = mapped_column(Integer, default=1)  # Сколько паков одновременно
    gate_bot_access = mapped_column(Boolean, default=False)
    gate_bot_customization = mapped_column(Boolean, default=False)  # Настройка приветствия
    personal_bot_enabled = mapped_column(Boolean, default=False)  # Генерация в своём боте
    broadcast_enabled = mapped_column(Boolean, default=False)     # Рассылка к себе в бота
    lifetime_broadcast_enabled = mapped_column(Boolean, default=False)  # Одноразовая рассылка при lifetime
    bonus_days = mapped_column(Integer, default=0)  # Бонус за апгрейд
    is_lifetime = mapped_column(Boolean, default=False)

    # Связи
    category = relationship("ProductCategory", back_populates="products")
    subscriptions = relationship("UserSubscription", back_populates="product")
    payments = relationship("Payment", back_populates="product")