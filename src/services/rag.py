from schemas.rag import RequestRunRag, Scenario, Question, ResponseRunRag
from schemas.generation import GenerateRequest
from schemas.retrieval import SearchRequest, WebSearchRequest
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

        if payload.product_id is not None:
            filters = {
                "product_id": payload.product_id
            }
        else:
            filters = None

        questions = await self.retrieval_service.search(
            SearchRequest(
                query=payload.question,
                collection=questions_collection,
                filters=filters
            )
        )
        data_product = await self.retrieval_service.web_search(
            WebSearchRequest(
                query=payload.product_name, # ищем конкретно такой товар
                top_k=20
            )
        ) # TODO надо поделить на чанки, после этого переранжировать и передавать в контекст только наиболее релевантные

        rerank_data_product = await self.retrieval_service.rerank_web_search_data(
            payload.question,
            data_product["data"],
            top_k=5
        )
        web_info_product_str = ""
        for product in rerank_data_product["results"]:
            web_info_product_str += f"Найденная информация:\n 1 ТЕМА: {product['title']}, 2 Данные:{product['content']}, 3 Ссылка: {product['url']}"
        questions_str = ""
        for question in questions["results"]:
            questions_str += f"Вопрос: {question["content"]["question"]}, Ответ: {question["content"]["answer"]}, Товар: {question["content"]["product_name"]} id Товара: {question["content"]["product_id"]}\n"

        request = GenerateRequest(
                query=payload.question,
                prompt_id=5,
                fields={
                    "questions": questions_str,
                    "product_description": payload.product_description,
                    "web_info": web_info_product_str
                }
            )

        result = await self.generation_service.generate(
            request
        )

        return ResponseRunRag(
            result=str(result),
        )
