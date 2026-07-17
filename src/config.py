from pydantic_settings import BaseSettings, SettingsConfigDict


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

class RabbitMQSettings(BaseSettings):

    user: str
    password: str
    host: str
    port: int

    @property
    def dsn(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", env_file=".env", extra="ignore")


class Settings(BaseSettings):
    host: str
    port: int

    retrieval: RetrievalSettings
    generation: GenerationSettings
    qdrant: Qdrant
    rabbitmq: RabbitMQSettings

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")


settings = Settings(
    qdrant=Qdrant(
        collections=Collections()
    ),
    retrieval=RetrievalSettings(
    ),
    generation=GenerationSettings(
    ),
    rabbitmq=RabbitMQSettings(
    )
)