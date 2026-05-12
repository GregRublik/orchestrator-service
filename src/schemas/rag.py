from pydantic import BaseModel
from enum import StrEnum

class Scenario(StrEnum):
    mp_questions = "mp_questions"

class QueryData(BaseModel):
    prompt: str
    query: str
    fields: dict[str, str]

class RequestRunRag(BaseModel):
    data: QueryData
    scenario: Scenario

class ResponseRunRag(BaseModel):
    pass
