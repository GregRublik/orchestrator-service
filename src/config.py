from pydantic_settings import BaseSettings, SettingsConfigDict
from aiohttp import ClientSession

from services.generation import GenerationService


class SessionManager:
    _session: ClientSession | None = None

    @classmethod
    async def get_session(cls) -> ClientSession:
        """Возвращает сессию aiohttp, создавая её при первом вызове."""
        if cls._session is None or cls._session.closed:
            cls._session = ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        """Закрывает сессию, если она существует."""
        if cls._session is not None:
            await cls._session.close()
            cls._session = None

class GenerationSettings(BaseSettings):
    host: str
    port: int

    @property
    def dsn(self):
        return f"http://{self.host}:{self.port}"

    model_config = SettingsConfigDict(env_prefix="GENERATION_", env_file=".env", extra="ignore")

class RetrievalSettings(BaseSettings):
    host: str
    port: int

    @property
    def dsn(self):
        return f"http://{self.host}:{self.port}"

    model_config = SettingsConfigDict(env_prefix="RETRIEVAL_", env_file=".env", extra="ignore")


class Collections(BaseSettings):
    questions: str

    model_config = SettingsConfigDict(env_prefix="COLLECTION_", env_file=".env", extra="ignore")


class Qdrant(BaseSettings):
    collections: Collections

class Settings(BaseSettings):
    host: str
    port: int

    retrieval: RetrievalSettings
    generation: GenerationSettings
    qdrant: Qdrant

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")


settings = Settings(
    qdrant=Qdrant(
        collections=Collections()
    ),
    retrieval=RetrievalSettings(
    ),
    generation=GenerationSettings(
    )
)