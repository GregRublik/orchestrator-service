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
