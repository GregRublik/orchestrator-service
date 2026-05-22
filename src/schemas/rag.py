from pydantic import BaseModel
from enum import StrEnum
from typing import Optional


class Question(BaseModel):
    question: str
    product_name: str
    product_description: str
    product_id: Optional[int] = None

class RequestRunRag(BaseModel):
    prompt_id: int

class RequestRunRagGenerate(RequestRunRag):
    query: str

class RequestRunRagQuestion(RequestRunRag):
    question: Optional[Question] = None

class ResponseRunRag(BaseModel):
    result: str
