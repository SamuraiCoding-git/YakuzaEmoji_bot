from sqlalchemy import Integer, String, JSON, Text
from sqlalchemy.orm import relationship, mapped_column

from api.infrastructure.database.models.base import TimestampMixin, TableNameMixin, Base


class PromoCampaign(Base, TimestampMixin, TableNameMixin):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(255), nullable=False)
    message_text = mapped_column(Text, nullable=True)
    media = mapped_column(JSON, nullable=True)  # {"type": "photo", "file_id": "..."}
    keyboard = mapped_column(JSON, nullable=True)  # [{"text": "Купить", "url": "..."}, ...]

    total_sent = mapped_column(Integer, default=0)

    interactions = relationship("PromoInteractionLog", back_populates="promo")