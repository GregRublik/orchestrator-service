from fastapi import APIRouter
from fastapi import Depends

from schemas.rag import RequestRunRag, ResponseRunRag
from schemas.response import APIResponse, ok
from services.rag import RagService

from depends import get_rag_service

router = APIRouter(prefix="/rag")

@router.post("/run", response_model=APIResponse[ResponseRunRag])
async def rag(
    request: RequestRunRag,
    rag_service: RagService = Depends(get_rag_service),
) -> ResponseRunRag:

    return ok(await rag_service.execute(request))
