"""Результаты обработки вопросов через RAG-пайплайн."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from db.database import Base


class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    question_text = Column(Text, default="")
    product_name = Column(String(500), default="")
    product_description = Column(Text, default="")
    product_id = Column(Integer, nullable=True)
    prompt_id = Column(Integer, nullable=False)

    answer_text = Column(Text, default="")

    is_read = Column(Integer, default=0, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
