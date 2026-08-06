from fastapi import FastAPI
import uvicorn
from config import settings
from api.v1.endpoints import (
    health,
    problem_classes,
    question_answers,
    rag,
    recommendation_products,
    review_analyses,
)
# Эти импорты регистрируют маршруты на broker_router через декораторы
import api.v1.endpoints.reviews  # noqa: F811
import api.v1.endpoints.questions  # noqa: F811
from api.v1.endpoints.broker_router import broker_router

from exceptions import APIException
from exception_handlers import api_exception_handler


app = FastAPI()
app.include_router(broker_router)
app.include_router(rag.router, tags=["rag"])
app.include_router(health.router, tags=["health"])
app.include_router(problem_classes.router, tags=["problem-classes"])
app.include_router(recommendation_products.router, tags=["recommendation-products"])
app.include_router(review_analyses.router, tags=["review-analyses"])
app.include_router(question_answers.router, tags=["question-answers"])

app.add_exception_handler(APIException, api_exception_handler)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
