"""Репозиторий для QuestionAnswer."""

from models.question_answer import QuestionAnswer
from repositories.base import SQLAlchemyRepository


class QuestionAnswerRepository(SQLAlchemyRepository):
    model = QuestionAnswer
