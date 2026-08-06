"""Схемы для endpoint'ов работы с вопросами."""

from pydantic import BaseModel
from typing import Optional


class CreateQuestionRequest(BaseModel):
    """Минимально необходимые поля для обработки вопроса.
    Оркестратору реально нужны только: вопрос, название товара, описание, ID товара."""

    question: str
    product_name: str
    product_description: str
    product_id: Optional[int] = None

    def to_question_input(self) -> "QuestionInput":
        """Разворачивает минимальную схему в полную QuestionInput."""
        return QuestionInput(
            question=self.question,
            product_name=self.product_name,
            product_description=self.product_description,
            product_id=self.product_id,
        )


class QuestionInput(BaseModel):
    """Полная схема вопроса для передачи воркеру (без prompt_id — он задаётся на уровне воркера)."""

    question: str
    product_name: str
    product_description: str
    product_id: Optional[int] = None


class ResponseQuestion(BaseModel):
    """Ответ после обработки вопроса."""

    result: str | None = None
