from pydantic import BaseModel
from enum import StrEnum
from typing import Optional


class RequestRunRag(BaseModel):
    prompt_id: int


class RequestRunRagGenerate(RequestRunRag):
    query: str
    fields: Optional[dict[str, str]] = {}


class ResponseRunRag(BaseModel):
    result: str
