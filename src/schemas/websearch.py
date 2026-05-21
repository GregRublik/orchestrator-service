from pydantic import BaseModel
from typing import List

class ExtractedDocument(BaseModel):
    url: str
    title: str
    content: str
    score: float
