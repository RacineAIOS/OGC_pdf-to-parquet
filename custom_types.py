# custom_types.py

from litellm import acompletion
from pydantic import BaseModel
import asyncio, instructor



class TechnicalQueries(BaseModel):
    main_query: str
    secondary_query: str
    visual_query: str
    multimodal_query: str
    language: str



class ParallelInstructor:
    """
    Returns the next available client instance from the pool in a thread-safe manner.

    Returns:
        An instructor client instance.
    """

    def __init__(self, num_instances: int) -> None:
        self.clients = [
          (
            instructor.from_litellm(
              acompletion
            )) for _ in range(num_instances)
        ]
        self.current_client = 0
        self._lock = asyncio.Lock()

    async def get_client(self) -> instructor.Instructor:
        async with self._lock:
            client = self.clients[self.current_client]
            self.current_client = (self.current_client + 1) % len(self.clients)
            return client