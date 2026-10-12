import argparse
import itertools
import logging
import os
import re
from collections.abc import Iterable
from datetime import datetime, timezone
from urllib import parse

import wget_utils
from bs4 import BeautifulSoup
from extractors import JsonImagePreUrlExtractor
from more_itertools import unique_everseen
from utils import FileWriter, Reader

_logger = logging.getLogger(__name__)


def _validate_user_name(user_name):
    user_regex = re.compile(r"^[a-z0-9\-]+$")
    if not user_regex.match(user_name):
        raise ValueError("name is not valid")
    return user_name


def run_multi_page(*, user: str, start_amount: int, end_amount: int | None, wait: float):
    """Download a range of pages from a user"""
    # Validation
    if end_amount is None:
        start_amount, end_amount = 1, start_amount
    if wait < 0.0:
        raise ValueError("Wait time should be positive")

    user_dir = os.path.join(os.path.dirname(__file__), "gallery-pages", user)
    os.makedirs(user_dir, exist_ok=True)
    for i in range(start_amount, end_amount + 1):
        url = f"https://www.deviantart.com/{user}/gallery?page={i}"
        target = os.path.join(user_dir, f"gallery_page_{i}.html")
        wget_utils.curl_download(url, target)
        if i != end_amount:
            wget_utils.pause_execution(wait)


def run_single_page(users: list[str] | str, wait: float):
    """Download the first page of the users"""
    if isinstance(users, str):
        users = [users]
    for i, user in enumerate(users, start=1):
        # on iterations after the first, run a delay
        if i > 1:
            wget_utils.pause_execution(wait)
        print(user)
        user_url = "https://www.deviantart.com/{}/gallery?page=1".format(user)
        user_output = "{}_gal_page_1.html".format(user)
        wget_utils.curl_download(url=user_url, output_file=user_output)


def run_single_user(user, wait: float):
    """Download the full gallery of a single user"""
    assert isinstance(user, str)
    assert isinstance(wait, float)

    if wait < 0.0:
        raise ValueError("Wait time should be positive")
    user = _validate_user_name(user)
    from urllib import parse

    user_dir = os.path.join(os.path.dirname(__file__), "gallery-pages", user)
    os.makedirs(user_dir, exist_ok=True)
    index = 1
    target_url = f"https://www.deviantart.com/{user}/gallery?page=1"
    while target_url:
        target = os.path.join(user_dir, f"gallery_page_{index}.html")
        wget_utils.curl_download(target_url, target)
        index += 1

        # read the file again
        with open(target, "r") as f:
            soup = BeautifulSoup(f.read(), features="html.parser")
        # find the next one, 1) using the string param doesnt work correctly, 2) replace == with ordinal compare
        next_anchors = [anchor for anchor in soup.find_all("a") if anchor.text == "Next"]

        if not next_anchors:
            break
        new_target = next_anchors[0]
        # the original HREF is an http link, replace with https
        href = new_target["href"]
        _, *parts = parse.urlparse(href)
        target_url = parse.urlunparse(["https", *parts])
        wget_utils.pause_execution(wait, True)


def run_daily(wait: float = 0.2):
    """Download all images currently on the front page, stops if the directory already exist"""
    today = datetime.now(tz=timezone.utc)
    today_map = format(today, "art-%Y-%j")

    today_index = os.path.join("front-page", format(today, "index-%Y-%j.html"))

    today_art_links = format(today, "art-%Y-%j.txt")
    print(today_map, today_index, today_art_links)

    if os.path.exists(today_map):
        _logger.error("Directory already exists, ending call")
        return 1

    os.makedirs(today_map, exist_ok=True)  # exist ok is used to avoid crashing
    # Download home page,
    wget_utils.curl_download("https://www.deviantart.com/", today_index)
    # extract urls
    image_urls = _json_pre_image_extractor(files=[today_index], write_target=today_art_links)
    # download the urls
    wget_utils.download_from_stream(urls=image_urls, directory_prefix=today_map, wait_time=wait)
    return 0


def run_tag(tags, wait: float, wait_between: float, max_downloads: int = 1, lazy: bool = True):

    today = format(datetime.now(tz=timezone.utc), "%Y-%j")
    for tag in tags:
        print(tag)

        url = f"https://www.deviantart.com/tag/{tag}"

        today_tag_map = f"tag/art-{tag}-{today}"
        today_tag_index = f"tag/front-page/index-{tag}-{today}.html"
        today_tag_art_links = f"tag/links/art-{tag}-{today}.txt"

        print(url, today_tag_map, today_tag_index, today_tag_art_links)

        if os.path.isfile(today_tag_index):
            _logger.warning("Tag %s is already downloaded", tag)
            continue

        os.makedirs(today_tag_map)
        files = _download_next_loop(
            initial_url=url,
            initial_location=today_tag_index,
            location_url=lambda i: f"tag/front-page/index-{tag}-{today}-{i}.html",
            max_downloads=max_downloads,
            wait=wait_between,
            lazy=lazy,
        )

        image_urls = _json_pre_image_extractor(files=files, write_target=today_tag_art_links)
        wget_utils.download_from_stream(urls=image_urls, directory_prefix=today_tag_map, wait_time=wait)
        # pause execution for debugging and avoid rate-limitters
        wget_utils.pause_execution(wait_between)

    return 0


