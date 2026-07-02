import argparse
import os
import pathlib
import uuid

from playwright.sync_api import sync_playwright


def scrape_playwright_website():
    MAIN = "https://playwright.dev/"

    cached = []

    def cancel_all_but_main_reroute(route):
        print(route.request.url)
        cached.append(route.request.url)
        if route.request.url == MAIN:
            route.fallback()
        else:
            route.abort()

    with sync_playwright() as p:
        with p.webkit.launch() as browser:
            page = browser.new_page()
            page.route("**/*", cancel_all_but_main_reroute)
            page.goto(MAIN)
            page.screenshot(path="example3.png")

    print(len(cached))
    print(*cached, sep="\n")
    return cached


def website_url(url):
    # MAIN = url
    MAIN = "https://playwright.dev/"
    temp = pathlib.Path("temp")

    os.makedirs(temp, exist_ok=True)
    collected_links = []

    def cancel_all_but_main_reroute(route):
        print(route.request.url)
        collected_links.append(route.request.url)
        if route.request.url == MAIN or 1:
            p = uuid.uuid4().hex
            p2 = temp / p
            response = route.fetch()

            with open(p2, "wb") as f:
                f.write(response.body())
            print(dir(response))

            route.fulfill(response=response)
            # route.fallback()
        else:
            route.abort()

    with sync_playwright() as p:
        with p.webkit.launch() as browser:
            page = browser.new_page()
            page.route("**/*", cancel_all_but_main_reroute)
            page.goto(MAIN)
            page.screenshot(path="example3.png")

    print(len(collected_links))
    print(*collected_links, sep="\n")
    return collected_links


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", "-i")
    parser.add_argument("--output", "-o")

    args = parser.parse_args()
    url = "file:///home/joery/Bureaublad/raspiMap/deviant/front-page/index-2026-180.html"
    # scrape_playwright_website()
    website_url(url)
    print(args)


if __name__ == "__main__":
    main()
