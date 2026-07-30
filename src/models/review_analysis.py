"""Результаты мультиагентного анализа отзыва."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.database import Base


class ReviewAnalysis(Base):
    __tablename__ = "review_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- Данные отзыва ---
    review_id = Column(String(255), nullable=False, index=True)
    product_name = Column(String(500), nullable=True)
    product_valuation = Column(Integer, nullable=True)
    review_text = Column(Text, default="")

    # --- Sentiment Agent ---
    is_positive = Column(Boolean, nullable=True)
    sentiment_reasoning = Column(Text, default="")

    # --- Problem Classification Agent (негативные) ---
    problem_class_id = Column(
        Integer, ForeignKey("problem_classes.id"), nullable=True
    )
    problem_class = relationship("ProblemClass", back_populates="analyses")
    problem_reasoning = Column(Text, default="")

    # --- Recommendation Agent (позитивные) ---
    recommended_product_ids = Column(JSONB, default=list)  # [1, 3, 5]
    need_determined = Column(Text, default="")

    # --- Финальный ответ ---
    generated_response = Column(Text, default="")

    # --- Статус обработки ---
    is_read = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
