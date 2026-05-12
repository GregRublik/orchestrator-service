from schemas.rag import RequestRunRag, Scenario, Question, ResponseRunRag
from schemas.retrieval import SearchRequest
from services.retrieval import RetrievalService
from services.generation import GenerationService

from config import settings


class RagService:
    """Service execution RAG pipeline"""

    def __init__(self, generation_service: GenerationService, retrieval_service: RetrievalService):
        self.generation_service = generation_service
        self.retrieval_service = retrieval_service

    async def execute(self, request: RequestRunRag) -> ResponseRunRag:
        if request.scenario == Scenario.mp_questions:
            return await self.execute_scenario_questions(request.question, settings.qdrant.collections.questions)

    async def execute_scenario_questions(self, payload: Question, questions_collection: str) -> ResponseRunRag:
        found_data = await self.retrieval_service.search(
            SearchRequest(
                query=payload.question,
                collection=questions_collection
            )
        )
        print(found_data)

        return ResponseRunRag(
        )