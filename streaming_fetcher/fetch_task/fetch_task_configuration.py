from asyncio import Semaphore
from dataclasses import dataclass


@dataclass
class FetchTaskConfiguration:
    fetch_episode_tasks_limiter: Semaphore = Semaphore(3)
    fetch_episode_limiter: Semaphore = Semaphore(3)

    @fetch_episode_tasks_limiter.setter
    def set_fetch_episode_tasks_limiter(self, limiter: Semaphore | int) -> None:
        self.fetch_episode_tasks_limiter = limiter if isinstance(limiter, Semaphore) else Semaphore(limiter)

    @fetch_episode_limiter.setter
    def set_fetch_episode_limiter(self, limiter: Semaphore | int) -> None:
        self.fetch_episode_limiter = limiter if isinstance(limiter, Semaphore) else Semaphore(limiter)
