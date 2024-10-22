from playwright.async_api import Locator


class PlaywrightUtils:
    @staticmethod
    async def highlight_element(e: Locator):
        await e.evaluate("e => e.style.outline = '3px solid green'")

    @staticmethod
    async def click(e: Locator):
        await e.evaluate("e => e.click()")
