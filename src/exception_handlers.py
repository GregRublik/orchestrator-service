from fastapi import Request, status
from fastapi.responses import JSONResponse
from exceptions import APIException

async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.error
        }
    )
