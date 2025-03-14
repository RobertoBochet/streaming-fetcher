from asyncio import Semaphore
from dataclasses import dataclass


@dataclass
class FetchTaskConfiguration:
    fetch_episode_tasks_limiter: Semaphore = Semaphore(3)
    fetch_episode_limiter: Semaphore = Semaphore(3)
