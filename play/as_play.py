import asyncio
import os
import pathlib
import uuid

from playwright.async_api import Playwright, Route, async_playwright
from utils import persistent_data


async def run(playwright: Playwright, todo, seen):
    temp_path = pathlib.Path(__file__).parent / "temp_storage"
    os.makedirs(temp_path, exist_ok=True)

    async def handle(route: Route):
        response = await route.fetch()
        body = await response.body()
        with open(temp_path / uuid.uuid4().hex[:12], "wb") as f:
            f.write(body)
        await route.fulfill(response=response)

    browser = await playwright.chromium.launch()
    page = await browser.new_page()
    await page.route("**/*", handle)

    while todo:
        url = todo.pop()
        if url in seen:
            continue
        await page.goto(url=url)
        seen.append(url)

        href = await page.evaluate("() => document.location.href")
        print(href)
        urls = await page.evaluate(
            "() => document.querySelectorAll('a').values().map(a => a['href']).filter(x => x).reduce((a,b) => a + '\\n' + b, '')"
        )
        print(urls)
        todo.extend(urls.split("\n"))


async def main():
    # todo = persistent_data("todo.json", ["https://www.example.com"])
    # seen = persistent_data("seen.json", [])
    items = persistent_data("items.json", {"todo": ["https://example.com"], "seen": []})
    async with async_playwright() as playwright:
        await run(playwright, items.data["todo"], items.data["seen"])
    pass


if __name__ == "__main__":
    asyncio.run(main())
