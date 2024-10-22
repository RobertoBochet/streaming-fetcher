import json
import re

from playwright.async_api import Error, Page, async_playwright

from ..exceptions import FetchEpisodeFailed, FetchEpisodeRateLimitExceeded
from ..utils import PlaywrightUtils
from .episode_fetch_task import EpisodeFetchTask
from .fetch_task import FetchTask


class AnimeUnityFetchTask(FetchTask):
    _fetch_episode_tasks_default_concurrency = 5
    _fetch_episode_default_concurrency = 3

    _base_url = "https://www.animeunity.to/anime"

    _regex_season = re.compile(r"([0-9]+)\s*(?:Part [0-9]+)?\s*(?:\(ITA\))?\s*$", flags=re.IGNORECASE)

    def __init__(self, show_id: str, /, **kwargs):
        super().__init__(**kwargs)
        self.show_id = show_id

    @classmethod
    async def get_season(cls, page: Page) -> int:
        title = await page.locator(".general .title").text_content()
        match = cls._regex_season.search(title)
        if match is not None:
            return int(match.group(1))
        return 1

    @classmethod
    def get_show_page_url(cls, show_id: str) -> str:
        return f"{cls._base_url}/{show_id}"

    @classmethod
    def get_watch_episode_url(cls, show_id: str, episode_id: int) -> str:
        return f"{cls.get_show_page_url(show_id)}/{episode_id}"

    async def fetch_episode_tasks(self):
        async with async_playwright() as playwright:
            browser = await playwright.firefox.launch()
            browser_context = await browser.new_context(java_script_enabled=False)

            page = await browser_context.new_page()
            await page.goto(self.get_show_page_url(self.show_id))

            player = page.locator("video-player")
            episodes = await player.get_attribute("episodes")

            season = await self.get_season(page)

            episodes_count = int(await player.get_attribute("episodes_count"))

            await page.close()
            await browser_context.close()

            episodes = json.loads(episodes)

            episodes = {(int(e.get("number")), int(e.get("id"))) for e in episodes}

            if len(episodes) < episodes_count:
                browser_context = await browser.new_context(java_script_enabled=True)

                page = await browser_context.new_page()
                await page.goto(self.get_show_page_url(self.show_id))

                episodes_nav_locator = page.locator("#episode-nav button")

                for i in range(1, await episodes_nav_locator.count()):
                    async with page.expect_response("**/info_api/**") as response:
                        await PlaywrightUtils.click(episodes_nav_locator.nth(i))
                    response = await response.value
                    response_payload = await response.json()
                    response_episodes = response_payload.get("episodes")

                    episodes |= {(int(e.get("number")), int(e.get("id"))) for e in response_episodes}

        episodes = sorted(episodes, key=lambda e: e[0])
        episodes = [(self.episode_filter(season, e), i) for e, i in episodes]
        episodes = [(*e, i) for e, i in episodes if e is not None]

        return [
            EpisodeFetchTask(
                fetch_task=self,
                season=s,
                episode=e,
                url=self.get_watch_episode_url(self.show_id, i),
            )
            for s, e, i in episodes
        ]

    async def fetch_episode(self, task: EpisodeFetchTask):
        async with async_playwright() as playwright:
            browser = await playwright.firefox.launch()
            browser_context = await browser.new_context(java_script_enabled=True)

            page = await browser_context.new_page()
            await page.goto(task.url)
            frame_url = await page.locator("#embed").get_attribute("src")
            await page.goto(frame_url)

            async with page.expect_download() as download_info:
                download_url = await page.evaluate("window.downloadUrl")
                async with page.expect_response(download_url) as response:
                    try:
                        await page.goto(download_url)
                    except Error:
                        pass  # workaround download bug playwright
                response_value = await response.value

                if response_value.status != 200:
                    await page.close()
                    await browser_context.close()

                    if response_value.status == 503:
                        raise FetchEpisodeRateLimitExceeded()
                    raise FetchEpisodeFailed()

            download = await download_info.value
            await download.save_as(task.path)

            await page.close()
            await browser_context.close()

    def __str__(self) -> str:
        return self.show_id
