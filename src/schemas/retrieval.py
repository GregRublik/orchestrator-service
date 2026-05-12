from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    collection: str

class SearchResult(BaseModel):
    id: int
    score: float
    content: dict
    metadata: dict

class SearchResponse(BaseModel):
    results: list[SearchResult]
