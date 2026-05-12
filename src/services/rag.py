from schemas.rag import RequestRunRag, Scenario, QueryData, ResponseRunRag
from schemas.retrieval import SearchRequest
from services.retrieval import RetrievalService
from services.generation import GenerationService


class RagService:
    """Service execution RAG pipeline"""

    def __init__(self, generation_service: GenerationService, retrieval_service: RetrievalService):
        self.generation_service = generation_service
        self.retrieval_service = retrieval_service

    async def execute(self, request: RequestRunRag) -> ResponseRunRag:
        if request.scenario == Scenario.mp_questions:
            return await self.execute_scenario_questions(request.data, )

    async def execute_scenario_questions(self, payload: QueryData, questions_collection: str) -> ResponseRunRag:
        found_data = await self.retrieval_service.search(
            SearchRequest(
                query=payload.query,
                collection=questions_collection
            )
        )



        return ResponseRunRag(

        )