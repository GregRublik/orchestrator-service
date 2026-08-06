"""CRUD для результатов обработки вопросов с динамической фильтрацией."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from depends import get_question_answer_repository
from repositories.question_answer import QuestionAnswerRepository
from schemas.agent import (
    QuestionAnswerResponse,
    QuestionAnswerUpdate,
)
from schemas.response import APIResponse, ok
from exceptions import APIException, ModelNotFoundException

router = APIRouter(prefix="/question-answers", tags=["question-answers"])


def _parse_query_filters(request: Request) -> dict:
    """Извлекает фильтры из query-параметров запроса.

    Django-style операторы: ?is_read__eq=0, ?product_name__ilike=крем,
    ?prompt_id__eq=3 и т.д.
    """
    excluded = {"mark_read"}
    filters = {}
    for key in request.query_params:
        if key in excluded:
            continue
        value = request.query_params[key]
        if value.lstrip("-").isdigit():
            filters[key] = int(value)
        else:
            filters[key] = value
    return filters


@router.get("/", response_model=APIResponse[list[QuestionAnswerResponse]])
async def list_question_answers(
    request: Request,
    mark_read: bool = Query(False, description="Пометить возвращённые результаты как прочитанные"),
    repo: QuestionAnswerRepository = Depends(get_question_answer_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Получить результаты обработки вопросов с фильтрацией.

    ```
    GET /question-answers/?is_read__eq=0             — только непрочитанные
    GET /question-answers/?product_name__ilike=крем   — поиск по названию
    GET /question-answers/?prompt_id__eq=3            — по prompt_id
    GET /question-answers/?is_read__eq=0&mark_read=true — взять и отметить
    ```
    """
    filters = _parse_query_filters(request)
    items = await repo.get_all(session, filters=filters if filters else None)

    if mark_read and items:
        for item in items:
            if not item.is_read:
                await repo.change_one(session, item.id, {"is_read": 1})
        await session.commit()
        items = await repo.get_all(session, filters=filters if filters else None)

    return ok([QuestionAnswerResponse.model_validate(item) for item in items])


@router.get("/{answer_id}/", response_model=APIResponse[QuestionAnswerResponse])
async def get_question_answer(
    answer_id: int,
    mark_read: bool = Query(True, description="Пометить как прочитанный при получении"),
    repo: QuestionAnswerRepository = Depends(get_question_answer_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Получить один результат по ID. По умолчанию помечает `is_read=1`."""
    try:
        item = await repo.get_by_id(session, answer_id)
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Question answer not found")

    if mark_read and not item.is_read:
        item = await repo.change_one(session, answer_id, {"is_read": 1})
        await session.commit()

    return ok(QuestionAnswerResponse.model_validate(item))


@router.put("/{answer_id}/", response_model=APIResponse[QuestionAnswerResponse])
async def update_question_answer(
    answer_id: int,
    body: QuestionAnswerUpdate,
    repo: QuestionAnswerRepository = Depends(get_question_answer_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Обновить результат (например, is_read вручную)."""
    try:
        item = await repo.change_one(
            session, answer_id, body.model_dump(exclude_unset=True)
        )
        await session.commit()
        return ok(QuestionAnswerResponse.model_validate(item))
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Question answer not found")


@router.delete("/{answer_id}/", response_model=APIResponse[Any])
async def delete_question_answer(
    answer_id: int,
    repo: QuestionAnswerRepository = Depends(get_question_answer_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Удалить результат."""
    try:
        await repo.delete_by_id(session, answer_id)
        await session.commit()
        return ok(None)
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Question answer not found")
