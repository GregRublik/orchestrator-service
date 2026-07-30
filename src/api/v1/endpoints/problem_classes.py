"""CRUD для классов проблем."""

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from depends import get_problem_class_repository
from repositories.problem_class import ProblemClassRepository
from schemas.agent import (
    ProblemClassCreate,
    ProblemClassResponse,
    ProblemClassUpdate,
)
from schemas.response import APIResponse, ok
from exceptions import APIException, ModelNotFoundException

router = APIRouter(prefix="/problem-classes", tags=["problem-classes"])


@router.get("/", response_model=APIResponse[list[ProblemClassResponse]])
async def list_problem_classes(
    repo: ProblemClassRepository = Depends(get_problem_class_repository),
    session: AsyncSession = Depends(get_db_session),
):
    items = await repo.get_all(session)
    return ok(
        [ProblemClassResponse.model_validate(pc) for pc in items]
    )


@router.post("/", response_model=APIResponse[ProblemClassResponse])
async def create_problem_class(
    body: ProblemClassCreate,
    repo: ProblemClassRepository = Depends(get_problem_class_repository),
    session: AsyncSession = Depends(get_db_session),
):
    item = await repo.add_one(session, body.model_dump())
    await session.commit()
    return ok(ProblemClassResponse.model_validate(item))


@router.get("/{problem_class_id}/", response_model=APIResponse[ProblemClassResponse])
async def get_problem_class(
    problem_class_id: int,
    repo: ProblemClassRepository = Depends(get_problem_class_repository),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        item = await repo.get_by_id(session, problem_class_id)
        return ok(ProblemClassResponse.model_validate(item))
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Problem class not found")


@router.put("/{problem_class_id}/", response_model=APIResponse[ProblemClassResponse])
async def update_problem_class(
    problem_class_id: int,
    body: ProblemClassUpdate,
    repo: ProblemClassRepository = Depends(get_problem_class_repository),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        item = await repo.change_one(
            session, problem_class_id, body.model_dump(exclude_unset=True)
        )
        await session.commit()
        return ok(ProblemClassResponse.model_validate(item))
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Problem class not found")


@router.delete("/{problem_class_id}/", response_model=APIResponse[Any])
async def delete_problem_class(
    problem_class_id: int,
    repo: ProblemClassRepository = Depends(get_problem_class_repository),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        await repo.delete_by_id(session, problem_class_id)
        await session.commit()
        return ok(None)
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Problem class not found")
