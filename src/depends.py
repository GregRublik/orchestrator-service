from fastapi import Depends
from services import rag
from services.retrieval import RetrievalService
from services.generation import GenerationService

from aiohttp import ClientSession

from config import SessionManager, settings


def get_http_session(
        http_session: ClientSession = Depends(SessionManager.get_session),
) -> ClientSession:
    return http_session

def get_generation_service() -> GenerationService:
    return GenerationService()

def get_retrieval_service(
        http_session: ClientSession = Depends(get_http_session),
) -> RetrievalService:
    return RetrievalService(
        http_session, settings.retrieval.dsn
    )

def get_rag_service(
    generation_service: GenerationService = Depends(get_generation_service),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> rag.RagService:
    return rag.RagService(
        generation_service,
        retrieval_service,
    )