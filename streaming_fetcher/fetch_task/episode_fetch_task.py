from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fetch_task import FetchTask


class EpisodeFetchTask:
    def __init__(self, fetch_task: "FetchTask", url: str, season: int, episode: int | list[int]):
        self.fetch_task = fetch_task
        self.url = url
        self.season = season
        self.episode = episode

    @property
    def need_episode(self) -> bool:
        return self.fetch_task.need_episode(self.season, self.episode)

    @property
    def path(self) -> Path:
        return self.fetch_task.get_episode_absolute_path(self.season, self.episode)

    async def fetch(self) -> None:
        return await self.fetch_task.fetch_episode(self)
