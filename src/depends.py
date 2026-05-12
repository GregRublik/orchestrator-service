from fastapi import Depends
from services import rag

def get_rag_service(

) -> rag.RagService:
    return rag.RagService(

    )