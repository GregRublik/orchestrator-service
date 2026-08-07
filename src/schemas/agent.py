"""Pydantic-схемы для мультиагентного анализа отзывов."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Входная модель отзыва (полный формат из внешней системы)
# ---------------------------------------------------------------------------

class ProductDetails(BaseModel):
    imtId: Optional[int] = None
    nmId: Optional[int] = None
    productName: Optional[str] = ""
    supplierArticle: Optional[str] = ""
    supplierName: Optional[str] = ""
    brandName: Optional[str] = ""
    size: Optional[str] = ""


class ReviewInput(BaseModel):
    """Полная структура отзыва из внешней системы."""

    id: str
    text: str = ""
    pros: str = ""
    cons: str = ""
    productValuation: int = 0
    createdDate: Optional[str] = None
    answer: Optional[str] = None
    state: str = "none"
    productDetails: Optional[ProductDetails] = None
    video: Optional[str] = None
    wasViewed: bool = False
    photoLinks: Optional[list[str]] = None
    userName: str = ""
    orderStatus: Optional[str] = None
    matchingSize: str = ""
    isAbleSupplierFeedbackValuation: bool = True
    supplierFeedbackValuation: int = 0
    isAbleSupplierProductValuation: bool = True
    supplierProductValuation: int = 0
    isAbleReturnProductOrders: bool = True
    returnProductOrdersDate: Optional[str] = None
    bables: Optional[list] = None
    lastOrderShkId: Optional[int] = None
    lastOrderCreatedAt: Optional[str] = None
    color: str = ""
    subjectId: Optional[int] = None
    subjectName: Optional[str] = ""
    parentFeedbackId: Optional[str] = None
    childFeedbackId: Optional[str] = None

    @property
    def product_name(self) -> str:
        if self.productDetails:
            return self.productDetails.productName
        return ""

    @property
    def review_text(self) -> str:
        """Собирает полный текст отзыва для анализа."""
        parts = [self.text]
        if self.pros:
            parts.append(f"Плюсы: {self.pros}")
        if self.cons:
            parts.append(f"Минусы: {self.cons}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Результаты работы агентов
# ---------------------------------------------------------------------------

class SentimentResult(BaseModel):
    """Результат Sentiment Agent."""

    is_positive: bool
    confidence: float
    reasoning: str


class ProblemClassification(BaseModel):
    """Результат Problem Classification Agent."""

    problem_class_id: int
    problem_class_name: str
    confidence: float
    reasoning: str


class RecommendationResult(BaseModel):
    """Результат Recommendation Agent."""

    need_determined: str
    product_ids: list[int] = []
    reasoning: str


# ---------------------------------------------------------------------------
# Состояние агентного пайплайна (для LangGraph)
# ---------------------------------------------------------------------------

class AgentState(BaseModel):
    """Состояние, передаваемое между узлами графа."""

    review: ReviewInput
    sentiment: Optional[SentimentResult] = None
    problem_classification: Optional[ProblemClassification] = None
    recommendation: Optional[RecommendationResult] = None
    generated_response: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Запрос на ручной запуск анализа
# ---------------------------------------------------------------------------

class AnalyzeReviewRequest(BaseModel):
    review: ReviewInput


class AnalyzeReviewResponse(BaseModel):
    review_id: str
    is_positive: Optional[bool] = None
    problem_class: Optional[str] = None
    need_determined: Optional[str] = None
    recommended_products: list[str] = []
    generated_response: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# CRUD схемы для problem_classes и recommendation_products
# ---------------------------------------------------------------------------

class ProblemClassCreate(BaseModel):
    name: str
    description: str = ""


class ProblemClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProblemClassResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationProductCreate(BaseModel):
    name: str
    description: str = ""
    category: str = ""
    brand: str = ""
    price: Optional[float] = None
    target_need: str = ""
    is_active: bool = True


class RecommendationProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    target_need: Optional[str] = None
    is_active: Optional[bool] = None


class RecommendationProductResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    brand: str
    price: Optional[float] = None
    target_need: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# CRUD схемы для review_analyses
# ---------------------------------------------------------------------------

class ReviewAnalysisResponse(BaseModel):
    id: int
    review_id: str
    product_name: Optional[str] = None
    product_valuation: Optional[int] = None
    review_text: str = ""
    is_positive: Optional[bool] = None
    sentiment_reasoning: str = ""
    problem_class_id: Optional[int] = None
    problem_reasoning: str = ""
    recommended_product_ids: list[int] = []
    need_determined: str = ""
    generated_response: str = ""
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewAnalysisUpdate(BaseModel):
    is_read: Optional[bool] = None


# ---------------------------------------------------------------------------
# CRUD схемы для question_answers
# ---------------------------------------------------------------------------

class QuestionAnswerResponse(BaseModel):
    id: int
    question_text: str = ""
    product_name: str = ""
    product_description: str = ""
    product_id: Optional[int] = None
    external_id: Optional[str] = None
    prompt_id: int
    answer_text: str = ""
    is_read: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionAnswerUpdate(BaseModel):
    is_read: Optional[int] = None
