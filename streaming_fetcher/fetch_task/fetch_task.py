from abc import ABC
from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import Callable

from .episode_fetch_task import EpisodeFetchTask
from .fetch_task_configuration import FetchTaskConfiguration


class FetchTask(ABC):
    configuration = FetchTaskConfiguration()

    @cached_property
    def _logger(self):
        return getLogger(__package__)

    base_path: Path | None = None

    def __init__(
        self,
        episode_path: Callable[[int, int | list[int]], Path] | None = None,
        episode_filter: Callable[[int, int | list[int]], tuple[int, int | list[int]] | None] | None = None,
        need_episode: Callable[[int, int | list[int]], bool] | None = None,
    ):
        self._episode_path = episode_path
        self._episode_filter = episode_filter
        self._need_episode = need_episode

    def get_episode_path(self, season: int, episode: int | list[int]) -> Path:
        return self._episode_path(season, episode)

    def get_episode_absolute_path(self, season: int, episode: int | list[int]) -> Path:
        relative_path = self.get_episode_path(season, episode)
        if relative_path.is_absolute():
            return relative_path
        else:
            return self.base_path / relative_path

    def episode_filter(self, season: int, episode: int | list[int]) -> tuple[int, int | list[int]] | None:
        if self._episode_filter is not None:
            return self._episode_filter(season, episode)
        return season, episode

    def need_episode(self, season: int, episode: int | list[int]) -> bool:
        if self._need_episode is not None:
            return self._need_episode(season, episode)
        return not self.get_episode_absolute_path(season, episode).exists()

    def __str__(self) -> str:
        pass

    async def fetch_episode_tasks(self) -> list[EpisodeFetchTask]:
        pass

    async def fetch_episode(self, task: EpisodeFetchTask) -> None:
        pass
