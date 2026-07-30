import sys
import asyncio
import signal

sys.path.append("src/")

from faststream.rabbit.broker import RabbitBroker
from faststream.rabbit import RabbitMessage
from config import settings, logger
from schemas.review import CreateReview
from queues import reviews_queue

from services.review import ReviewService
from depends import get_review_service


broker = RabbitBroker(settings.rabbitmq.dsn)



@broker.subscriber(reviews_queue)
async def reviews(
    data: CreateReview,
    message: RabbitMessage,
    review_service: ReviewService = get_review_service()
):
    try:
        print(message.headers.get("x-retry-count"))
        await review_service.execute(data)
        await message.ack()

    except ZeroDivisionError as e:
        logger.error(e)
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
