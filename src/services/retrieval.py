from services.generation import GenerationService
from schemas.retrieval import SearchRequest, SearchResponse
from aiohttp import ClientSession


class RetrievalService:

    def __init__(self, session: ClientSession, base_url: str, ):
        self.session = session
        self.base_url = base_url

    async def search(self, payload: SearchRequest) -> SearchResponse:
        response = await self.session.post(
            self.base_url + "/search",
            json=payload.model_dump()
        )
        return await response.json()
