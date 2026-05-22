from fastapi import APIRouter
from fastapi import Depends

from schemas.rag import ResponseRunRag, RequestRunRagQuestion, RequestRunRagGenerate
from schemas.response import APIResponse, ok
from services.rag import RagService

from depends import get_rag_service

router = APIRouter(prefix="/rag")

@router.post("/generate", response_model=APIResponse[ResponseRunRag])
async def generate(
    request: RequestRunRagGenerate,
    rag_service: RagService = Depends(get_rag_service),
) -> ResponseRunRag:

    return ok(await rag_service.generation(request))

@router.post("/questions", response_model=APIResponse[ResponseRunRag])
async def questions(
    request: RequestRunRagQuestion,
    rag_service: RagService = Depends(get_rag_service),
) -> ResponseRunRag:
    return ok(await rag_service.questions(request))
