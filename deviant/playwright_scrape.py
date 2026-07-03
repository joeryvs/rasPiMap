import argparse
import os
import pathlib
import urllib.parse
import uuid
from http.client import responses

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
    MAIN = url
    # MAIN = "https://playwright.dev/"
    temp = pathlib.Path("temp2")

    os.makedirs(temp, exist_ok=True)
    collected_links = []

    def cancel_all_but_main_reroute(route):
        print(route.request.url)
        collected_links.append(route.request.url)
        if route.request.url == MAIN:
            p = uuid.uuid4().hex
            p2 = temp / p
            response = route.fetch()

            with open(p2, "wb") as f:
                f.write(response.body())
            # print(dir(response))

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


def local_searching(url):
    path = "deviant/Art-Pages/ivatant_art/Once-a-General-Now-a-Plaything-1080996029"
    collected_links = []

    def cancel_all_but_main_reroute(route):
        print(route.request.url)
        collected_links.append(str(route.request.url))
        if route.request.url == url:
            with open(path) as f:
                route.fulfill(status=200, type="text/html", body=f.read())
            # route.fulfill(response=response)
            # route.fallback()
        else:
            route.fallback()

    with sync_playwright() as p:
        with p.webkit.launch() as browser:
            page = browser.new_page()
            help(page)
            exit()
            # page.route("**/*", cancel_all_but_main_reroute)
            page.goto("https://example.com")
            page.screenshot(path="example6.png")

            testdata = page.evaluate("""() => this.window['__INITIAL_I18N__']""")
            print(testdata)
            print(type(testdata))


def google_search(params):
    data = {"q": params, "udm": 2}
    URL = "https://www.google.com/search?" + urllib.parse.urlencode(data)
    with sync_playwright() as p:
        with p.webkit.launch() as browser:
            help(browser.new_page)
            page = browser.new_page(offline=True)

            page.goto(URL)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("params", type=str, nargs="+")
    parser.add_argument("--input", "-i")
    parser.add_argument("--output", "-o")

    args = parser.parse_args()
    url = "file:///home/joery/Bureaublad/raspiMap/deviant/front-page/index-2026-180.html"
    url = "http://localhost:8000/Will-You-Marry-Me-849050669"
    # scrape_playwright_website()
    # website_url(url)
    # google_search(args.params)
    local_searching("")
    print(args)


if __name__ == "__main__":
    main()
