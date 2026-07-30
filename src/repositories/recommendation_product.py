"""Репозиторий для RecommendationProduct."""

from repositories.base import SQLAlchemyRepository
from models.recommendation_product import RecommendationProduct


class RecommendationProductRepository(SQLAlchemyRepository):
    model = RecommendationProduct
