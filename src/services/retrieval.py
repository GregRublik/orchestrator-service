from schemas.retrieval import SearchRequest, SearchResponse, WebSearchRequest, WebSearchResponse
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError

from exceptions import RetrievalServiceNotAvailable


class RetrievalService:

    def __init__(self, session: ClientSession, base_url: str, ):
        self.session = session
        self.base_url = base_url

    async def search(self, payload: SearchRequest) -> SearchResponse:
        try:
            response = await self.session.post(
                self.base_url + "/search/query/",
                json=payload.model_dump()
            )
            if response.status == 500: raise RetrievalServiceNotAvailable
            response = await response.json()
            return response.get("data")
        except RetrievalServiceNotAvailable as e:
            print(e.detail)
            raise e
        except ClientConnectorError as e:
            print(e)
            raise RetrievalServiceNotAvailable

    async def web_search(self, payload: WebSearchRequest) -> WebSearchResponse:
        try:
            response = await self.session.post(
                self.base_url + "/web/search/",
                json=payload.model_dump()
            )
            if response.status == 500: raise RetrievalServiceNotAvailable
            response = await response.json()
            return response.get("data")
        except RetrievalServiceNotAvailable as e:
            raise e
        except ClientConnectorError:
            raise RetrievalServiceNotAvailable

    async def rerank_web_search_data(self, query: str, documents: list[dict], top_k: int) -> WebSearchResponse:
        try:
            response = await self.session.post(
                self.base_url + "/search/semantic_in_texts/",
                json={
                    "query": query,
                    "documents": documents,
                    "top_k": top_k
                }
            )
            if response.status == 500: raise RetrievalServiceNotAvailable
            response = await response.json()
            return response.get("data")
        except RetrievalServiceNotAvailable as e:
            raise e
        except ClientConnectorError:
            raise RetrievalServiceNotAvailable