def run_search(search_query: str, wait: float, wait_image: float, max_downloads: int = 1, lazy: bool = False):
    """Run a search query and store the resulting images"""
    assert str.isprintable(search_query)

    query = parse.urlencode({"q": search_query})
    url = parse.urlunsplit(["https", "www.deviantart.com", "/search", query, ""])
    today = format(datetime.now(tz=timezone.utc), "%Y-%j")  # datestamp
    # define variables for storing the HTML, image urls and images
    today_search_map = f"search/art-{search_query}-{today}"
    today_search_index = f"search/front-page/index-{search_query}-{today}.html"
    today_search_art_links = f"search/links/art-{search_query}-{today}.txt"

    print(url, today_search_map, today_search_index, today_search_art_links)

    if os.path.isfile(today_search_map):  # dont allow downloading same search query on same day
        _logger.warning("Search %s is already downloaded", search_query)
        return

    os.makedirs(today_search_map, exist_ok=True)
    files = _download_next_loop(
        initial_url=url,
        initial_location=today_search_index,
        location_url=lambda i: f"search/front-page/art-{search_query}-{today}-{i}.html",
        max_downloads=max_downloads,
        wait=wait,
        lazy=lazy,
    )
    image_urls = _json_pre_image_extractor(files=files, write_target=today_search_art_links)
    wget_utils.download_from_stream(urls=image_urls, directory_prefix=today_search_map, wait_time=wait_image)


def _download_next_loop(
    initial_url,
    initial_location,
    location_url,
    *,
    max_downloads: int | None = None,
    wait: float,
    lazy: bool = True,
) -> Iterable[str]:
    """Download the pages, and continuosly go to the Next pages"""

    def foo():

        current_url = initial_url
        current_location = initial_location
        iterator = range(1, max_downloads + 1) if isinstance(max_downloads, int) else itertools.count(start=1)
        for iteration in iterator:
            wget_utils.curl_download(url=current_url, output_file=current_location)
            yield current_location

            with open(current_location, "r") as f:
                soup = BeautifulSoup(f.read(), features="html.parser")

            # find the next one, 1) using the string param doesnt work correctly, 2) replace == with ordinal compare
            next_anchors = [
                anchor for anchor in soup.find_all("a") if anchor.text == "Next" and hasattr(anchor, "href")
            ]
            if not next_anchors:
                break
            else:
                current_url = next_anchors[0]["href"]
                # current_location = format(iteration, format_spec)
                current_location = location_url(iteration)
                wget_utils.pause_execution(seconds=wait)

    if lazy:
        return foo()
    else:
        return list(foo())


def _json_pre_image_extractor(files: Iterable[str], write_target):
    """lazyly extract the image urls from JSON of the site, and save the urls in a file"""

    def write_to_file(items):
        if write_target:
            with open(write_target, "w") as f:
                for item in items:
                    print(item, file=f)
                    yield item
        else:
            yield from items

    extractor = JsonImagePreUrlExtractor(reader=Reader(), writer=FileWriter(write_target))
    links = extractor.retrieve(input_path=files)
    links = unique_everseen(links)  # remove duplicates
    yield from write_to_file(links)


def main():
    logging.basicConfig(level="DEBUG")
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()
    single_page_parser = subparsers.add_parser("single", help="download the first page of user(s)")
    single_page_parser.add_argument("--wait", type=float, default=11, dest="wait")
    single_page_parser.add_argument("users", type=_validate_user_name, nargs="+")
    single_page_parser.set_defaults(func=run_single_page)

    single_user_parser = subparsers.add_parser("full", help="Fully scrape the gallery of a user")
    single_user_parser.add_argument("user", type=_validate_user_name)
    single_user_parser.add_argument("--wait", type=float, default=11, dest="wait")
    single_user_parser.set_defaults(func=run_single_user)

    multi_page_parser = subparsers.add_parser("multi", help="Scrape the range of gallery pages of a user")
    multi_page_parser.add_argument("user", type=_validate_user_name)
    multi_page_parser.add_argument("start_amount", type=int)
    multi_page_parser.add_argument("--wait", type=float, default=11, dest="wait")
    multi_page_parser.add_argument("end_amount", type=int, nargs="?")
    multi_page_parser.set_defaults(func=run_multi_page)

    daily_parser = subparsers.add_parser("daily", help="Scrape the front page")
    daily_parser.add_argument("--wait", type=float, default=0.4, dest="wait")
    daily_parser.set_defaults(func=run_daily)

    tag_parser = subparsers.add_parser("tag", help="Scrape a tag page")
    tag_parser.add_argument("tags", type=str, nargs="+")
    tag_parser.add_argument("--wait", type=float, default=0.5, dest="wait")
    tag_parser.add_argument("--wait-between", type=float, default=7, dest="wait_between")
    tag_parser.add_argument("--max-downloads", type=int, default=1, dest="max_downloads")
    tag_parser.add_argument("--lazy", action="store_true", dest="lazy")
    tag_parser.add_argument("--eager", action="store_false", dest="lazy")
    tag_parser.set_defaults(func=run_tag)

    search_parser = subparsers.add_parser("search", help="Perform a search scrape")
    search_parser.add_argument("search_query", type=str)
    search_parser.add_argument("--wait", type=float, default=7, dest="wait")
    search_parser.add_argument("--wait-image", type=float, default=0.5)
    search_parser.add_argument("--max-downloads", type=int, default=1)
    search_parser.add_argument("--lazy", action="store_true", dest="lazy")
    search_parser.add_argument("--eager", action="store_false", dest="lazy")
    search_parser.set_defaults(func=run_search)

    args = parser.parse_args()
    args = vars(args)

    func = args.pop("func")

    func(**args)


if __name__ == "__main__":
    main()
