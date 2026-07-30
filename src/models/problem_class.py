"""Классы проблем товара (доставка, качество, упаковка и т.д.)."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from db.database import Base


class ProblemClass(Base):
    __tablename__ = "problem_classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("ReviewAnalysis", back_populates="problem_class")
