"""
Endpoints обработки отзывов МП
"""
from typing import Any

from fastapi import APIRouter, status, Depends
from faststream.rabbit.fastapi import RabbitRouter

from schemas.response import APIResponse, ok
from schemas.review import ResponseReview, CreateReview

from config import settings


from exceptions import APIException


router = RabbitRouter(
    settings.rabbitmq.dsn
)


@router.post("/reviews", response_model=APIResponse[Any])
async def reviews(
    request: CreateReview,
    # review_service: ReviewService = Depends(get_review_service),
):
    try:

        res = await router.broker.publish(
            request.model_dump(),
            "new_reviews",
        )

        print(res)
        return ok("es")
    except APIException as e:
        raise APIException(
            status_code=status.HTTP_207_MULTI_STATUS,
            # error=e.detail
            error="dsf"
        )
