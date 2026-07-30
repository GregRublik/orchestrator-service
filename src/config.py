from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",)
logger = logging.getLogger(__name__)


class DBSettings(BaseSettings):
    host: str
    user: str
    password: str
    name: str
    port: int

    @property
    def dsn_asyncpg(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")


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

class RabbitMQQueueSettings(BaseSettings):
    reviews: str = "reviews_new_message"
    questions: str = "questions_new_message"

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_QUEUE_", env_file=".env", extra="ignore")

class RabbitMQSettings(BaseSettings):

    queues: RabbitMQQueueSettings
    user: str
    password: str
    host: str
    port: int

    @property
    def dsn(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", env_file=".env", extra="ignore")


class AgentPromptIds(BaseSettings):
    """prompt_id в generation_service для каждого агента."""
    sentiment: int = 5
    problem_classification: int = 6
    recommendation: int = 7
    response: int = 8

    model_config = SettingsConfigDict(env_prefix="AGENT_PROMPT_", env_file=".env", extra="ignore")


class Settings(BaseSettings):
    host: str
    port: int

    db: DBSettings
    agent_prompts: AgentPromptIds
    retrieval: RetrievalSettings
    generation: GenerationSettings
    qdrant: Qdrant
    rabbitmq: RabbitMQSettings

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")


settings = Settings(
    db=DBSettings(),
    agent_prompts=AgentPromptIds(),
    qdrant=Qdrant(
        collections=Collections()
    ),
    retrieval=RetrievalSettings(
    ),
    generation=GenerationSettings(
    ),
    rabbitmq=RabbitMQSettings(
        queues=RabbitMQQueueSettings()
    )
)
