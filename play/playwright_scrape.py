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
            page = browser.new_page(headless=False)
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
    path = url
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


def keep_content_type(content_type):
    return True


CONTENT_TYPES = {
    "text/html": ".html",
    "text/javascript": ".js",
    "text/css": ".css",
    "image/png": ".png",
    "image/jpg": ".jpg",
    "image/jpeg": ".jpeg",
    "image/svg": ".svg",
    "image/webp": ".webp",
    "font/woff2": ".woff2",
}


def get_content_type_extension(content_type):
    content_type = content_type.split("; ")[0]
    if content_type in CONTENT_TYPES:
        return CONTENT_TYPES[content_type]
    print(content_type)
    return ""


def google_search(params):
    data = {"q": " ".join(params), "udm": 2}
    URL = "https://www.google.com/search?" + urllib.parse.urlencode(data)
    # URL = "https://www.example.com/"
    # URL = "https://playwright.dev/python/"
    # URL = "https://playwright.dev/"
    current_scrape_dir = pathlib.Path(uuid.uuid4().hex[:12])
    os.mkdir(current_scrape_dir)
    print(current_scrape_dir.name)
    urls = []

    def reroute_url(route):
        # print(route.request.url)
        urls.append(route.request.url)
        response = route.fetch()
        headers = response.headers
        # print(headers)
        if keep_content_type(headers.get("content-type")):
            extension: str = get_content_type_extension(headers["content-type"])
            new_path = current_scrape_dir / uuid.uuid4().hex[:12]
            new_path = new_path.with_suffix(extension)
            # new_path.suffix = extension
            with open(new_path, "wb+") as f:
                f.write(response.body())
        route.fulfill(response=response)

    with sync_playwright() as p:
        with p.webkit.launch() as browser:
            # help(browser.new_page)
            page = browser.new_page()
            page.route("**/*", reroute_url)
            page.goto(URL)
            print(page.url)
            page.screenshot(path="example3.png")

            # page.wait(1000)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("params", type=str, nargs="+")
    parser.add_argument("--input", "-i")
    parser.add_argument("--output", "-o")

    args = parser.parse_args()
    # url = "file:///home/joery/Bureaublad/raspiMap/deviant/front-page/index-2026-180.html"
    # url = "http://localhost:8000/Will-You-Marry-Me-849050669"
    # scrape_playwright_website()
    # website_url(url)
    google_search(args.params)
    # local_searching("")
    print(args)


if __name__ == "__main__":
    main()
