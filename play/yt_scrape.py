import asyncio
import os
import pathlib
import random

from playwright.async_api import Playwright, async_playwright
from utils import persistent_data, save_response_handler


async def run(playwright: Playwright, type, downloaded, url):
    temp_path = pathlib.Path(__file__).parent / "youtube"
    os.makedirs(temp_path, exist_ok=True)

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    await context.route("**/*", save_response_handler(temp_path, type, downloaded))
    page = await context.new_page()
    await page.goto(url=url)
    # accept cookies
    cookie_button = page.get_by_role("button",name="Alles afwijzen")
    await cookie_button.click()
    for i in range(100):
        # wait until all images are loaded lazily
        await page.wait_for_timeout(timeout=random.uniform(1000, 3000))
        await page.keyboard.press("PageDown")
        # if there are right-arrows click it repeatedly
        # for i, p in range()

    await browser.close()


async def main():
    url = "https://www.youtube.com/@pokemon/posts"
    items = persistent_data(
        "items_youtube.json", {"todo": [url], "seen": [], "new_type": [], "downloaded": []}
    )
    async with async_playwright() as playwright:
        await run(playwright, items.data["new_type"], items.data["downloaded"], url)
    pass


if __name__ == "__main__":
    asyncio.run(main())
