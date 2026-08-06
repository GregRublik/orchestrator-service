"""
Endpoints обработки вопросов — через очередь RabbitMQ.
"""
from typing import Any
from uuid import uuid4

from fastapi import status
from faststream.rabbit.fastapi import RabbitRouter

from schemas.response import APIResponse, ok
from schemas.rag import RequestRunRagQuestion

from config import settings
from exceptions import APIException
from queues import questions_queue

from .broker_router import broker_router


@broker_router.post("/questions", response_model=APIResponse[Any])
async def questions(request: RequestRunRagQuestion):
    message_id = str(uuid4())
    try:
        await broker_router.broker.publish(
            request.model_dump(),
            message_id=message_id,
            queue=questions_queue,
            persist=True,
        )
        return ok({"message_id": message_id})
    except APIException as e:
        raise APIException(
            status_code=status.HTTP_207_MULTI_STATUS,
            error="Failed to publish question",
        )
