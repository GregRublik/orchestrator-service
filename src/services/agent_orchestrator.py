"""Мультиагентный оркестратор для анализа отзывов.

Каждый «агент» — это вызов GenerationService с определённым prompt_id и
mode="structured". Оркестратор последовательно прогоняет отзыв через:
  1. Sentiment Agent       — позитивный / негативный
  2. Problem Classification / Recommendation — в зависимости от тональности
  3. Response Agent        — генерация финального ответа
"""

import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.agent import (
    AgentState,
    ProblemClassification,
    RecommendationResult,
    ReviewInput,
    SentimentResult,
)
from schemas.generation import GenerateRequest, Mode
from services.generation import GenerationService
from repositories.problem_class import ProblemClassRepository
from repositories.recommendation_product import RecommendationProductRepository
from repositories.review_analysis import ReviewAnalysisRepository
from config import logger


class AgentOrchestrator:
    """Оркестратор мультиагентного анализа отзыва."""

    def __init__(
        self,
        generation_service: GenerationService,
        problem_class_repo: ProblemClassRepository,
        recommendation_product_repo: RecommendationProductRepository,
        review_analysis_repo: ReviewAnalysisRepository,
        prompt_ids: dict[str, int],
    ):
        self.generation = generation_service
        self.problem_class_repo = problem_class_repo
        self.recommendation_product_repo = recommendation_product_repo
        self.review_analysis_repo = review_analysis_repo
        self.prompt_ids = prompt_ids

    # ------------------------------------------------------------------
    # Публичный метод
    # ------------------------------------------------------------------

    async def analyze(
        self,
        review: ReviewInput,
        session: AsyncSession,
    ) -> AgentState:
        """Прогоняет отзыв через весь мультиагентный конвейер."""
        state = AgentState(review=review)

        try:
            # 1. Определение тональности
            state.sentiment = await self._run_sentiment_agent(state)
            logger.info(
                "Sentiment for review %s: positive=%s (%.2f)",
                review.id, state.sentiment.is_positive, state.sentiment.confidence,
            )

            # 2. Маршрутизация
            if state.sentiment.is_positive:
                state.recommendation = await self._run_recommendation_agent(state, session)
                logger.info(
                    "Recommendation for review %s: need=%s, products=%s",
                    review.id, state.recommendation.need_determined, state.recommendation.product_ids,
                )
            else:
                state.problem_classification = await self._run_problem_classification_agent(state, session)
                logger.info(
                    "Problem class for review %s: %s",
                    review.id, state.problem_classification.problem_class_name,
                )

            # 3. Генерация ответа
            state.generated_response = await self._run_response_agent(state, session)

            # 4. Сохраняем в БД
            await self._save_analysis(state, session)

        except Exception as exc:
            logger.error("Agent pipeline failed for review %s: %s", review.id, exc)
            state.error = str(exc)

        return state

    # ------------------------------------------------------------------
    # Агент 1: Sentiment
    # ------------------------------------------------------------------

    async def _run_sentiment_agent(self, state: AgentState) -> SentimentResult:
        review = state.review
        query = (
            f"Определи тональность отзыва. "
            f"Оценка покупателя: {review.productValuation}/5. "
            f"Даже если оценка 5 звёзд, но текст негативный — отзыв считается отрицательным.\n\n"
            f"Текст: {review.review_text}"
        )

        result = await self.generation.generate(
            GenerateRequest(
                query=query,
                prompt_id=self.prompt_ids["sentiment"],
                fields={
                    "product_name": review.product_name,
                    "valuation": str(review.productValuation),
                    "review_text": review.review_text,
                    "pros": review.pros,
                    "cons": review.cons,
                },
                mode=Mode.structured,
            )
        )

        return self._parse_structured(result, SentimentResult)

    # ------------------------------------------------------------------
    # Агент 2a: Problem Classification (для негативных)
    # ------------------------------------------------------------------

    async def _run_problem_classification_agent(
        self, state: AgentState, session: AsyncSession
    ) -> ProblemClassification:
        review = state.review

        # Достаём все доступные классы проблем из БД
        problem_classes = await self.problem_class_repo.get_all(session)
        classes_str = "\n".join(
            f"- id={pc.id}, name={pc.name}" for pc in problem_classes
        ) if problem_classes else "- id=1, name=качество товара\n- id=2, name=доставка\n- id=3, name=упаковка"

        query = (
            f"Классифицируй проблему, описанную в отзыве. "
            f"Выбери наиболее подходящий класс из списка ниже.\n\n"
            f"Доступные классы проблем:\n{classes_str}\n\n"
            f"Текст отзыва: {review.review_text}\n"
            f"Товар: {review.product_name}"
        )

        result = await self.generation.generate(
            GenerateRequest(
                query=query,
                prompt_id=self.prompt_ids["problem_classification"],
                fields={
                    "product_name": review.product_name,
                    "review_text": review.review_text,
                    "problem_classes": classes_str,
                },
                mode=Mode.structured,
            )
        )

        return self._parse_structured(result, ProblemClassification)

    # ------------------------------------------------------------------
    # Агент 2b: Recommendation (для позитивных)
    # ------------------------------------------------------------------

    async def _run_recommendation_agent(
        self, state: AgentState, session: AsyncSession
    ) -> RecommendationResult:
        review = state.review

        # Достаём активные товары для рекомендаций
        products = await self.recommendation_product_repo.get_all(
            session, filters={"is_active": True}
        )
        products_str = "\n".join(
            f"- id={p.id}, name={p.name}, category={p.category}, "
            f"target_need={p.target_need}, price={p.price}"
            for p in products
        ) if products else "Нет товаров для рекомендаций"

        query = (
            f"Покупатель оставил положительный отзыв на товар «{review.product_name}». "
            f"Определи возможную потребность покупателя и порекомендуй подходящие товары "
            f"из нашего каталога (укажи ID товаров).\n\n"
            f"Наш каталог:\n{products_str}\n\n"
            f"Текст отзыва: {review.review_text}"
        )

        result = await self.generation.generate(
            GenerateRequest(
                query=query,
                prompt_id=self.prompt_ids["recommendation"],
                fields={
                    "product_name": review.product_name,
                    "review_text": review.review_text,
                    "catalog": products_str,
                },
                mode=Mode.structured,
            )
        )

        return self._parse_structured(result, RecommendationResult)

    # ------------------------------------------------------------------
    # Агент 3: Response Generation
    # ------------------------------------------------------------------

    async def _run_response_agent(
        self, state: AgentState, session: AsyncSession
    ) -> str:
        review = state.review

        # Собираем контекст в зависимости от тональности
        if state.sentiment and state.sentiment.is_positive:
            situation = "ПОЛОЖИТЕЛЬНЫЙ ОТЗЫВ"
            extra_context = ""
            if state.recommendation:
                extra_context = (
                    f"Потребность покупателя: {state.recommendation.need_determined}\n"
                    f"Рекомендованные товары (ID): {state.recommendation.product_ids}"
                )
        else:
            situation = "НЕГАТИВНЫЙ ОТЗЫВ"
            extra_context = ""
            if state.problem_classification:
                extra_context = (
                    f"Класс проблемы: {state.problem_classification.problem_class_name}\n"
                    f"Обоснование: {state.problem_classification.reasoning}"
                )

        # Формируем comment_text как в prompt.txt
        comment_text = (
            f"Товар: {review.product_name}\n"
            f"Оценка: {review.productValuation}/5\n"
            f"Комментарий: {review.text or 'Нет текста'}\n"
            f"Плюсы: {review.pros or 'Нет текста'}\n"
            f"Минусы: {review.cons or 'Нет текста'}"
        )

        # Бренд из отзыва (динамический — у разных магазинов разный)
        brand_name = (
            review.productDetails.brandName
            if review.productDetails and review.productDetails.brandName
            else "SCENT"
        )

        result = await self.generation.generate(
            GenerateRequest(
                query=comment_text,
                prompt_id=self.prompt_ids["response"],
                fields={
                    "brand_name": brand_name,
                    "comment_text": comment_text,
                    "situation": situation,
                    "extra_context": extra_context,
                },
                mode=Mode.generate,
            )
        )

        # Для mode="generate" результат может быть строкой или словарём с data
        if isinstance(result, dict):
            return result.get("data", str(result))
        return str(result)

    # ------------------------------------------------------------------
    # Сохранение результатов в БД
    # ------------------------------------------------------------------

    async def _save_analysis(
        self, state: AgentState, session: AsyncSession
    ) -> None:
        data = {
            "review_id": state.review.id,
            "product_name": state.review.product_name,
            "product_valuation": state.review.productValuation,
            "review_text": state.review.review_text,
            "is_positive": state.sentiment.is_positive if state.sentiment else None,
            "sentiment_reasoning": state.sentiment.reasoning if state.sentiment else "",
            "problem_class_id": (
                state.problem_classification.problem_class_id
                if state.problem_classification
                else None
            ),
            "problem_reasoning": (
                state.problem_classification.reasoning
                if state.problem_classification
                else ""
            ),
            "recommended_product_ids": (
                state.recommendation.product_ids if state.recommendation else []
            ),
            "need_determined": (
                state.recommendation.need_determined if state.recommendation else ""
            ),
            "generated_response": state.generated_response or "",
        }

        try:
            await self.review_analysis_repo.add_one(session, data)
            await session.commit()
        except Exception as exc:
            logger.error("Failed to save analysis for review %s: %s", state.review.id, exc)
            await session.rollback()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_structured(result, model_cls):
        """Парсит structured-ответ от generation_service в Pydantic-модель."""
        # result может быть строкой JSON, словарём, или вложенным {"data": ...}
        if isinstance(result, dict):
            if "data" in result and isinstance(result["data"], dict):
                result = result["data"]
        elif isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                # Пробуем вытащить JSON из текста (иногда модель оборачивает в ```json)
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                    result = json.loads(result)
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                    result = json.loads(result)
                else:
                    raise

        return model_cls(**result)
