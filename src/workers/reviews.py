"""RabbitMQ-воркер для обработки отзывов."""

import sys
import asyncio
import signal

sys.path.append("src/")

from aiohttp import ClientSession

from faststream.rabbit.broker import RabbitBroker
from faststream.rabbit import RabbitMessage

from config import settings, logger
from schemas.review import CreateReview
from queues import reviews_queue
from db.database import async_session_maker

from services.generation import GenerationService
from services.review import ReviewService
from services.agent_orchestrator import AgentOrchestrator

from repositories.problem_class import ProblemClassRepository
from repositories.recommendation_product import RecommendationProductRepository
from repositories.review_analysis import ReviewAnalysisRepository


broker = RabbitBroker(settings.rabbitmq.dsn)


def _build_review_service(http_session: ClientSession) -> ReviewService:
    """Собирает цепочку зависимостей вручную (вне контекста FastAPI)."""
    generation_service = GenerationService(http_session, settings.generation.dsn)

    orchestrator = AgentOrchestrator(
        generation_service=generation_service,
        problem_class_repo=ProblemClassRepository(),
        recommendation_product_repo=RecommendationProductRepository(),
        review_analysis_repo=ReviewAnalysisRepository(),
        prompt_ids={
            "sentiment": settings.agent_prompts.sentiment,
            "problem_classification": settings.agent_prompts.problem_classification,
            "recommendation": settings.agent_prompts.recommendation,
            "response": settings.agent_prompts.response,
        },
    )

    return ReviewService(orchestrator=orchestrator)


@broker.subscriber(reviews_queue)
async def reviews(
    data: CreateReview,
    message: RabbitMessage,
):
    """Обрабатывает отзыв через мультиагентный конвейер."""
    async with ClientSession() as http_session:
        review_service = _build_review_service(http_session)

        try:
            async with async_session_maker() as session:
                result = await review_service.execute(data, session)
                logger.info(
                    "Review %s processed: positive=%s, problem=%s",
                    result.review_id, result.is_positive, result.problem_class,
                )
                await message.ack()

        except Exception as e:
            logger.error(
                "Failed to process review %s: %s",
                data.id if hasattr(data, 'id') else 'unknown', e,
            )
            retry_count = int(message.headers.get("x-retry-count", 0))
            if retry_count < 3:
                updated_headers = {**message.headers, "x-retry-count": str(retry_count + 1)}
                await broker.publish(
                    data.model_dump(),
                    queue=reviews_queue,
                    headers=updated_headers,
                    persist=True,
                )
                await message.ack()
            else:
                await message.nack(requeue=False)


async def main():
    stop = asyncio.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())

    async with broker:
        await broker.start()
        await stop.wait()


if __name__ == "__main__":
    asyncio.run(main())
