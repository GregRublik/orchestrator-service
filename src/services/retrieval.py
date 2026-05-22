from schemas.websearch import ExtractedDocument
from services.generation import GenerationService
from schemas.retrieval import SearchRequest, SearchResponse, WebSearchRequest, WebSearchResponse
from aiohttp import ClientSession
from typing import List


class RetrievalService:

    def __init__(self, session: ClientSession, base_url: str, ):
        self.session = session
        self.base_url = base_url

    async def search(self, payload: SearchRequest) -> SearchResponse:
        response = await self.session.post(
            self.base_url + "/search/query/",
            json=payload.model_dump()
        )
        response = await response.json()

        return response.get("data")

    async def web_search(self, payload: WebSearchRequest) -> WebSearchResponse:
        response = await self.session.post(
            self.base_url + "/web/search/",
            json=payload.model_dump()
        )
        response = await response.json()

        return response.get("data")

    async def rerank_web_search_data(self, query: str, documents: list[dict], top_k: int) -> WebSearchResponse:
        response = await self.session.post(
            self.base_url + "/search/semantic_in_texts/",
            json={
                "query": query,
                "documents": documents,
                "top_k": top_k
            }
        )
        response = await response.json()

        return response.get("data")