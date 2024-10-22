import asyncio
import re
from collections.abc import Callable

from playwright.async_api import Page, Route, async_playwright
from yt_dlp import YoutubeDL

from streaming_fetcher.utils import PlaywrightUtils

from .episode_fetch_task import EpisodeFetchTask
from .fetch_task import FetchTask


class StreamingCommunityFetchTask(FetchTask):
    _fetch_episode_tasks_default_concurrency = 5
    _fetch_episode_default_concurrency = 5

    _base_url = "https://streamingcommunity.computer"

    _regex_season = re.compile("^(?:Stagione|Parte) ([0-9]+)")

    def __init__(
        self,
        show_id: str,
        /,
        episode_number: Callable[[dict, int], int | list[int]] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.show_id = show_id
        self.episode_number = episode_number

    def get_episode_number(self, episode_data: dict, season: int) -> int | list[int]:
        if self.episode_number is not None:
            e = self.episode_number(episode_data, season)
            if e is not None:
                return e
        return episode_data.get("number")

    @classmethod
    def get_season_number_from_name(cls, name: str) -> int:
        return int(cls._regex_season.match(name).group(1))

    @classmethod
    async def get_available_seasons(cls, page: Page) -> list[int]:
        await PlaywrightUtils.click(page.locator(".episodes-tab .season-trigger"))
        seasons_list = page.locator(".episodes-tab .season-list .season-item")
        seasons_list_text = [await s.text_content() for s in await seasons_list.all()]
        return [cls.get_season_number_from_name(t) for t in seasons_list_text]

    @classmethod
    async def select_season(cls, page: Page, season: int) -> None:
        await PlaywrightUtils.click(
            page.locator(".episodes-tab .season-list .season-item").get_by_text(f"Stagione {season}").first
        )

    @classmethod
    def get_show_page_url(cls, show_id: str) -> str:
        return f"{cls._base_url}/titles/{show_id}"

    @classmethod
    def get_watch_episode_url(cls, show_id: int, episode_id: int) -> str:
        return f"{cls._base_url}/watch/{show_id}?e={episode_id}"

    async def fetch_episode_tasks(self):
        async with async_playwright() as playwright:
            browser = await playwright.firefox.launch()
            browser_context = await browser.new_context(java_script_enabled=True)

            page = await browser_context.new_page()
            await page.goto(self.get_show_page_url(self.show_id))

            await PlaywrightUtils.click(page.locator(".info-wrap .episodes"))

            async def fake(route: Route):
                headers = route.request.headers
                headers["X-Inertia-Partial-Data"] = "loadedSeason,flash"
                await route.continue_(headers=headers)

            await page.route("**/stagione-*", fake)

            tasks = []

            for s in await self.get_available_seasons(page):
                self._logger.info(f"fetch episodes list {self.show_id} season {s}")
                async with page.expect_response("**/stagione-*") as response:
                    await self.select_season(page, s)
                response = await response.value
                response_payload = await response.json()
                response_season = response_payload.get("props").get("loadedSeason")
                response_episodes = response_season.get("episodes")

                show_id = response_season.get("title_id")

                tasks += [
                    EpisodeFetchTask(
                        fetch_task=self,
                        url=self.get_watch_episode_url(show_id, e.get("id")),
                        season=s,
                        episode=self.get_episode_number(season=s, episode_data=e),
                    )
                    for e in response_episodes
                    if self.episode_filter(s, self.get_episode_number(season=s, episode_data=e))
                ]

        return tasks

    async def fetch_episode(self, task: EpisodeFetchTask):
        with YoutubeDL(
            {
                "paths": {"home": str(task.path.parent)},
                "outtmpl": str(task.path.name),
                "quiet": True,
                "noprogress": True,
            }
        ) as ydl:
            await asyncio.to_thread(ydl.download, [task.url])

    def __str__(self) -> str:
        return self.show_id
