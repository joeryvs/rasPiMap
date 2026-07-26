import asyncio
import os
import pathlib
import random

from playwright.async_api import Playwright, async_playwright
from utils import persistent_data, save_response_handler


async def run(playwright: Playwright, todo, seen, type, downloaded):
    temp_path = pathlib.Path(__file__).parent / "temp_storage4"
    os.makedirs(temp_path, exist_ok=True)

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    await context.route("**/*", save_response_handler(temp_path, type, downloaded))
    page = await context.new_page()
    while todo and len(seen) < 80:
        url = todo.pop()
        if url in seen:
            continue
        if not url or not url.startswith("https://"):
            continue
        await page.goto(url=url)
        seen.append(url)
        # wait to prevent errora
        await page.wait_for_timeout(timeout=random.uniform(5000, 6000))
        # reject cookies if available action-type="DENY"
        obj = await page.locator("button[action-type='DENY']").all()
        if obj:
            await obj[0].click()
        href = await page.evaluate("() => document.location.href")
        print(href)
        urls = await page.evaluate(
            "() => document.querySelectorAll('a').values().map(a => a['href']).filter(x => x).reduce((a,b) => a + '\\n' + b, '')"
        )
        # print(urls)
        todo.extend(urls.split("\n"))
        print(len(todo), len(seen))
    await browser.close()


async def main():
    items = persistent_data(
        "items.json", {"todo": ["https://www.example.com"], "seen": [], "new_type": [], "downloaded": []}
    )
    async with async_playwright() as playwright:
        await run(playwright, items.data["todo"], items.data["seen"], items.data["new_type"], items.data["downloaded"])
    pass


if __name__ == "__main__":
    asyncio.run(main())
