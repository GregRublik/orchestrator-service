"""Сервис обработки отзывов — точка входа для мультиагентного анализа."""

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.review import CreateReview, ResponseReview
from services.agent_orchestrator import AgentOrchestrator
from config import logger


class ReviewService:
    """Принимает отзыв и запускает мультиагентный конвейер."""

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator

    async def execute(self, review: CreateReview, session: AsyncSession) -> ResponseReview:
        """Прогоняет отзыв через всех агентов и возвращает результат."""
        logger.info("Starting multi-agent analysis for review %s", review.id)

        state = await self.orchestrator.analyze(review, session)

        return ResponseReview(
            review_id=review.id,
            is_positive=state.sentiment.is_positive if state.sentiment else None,
            problem_class=(
                state.problem_classification.problem_class_name
                if state.problem_classification
                else None
            ),
            generated_response=state.generated_response,
        )
