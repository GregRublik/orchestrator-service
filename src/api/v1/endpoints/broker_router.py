"""Общий RabbitRouter для всех эндпоинтов, работающих через очередь.
Все эндпоинты используют ОДИН экземпляр роутера, чтобы избежать
дублирования AsyncAPI-эндпоинтов от FastStream."""

from faststream.rabbit.fastapi import RabbitRouter

from config import settings

from queues import questions_queue, reviews_queue


broker_router = RabbitRouter(settings.rabbitmq.dsn)


@broker_router.after_startup
async def declare_all_queues(app):
    """Декларирует все очереди при старте — очереди существуют всегда,
    даже если воркеры ещё не запущены."""
    await broker_router.broker.declare_queue(reviews_queue)
    await broker_router.broker.declare_queue(questions_queue)
