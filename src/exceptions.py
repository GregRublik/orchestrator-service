class APIException(Exception):
    def __init__(self, status_code: int, error: str):
        self.status_code = status_code
        self.error = error

class GeneratorServiceNotAvailable(BaseException):
    """LLM модель недоступна"""
    detail = "Generator is not available"

class RetrievalServiceNotAvailable(BaseException):
    """Сервис поиска недоступен"""
    detail = "Retrieval is not available"

class ModelAlreadyExistsException(BaseException):
    """Объект уже существует"""

    detail = "model already exists"

class ModelNotFoundException(Exception):
    """Объект не найден"""

    detail = "model not found"

class ModelMultipleResultsFoundException(BaseException):
    """При ожидании одного объекта нашлось несколько экземпляров"""

    detail = "multiple results found"
