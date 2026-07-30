"""Схемы для endpoint'ов работы с отзывами."""

from pydantic import BaseModel

# Переиспользуем полную модель отзыва из agent-схем
from schemas.agent import ReviewInput


class CreateReview(ReviewInput):
    """Принимает полный отзыв из внешней системы (наследует все поля ReviewInput)."""
    pass


class ResponseReview(BaseModel):
    """Ответ после обработки отзыва."""
    review_id: str
    is_positive: bool | None = None
    problem_class: str | None = None
    generated_response: str | None = None
