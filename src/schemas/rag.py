from pydantic import BaseModel
from enum import StrEnum
from typing import Optional

class Scenario(StrEnum):
    mp_questions = "mp_questions"
    generation = "generation"

class Question(BaseModel):
    question: str
    product_name: str
    product_description: str
    product_id: Optional[int] = None

class RequestRunRag(BaseModel):
    query: Optional[str] = None
    prompt_id: Optional[int] = 7
    question: Optional[Question] = None
    scenario: Scenario

class ResponseRunRag(BaseModel):
    result: str
