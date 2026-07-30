"""Схемы для endpoint'ов работы с отзывами."""

from pydantic import BaseModel

from schemas.agent import ReviewInput


class CreateReviewRequest(BaseModel):
    """Минимально необходимые поля для обработки отзыва.
    Оркестратору реально нужны только: id, текст, оценка, данные о товаре."""

    id: str
    text: str = ""
    pros: str = ""
    cons: str = ""
    productValuation: int = 0
    productName: str = ""
    brandName: str = ""

    def to_review_input(self) -> ReviewInput:
        """Разворачивает минимальную схему в полную ReviewInput."""
        from schemas.agent import ProductDetails

        return ReviewInput(
            id=self.id,
            text=self.text,
            pros=self.pros,
            cons=self.cons,
            productValuation=self.productValuation,
            productDetails=ProductDetails(
                productName=self.productName,
                brandName=self.brandName,
            ),
        )


class CreateReview(ReviewInput):
    """Наследует все поля ReviewInput (совместимость)."""
    pass


class ResponseReview(BaseModel):
    """Ответ после обработки отзыва."""
    review_id: str
    is_positive: bool | None = None
    problem_class: str | None = None
    generated_response: str | None = None
