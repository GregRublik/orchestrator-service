from abc import ABC, abstractmethod

class BaseBrokers(ABC):

    @abstractmethod
    async def create_message(self, ):
        pass


class RabbiMQBroker(BaseBrokers):


