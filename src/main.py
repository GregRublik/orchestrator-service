from fastapi import FastAPI
import uvicorn
from config import settings
from api.v1.endpoints import (
    rag,
    health,
    reviews,
    problem_classes,
    recommendation_products,
    review_analyses,
)

from exceptions import APIException
from exception_handlers import api_exception_handler


app = FastAPI()
app.include_router(rag.router, tags=["rag"])
app.include_router(health.router, tags=["health"])
app.include_router(reviews.router, tags=["reviews"])
app.include_router(problem_classes.router, tags=["problem-classes"])
app.include_router(recommendation_products.router, tags=["recommendation-products"])
app.include_router(review_analyses.router, tags=["review-analyses"])

app.add_exception_handler(APIException, api_exception_handler)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
