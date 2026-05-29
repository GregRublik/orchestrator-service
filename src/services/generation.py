from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError, ClientConnectorError
from schemas.generation import GenerateRequest

from exceptions import GeneratorServiceNotAvailable

class GenerationService:

    def __init__(self, session: ClientSession, base_url: str, ):
        self.session = session
        self.base_url = base_url

    async def generate(self, payload: GenerateRequest):
        try:
            result = await self.session.post(
                f"{self.base_url}/responses/generate/",
                json=payload.model_dump()
            )
            # if result.status == 500: raise GeneratorServiceNotAvailable()
            result = await result.json()
            return result.get("data")
        # except GeneratorServiceNotAvailable as e:
        #     raise e
        # except ClientConnectorError:
        #     raise GeneratorServiceNotAvailable
        finally:
            pass
