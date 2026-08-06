"""RAG generate endpoint (прямой, без очереди)."""
from fastapi import APIRouter, status, Depends

from schemas.rag import ResponseRunRag, RequestRunRagGenerate
from schemas.response import APIResponse, ok
from services.rag import RagService

from depends import get_rag_service
from exceptions import GeneratorServiceNotAvailable, RetrievalServiceNotAvailable, APIException

router = APIRouter(prefix="/rag")


@router.post("/generate", response_model=APIResponse[ResponseRunRag])
async def generate(
    request: RequestRunRagGenerate,
    rag_service: RagService = Depends(get_rag_service),
) -> ResponseRunRag:
    try:
        return ok(await rag_service.generation(request))
    except GeneratorServiceNotAvailable as e:
        raise APIException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error=e.detail
        )
    except RetrievalServiceNotAvailable as e:
        raise APIException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error=e.detail
        )