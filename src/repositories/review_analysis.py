"""Репозиторий для ReviewAnalysis."""

from repositories.base import SQLAlchemyRepository
from models.review_analysis import ReviewAnalysis


class ReviewAnalysisRepository(SQLAlchemyRepository):
    model = ReviewAnalysis
