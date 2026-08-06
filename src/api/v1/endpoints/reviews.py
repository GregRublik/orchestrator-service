"""
Endpoints обработки отзывов МП
"""
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, status, Depends
from faststream.rabbit.fastapi import RabbitRouter

from schemas.response import APIResponse, ok
from schemas.review import CreateReviewRequest, ResponseReview

from config import settings
from exceptions import APIException
from queues import reviews_queue


from .broker_router import broker_router


@broker_router.post("/reviews", response_model=APIResponse[Any])
async def reviews(
    request: CreateReviewRequest,
    # review_service: ReviewService = Depends(get_review_service),
):
    message_id = str(uuid4())
    try:
        # Разворачиваем в полный ReviewInput — воркер ожидает его
        await broker_router.broker.publish(
            request.to_review_input().model_dump(),
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
