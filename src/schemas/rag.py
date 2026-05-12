from pydantic import BaseModel
from enum import StrEnum

class Scenario(StrEnum):
    mp_questions = "mp_questions"

class Question(BaseModel):
    question: str
    product_name: str
    product_id: int

class RequestRunRag(BaseModel):
    query: str | None = None
    question: Question | None = None
    scenario: Scenario

class ResponseRunRag(BaseModel):
    pass
