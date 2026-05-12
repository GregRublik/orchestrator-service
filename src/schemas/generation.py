from pydantic import BaseModel
from enum import StrEnum

class Mode(StrEnum):
    chat = "chat"
    generate = "generate"
    structured = "structured"
    summarize = "summarize"

class GenerateRequest(BaseModel):
    query: str
    prompt_id: int
    fields: dict[str, str]

    mode: Mode = Mode.generate
    stream: bool = False
