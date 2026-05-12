from aiohttp import ClientSession
from schemas.generation import GenerateRequest

class GenerationService:

    def __init__(self, session: ClientSession, base_url: str, ):
        self.session = session
        self.base_url = base_url

    async def generate(self, payload: GenerateRequest):

        result = await self.session.post(
            self.base_url,

        )
        return await result.json()
