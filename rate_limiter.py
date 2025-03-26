# rate_limiter.py

from collections import deque
import asyncio, time



class RateLimiter:
    def __init__(self, requests_per_second: int) -> None:
        self._lock = asyncio.Lock()
        self.successful_requests = deque(maxlen=30 * requests_per_second)
        self.last_display_time = time.time()
        self.capacity = requests_per_second
        self.tokens = self.capacity
        self.last_refill = time.time()


    async def record_success(self) -> None:
        """
        Records a successful API request and updates statistics.
        """
        async with self._lock:
            current_time = time.time()
            self.successful_requests.append(current_time)
            if current_time - self.last_display_time >= 1:
                self.display_current_rps()
                self.last_display_time = current_time


    def display_current_rps(self) -> None:
        """
        Calculates and displays the actual requests per second over the last 30s.
        """
        current_time = time.time()
        while self.successful_requests and current_time - self.successful_requests[0] > 30:
            self.successful_requests.popleft()
        actual_rps = len(self.successful_requests) / 30 if self.successful_requests else 0
        print(f"\rActual RPS (last 30s): {actual_rps:.2f}", end="", flush=True)


    async def acquire(self) -> None:
        """
        Acquires permission to make a new request, waiting if necessary.
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.last_refill = now
            
            self.tokens += elapsed * self.capacity
            self.tokens = min(self.tokens, self.capacity)
            
            if self.tokens < 1:
                deficit = 1 - self.tokens
                await asyncio.sleep(deficit / self.capacity)
                await self.acquire()
            else:
                self.tokens -= 1


    async def __aenter__(self):
        await self.acquire()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass