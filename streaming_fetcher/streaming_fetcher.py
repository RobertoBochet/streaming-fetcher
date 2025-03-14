from asyncio import gather
from functools import cached_property
from logging import getLogger
from pathlib import Path

from .exceptions import FetchEpisodeFailed, FetchEpisodeRateLimitExceeded
from .fetch_task import EpisodeFetchTask, FetchTask


class StreamingFetcher:
    @cached_property
    def _logger(self):
        return getLogger(__package__)

    def __init__(
        self,
        dry_run: bool = False,
        base_path: Path = None,
    ):
        self.dry_run = dry_run
        self.base_path = base_path

        self.tasks: list[FetchTask] = []

    def add_task(self, *tasks: FetchTask):
        if self.base_path is not None:
            for task in tasks:
                task.base_path = self.base_path
        self.tasks.extend(tasks)

    async def fetch_episodes_list(self, task: FetchTask):
        async with task.configuration.fetch_episode_tasks_limiter:
            self._logger.info(f"fetch episodes list {task}")

            tasks = await task.fetch_episode_tasks()

            self._logger.info(f"done fetch episodes list {task}: found {len(tasks)} episodes")

            return tasks

    async def fetch_episode(self, task: EpisodeFetchTask):
        if not task.need_episode:
            self._logger.info(f">>Skip {task.path.name}")
            return

        async with task.fetch_task.configuration.fetch_episode_limiter:
            self._logger.info(f"fetch {task.path.name}")

            if self.dry_run:
                return

            try:
                await task.fetch()
            except FetchEpisodeRateLimitExceeded:
                self._logger.error(f"failed fetch {task.path.name}: Rate limit exceeded")
                self._logger.warning(
                    "The remote service rate limits the episode fetching: "
                    "You should try to reduce the concurrency limit"
                )

                return

            except FetchEpisodeFailed:
                self._logger.error(f"failed fetch {task.path.name}: Generic error")
                return

            self._logger.info(f"done fetch {task.path.name}")

    async def run(self):
        self._logger.info("start tasks")

        tasks = [self.fetch_episodes_list(t) for t in self.tasks]

        fetch_episodes_lists_result = await gather(*tasks)

        self._logger.info(f"done fetch all episodes list: found {sum(map(len, fetch_episodes_lists_result))} episodes")

        for episodes_tasks in fetch_episodes_lists_result:
            tasks = [self.fetch_episode(t) for t in episodes_tasks]

            await gather(*tasks)

        self._logger.info("Done")
