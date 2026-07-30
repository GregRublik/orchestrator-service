"""Репозиторий для ProblemClass."""

from repositories.base import SQLAlchemyRepository
from models.problem_class import ProblemClass


class ProblemClassRepository(SQLAlchemyRepository):
    model = ProblemClass
