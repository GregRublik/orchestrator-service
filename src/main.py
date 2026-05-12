from fastapi import FastAPI
import uvicorn
from config import settings
from api.v1.endpoints import rag


app = FastAPI()
app.include_router(rag.router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
