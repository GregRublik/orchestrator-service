"""
Endpoints обработки отзывов МП
"""
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, status, Depends
from faststream.rabbit.fastapi import RabbitRouter

from schemas.response import APIResponse, ok
from schemas.review import ResponseReview, CreateReview

from config import settings
from exceptions import APIException
from queues import reviews_queue


router = RabbitRouter(
    settings.rabbitmq.dsn
)


@router.after_startup
async def declare_reviews_queue(app):
    """Декларирует очередь при старте роутера — очередь существует всегда,
    даже если воркер ещё не запущен."""
    await router.broker.declare_queue(reviews_queue)


@router.post("/reviews", response_model=APIResponse[Any])
async def reviews(
    request: CreateReview,
    # review_service: ReviewService = Depends(get_review_service),
):
    message_id = str(uuid4())
    try:
        await router.broker.publish(
            request.model_dump(),
            message_id=message_id,
            queue=reviews_queue,
            persist=True,
        )
        return ok({"message_id": message_id})
    except APIException as e:
        raise APIException(
            status_code=status.HTTP_207_MULTI_STATUS,
            # error=e.detail
            error="dsf"
        )
