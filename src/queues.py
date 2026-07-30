"""
Очереди RabbitMQ с параметрами долговременного хранения.

durable=True  — очередь переживает перезагрузку брокера
auto_delete=False — очередь не удаляется при отключении всех консьюмеров
"""

from faststream.rabbit import RabbitQueue

from config import settings

reviews_queue = RabbitQueue(
    name=settings.rabbitmq.queues.reviews,
    durable=True,
    auto_delete=False,
)

questions_queue = RabbitQueue(
    name=settings.rabbitmq.queues.questions,
    durable=True,
    auto_delete=False,
)
