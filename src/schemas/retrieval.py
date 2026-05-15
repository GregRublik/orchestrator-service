from pydantic import BaseModel
from typing import Optional, List


class BaseSearchRequest(BaseModel):
    top_k: int = 5
    filters: Optional[dict] = None
    collection: str

class SearchRequest(BaseSearchRequest):
    query: str

class SearchResult(BaseModel):
    id: int
    score: float
    content: dict
    metadata: dict

class WebSearchResult(BaseModel):
    url: str
    title: str
    score: float
    content: dict

class SearchResponse(BaseModel):
    results: List[SearchResult]

class WebSearchRequest(BaseModel):
    query: str
    top_k: int = 5

class WebSearchResponse(BaseModel):
    results: List[WebSearchResult]
