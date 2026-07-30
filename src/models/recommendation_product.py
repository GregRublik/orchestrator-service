"""Товары для рекомендаций на положительные отзывы."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from db.database import Base


class RecommendationProduct(Base):
    __tablename__ = "recommendation_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, default="")
    category = Column(String(255), default="")
    brand = Column(String(255), default="")
    price = Column(Float, nullable=True)
    target_need = Column(Text, default="")  # какую потребность закрывает товар
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
