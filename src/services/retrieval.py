from services.generation import GenerationService
from schemas.retrieval import SearchRequest, SearchResponse, WebSearchRequest, WebSearchResponse
from aiohttp import ClientSession
from typing import List


class RetrievalService:

    def __init__(self, session: ClientSession, base_url: str, ):
        self.session = session
        self.base_url = base_url

    async def search(self, payload: SearchRequest) -> SearchResponse:
        print(payload.model_dump())
        response = await self.session.post(
            self.base_url + "/search/",
            json=payload.model_dump()
        )
        response = await response.json()

        return response.get("data")

    async def web_search(self, payload: WebSearchRequest) -> WebSearchResponse:
        print(payload.model_dump())
        response = await self.session.post(
            self.base_url + "/web/search/",
            json=payload.model_dump()
        )
        response = await response.json()

        return response.get("data")