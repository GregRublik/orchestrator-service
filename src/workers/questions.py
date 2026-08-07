"""RabbitMQ-воркер для обработки вопросов."""

import sys
import asyncio
import signal

sys.path.append("src/")

from aiohttp import ClientSession

from faststream.rabbit.broker import RabbitBroker
from faststream.rabbit import RabbitMessage

from config import settings, logger
from schemas.question import QuestionInput
from queues import questions_queue
from db.database import async_session_maker
from repositories.question_answer import QuestionAnswerRepository
from services.generation import GenerationService
from services.retrieval import RetrievalService
from services.rag import RagService


broker = RabbitBroker(settings.rabbitmq.dsn)


def _build_rag_service(http_session: ClientSession) -> RagService:
    """Собирает цепочку зависимостей вручную (вне контекста FastAPI)."""
    generation_service = GenerationService(http_session, settings.generation.dsn)
    retrieval_service = RetrievalService(http_session, settings.retrieval.dsn)
    return RagService(generation_service, retrieval_service)


@broker.subscriber(questions_queue)
async def questions(data: dict, message: RabbitMessage):
    """Обрабатывает вопрос через RAG-пайплайн."""
    async with ClientSession() as http_session:
        rag_service = _build_rag_service(http_session)

        try:
            question_input = QuestionInput(**data)
            prompt_id = settings.agent_prompts.questions
            result = await rag_service.questions(question_input, prompt_id)
            logger.info("Question processed: %s -> %s", question_input.question, result.result[:100])

            # Сохраняем результат в БД
            repo = QuestionAnswerRepository()
            async with async_session_maker() as session:
                await repo.add_one(session, {
                    "question_text": question_input.question,
                    "product_name": question_input.product_name,
                    "product_description": question_input.product_description,
                    "product_id": question_input.product_id,
                    "external_id": question_input.id,
                    "prompt_id": prompt_id,
                    "answer_text": result.result,
                })
                await session.commit()
                logger.info("Question answer saved for: %s", question_input.question)

            await message.ack()

        except Exception as e:
            question_id = data.get("question", "unknown") if isinstance(data, dict) else "unknown"
            logger.error("Failed to process question '%s': %s", question_id, e)

            retry_count = int(message.headers.get("x-retry-count", 0))
            if retry_count < 3:
                updated_headers = {**message.headers, "x-retry-count": str(retry_count + 1)}
                await broker.publish(
                    data,
                    queue=questions_queue,
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
