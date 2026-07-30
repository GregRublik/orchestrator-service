"""CRUD для результатов анализа отзывов с динамической фильтрацией."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from depends import get_review_analysis_repository
from repositories.review_analysis import ReviewAnalysisRepository
from schemas.agent import (
    ReviewAnalysisResponse,
    ReviewAnalysisUpdate,
)
from schemas.response import APIResponse, ok
from exceptions import APIException, ModelNotFoundException

router = APIRouter(prefix="/review-analyses", tags=["review-analyses"])


def _parse_query_filters(request: Request) -> dict:
    """Извлекает фильтры из query-параметров запроса.

    Django-style операторы: ?is_read__eq=false, ?product_name__ilike=крем,
    ?review_id__eq=abc123, ?problem_class_id__gte=3 и т.д.

    Преобразует строковые 'true'/'false' в bool, числа в int.
    """
    excluded = {"mark_read"}
    filters = {}
    for key in request.query_params:
        if key in excluded:
            continue
        value = request.query_params[key]
        if value.lower() == "true":
            filters[key] = True
        elif value.lower() == "false":
            filters[key] = False
        elif value.lstrip("-").isdigit():
            filters[key] = int(value)
        else:
            filters[key] = value
    return filters


@router.get("/", response_model=APIResponse[list[ReviewAnalysisResponse]])
async def list_review_analyses(
    request: Request,
    mark_read: bool = Query(False, description="Пометить возвращённые результаты как прочитанные"),
    repo: ReviewAnalysisRepository = Depends(get_review_analysis_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Получить результаты анализа с фильтрацией.

    Фильтры — любые поля через query-параметры с Django-style операторами:

    ```
    GET /review-analyses/?is_read__eq=false          — только непрочитанные
    GET /review-analyses/?is_positive__eq=true        — только позитивные
    GET /review-analyses/?product_name__ilike=крем    — поиск по названию
    GET /review-analyses/?review_id__eq=abc123        — конкретный отзыв
    GET /review-analyses/?problem_class_id__eq=8      — конкретный класс проблемы
    GET /review-analyses/?is_read__eq=false&mark_read=true  — взять непрочитанные и сразу отметить
    ```

    Поддерживаемые операторы: `__eq`, `__ne`, `__gt`, `__gte`, `__lt`,
    `__lte`, `__in`, `__like`, `__ilike`, `__isnull`.
    """
    filters = _parse_query_filters(request)

    items = await repo.get_all(session, filters=filters if filters else None)

    # Помечаем как прочитанные, если запрошено
    if mark_read and items:
        for item in items:
            if not item.is_read:
                await repo.change_one(session, item.id, {"is_read": True})
        await session.commit()
        # Перезагружаем, чтобы вернуть актуальное состояние
        items = await repo.get_all(session, filters=filters if filters else None)

    return ok([ReviewAnalysisResponse.model_validate(item) for item in items])


@router.get("/{analysis_id}/", response_model=APIResponse[ReviewAnalysisResponse])
async def get_review_analysis(
    analysis_id: int,
    mark_read: bool = Query(True, description="Пометить как прочитанный при получении"),
    repo: ReviewAnalysisRepository = Depends(get_review_analysis_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Получить один результат по ID. По умолчанию помечает `is_read=true`."""
    try:
        item = await repo.get_by_id(session, analysis_id)
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Review analysis not found")

    if mark_read and not item.is_read:
        item = await repo.change_one(session, analysis_id, {"is_read": True})
        await session.commit()

    return ok(ReviewAnalysisResponse.model_validate(item))


@router.put("/{analysis_id}/", response_model=APIResponse[ReviewAnalysisResponse])
async def update_review_analysis(
    analysis_id: int,
    body: ReviewAnalysisUpdate,
    repo: ReviewAnalysisRepository = Depends(get_review_analysis_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Обновить результат (например, is_read вручную)."""
    try:
        item = await repo.change_one(
            session, analysis_id, body.model_dump(exclude_unset=True)
        )
        await session.commit()
        return ok(ReviewAnalysisResponse.model_validate(item))
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Review analysis not found")


@router.delete("/{analysis_id}/", response_model=APIResponse[Any])
async def delete_review_analysis(
    analysis_id: int,
    repo: ReviewAnalysisRepository = Depends(get_review_analysis_repository),
    session: AsyncSession = Depends(get_db_session),
):
    """Удалить результат."""
    try:
        await repo.delete_by_id(session, analysis_id)
        await session.commit()
        return ok(None)
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Review analysis not found")
