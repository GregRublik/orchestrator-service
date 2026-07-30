from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aiohttp import ClientSession

from config import settings
from db.database import get_db_session
from utils.session_manager import SessionManager

from services.rag import RagService
from services.retrieval import RetrievalService
from services.generation import GenerationService
from services.review import ReviewService
from services.agent_orchestrator import AgentOrchestrator

from repositories.problem_class import ProblemClassRepository
from repositories.recommendation_product import RecommendationProductRepository
from repositories.review_analysis import ReviewAnalysisRepository


# ---------------------------------------------------------------------------
# HTTP-сессия
# ---------------------------------------------------------------------------

def get_http_session(
    http_session: ClientSession = Depends(SessionManager.get_session),
) -> ClientSession:
    return http_session


# ---------------------------------------------------------------------------
# Внешние сервисы
# ---------------------------------------------------------------------------

def get_generation_service(
    http_session: ClientSession = Depends(get_http_session),
) -> GenerationService:
    return GenerationService(
        http_session, settings.generation.dsn
    )


def get_retrieval_service(
    http_session: ClientSession = Depends(get_http_session),
) -> RetrievalService:
    return RetrievalService(
        http_session, settings.retrieval.dsn
    )


# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------

def get_rag_service(
    generation_service: GenerationService = Depends(get_generation_service),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> RagService:
    return RagService(
        generation_service,
        retrieval_service,
    )


# ---------------------------------------------------------------------------
# Репозитории
# ---------------------------------------------------------------------------

def get_problem_class_repository() -> ProblemClassRepository:
    return ProblemClassRepository()


def get_recommendation_product_repository() -> RecommendationProductRepository:
    return RecommendationProductRepository()


def get_review_analysis_repository() -> ReviewAnalysisRepository:
    return ReviewAnalysisRepository()


# ---------------------------------------------------------------------------
# Оркестратор агентов
# ---------------------------------------------------------------------------

def get_agent_orchestrator(
    generation_service: GenerationService = Depends(get_generation_service),
    problem_class_repo: ProblemClassRepository = Depends(get_problem_class_repository),
    recommendation_product_repo: RecommendationProductRepository = Depends(
        get_recommendation_product_repository
    ),
    review_analysis_repo: ReviewAnalysisRepository = Depends(get_review_analysis_repository),
) -> AgentOrchestrator:
    return AgentOrchestrator(
        generation_service=generation_service,
        problem_class_repo=problem_class_repo,
        recommendation_product_repo=recommendation_product_repo,
        review_analysis_repo=review_analysis_repo,
        prompt_ids={
            "sentiment": settings.agent_prompts.sentiment,
            "problem_classification": settings.agent_prompts.problem_classification,
            "recommendation": settings.agent_prompts.recommendation,
            "response": settings.agent_prompts.response,
        },
    )


# ---------------------------------------------------------------------------
# Review Service
# ---------------------------------------------------------------------------

def get_review_service(
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
) -> ReviewService:
    return ReviewService(orchestrator=orchestrator)
