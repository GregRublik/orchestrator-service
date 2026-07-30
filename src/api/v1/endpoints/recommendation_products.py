"""CRUD для товаров рекомендаций."""

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from depends import get_recommendation_product_repository
from repositories.recommendation_product import RecommendationProductRepository
from schemas.agent import (
    RecommendationProductCreate,
    RecommendationProductResponse,
    RecommendationProductUpdate,
)
from schemas.response import APIResponse, ok
from exceptions import APIException, ModelNotFoundException

router = APIRouter(prefix="/recommendation-products", tags=["recommendation-products"])


@router.get("/", response_model=APIResponse[list[RecommendationProductResponse]])
async def list_products(
    repo: RecommendationProductRepository = Depends(get_recommendation_product_repository),
    session: AsyncSession = Depends(get_db_session),
):
    items = await repo.get_all(session)
    return ok(
        [RecommendationProductResponse.model_validate(p) for p in items]
    )


@router.post("/", response_model=APIResponse[RecommendationProductResponse])
async def create_product(
    body: RecommendationProductCreate,
    repo: RecommendationProductRepository = Depends(get_recommendation_product_repository),
    session: AsyncSession = Depends(get_db_session),
):
    item = await repo.add_one(session, body.model_dump())
    await session.commit()
    return ok(RecommendationProductResponse.model_validate(item))


@router.get("/{product_id}/", response_model=APIResponse[RecommendationProductResponse])
async def get_product(
    product_id: int,
    repo: RecommendationProductRepository = Depends(get_recommendation_product_repository),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        item = await repo.get_by_id(session, product_id)
        return ok(RecommendationProductResponse.model_validate(item))
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Product not found")


@router.put("/{product_id}/", response_model=APIResponse[RecommendationProductResponse])
async def update_product(
    product_id: int,
    body: RecommendationProductUpdate,
    repo: RecommendationProductRepository = Depends(get_recommendation_product_repository),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        item = await repo.change_one(
            session, product_id, body.model_dump(exclude_unset=True)
        )
        await session.commit()
        return ok(RecommendationProductResponse.model_validate(item))
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Product not found")


@router.delete("/{product_id}/", response_model=APIResponse[Any])
async def delete_product(
    product_id: int,
    repo: RecommendationProductRepository = Depends(get_recommendation_product_repository),
    session: AsyncSession = Depends(get_db_session),
):
    try:
        await repo.delete_by_id(session, product_id)
        await session.commit()
        return ok(None)
    except ModelNotFoundException:
        raise APIException(status.HTTP_404_NOT_FOUND, "Product not found")
