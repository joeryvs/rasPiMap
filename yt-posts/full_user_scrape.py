import argparse
import collections
import collections.abc
import datetime
import logging
import os
import pathlib
import urllib.parse
from uuid import uuid4

import extract
import requests
from main import YtPostScraper

_logger = logging.getLogger(__name__)
VERSION = "0.2"

extensions = {
    "text/html": ".html",
    "application/json": ".json",
    "image/webp": ".webp",
}


def full_scrape_user(user: str, wait_time: float, *, save_json: bool, save_urls: bool, save_temp_urls: bool):

    _logger.debug("Scraping user %s", user)
    input_file = f"{user}-full-urls.txt"
    json_directory = datetime.datetime.now(tz=datetime.timezone.utc).strftime("{}-%Y-%j").format(user)
    if os.path.isdir(json_directory):
        # Early return because the existence of the directory implies this user is already scraped
        _logger.warning("User %s has already been scraped today", user)
        return
    if save_json:
        os.makedirs(json_directory)
    else:
        json_directory = None

    all_urls = full_scrape_user_urls(user=user, wait_time=wait_time, json_directory=json_directory)

    if save_temp_urls:
        all_urls = print_iter_item(f"{user}-full-temp-urls.txt", all_urls)

    urls = (x for x in all_urls if x.startswith("https://yt3.ggpht.com"))
    if save_temp_urls:
        urls = print_iter_item(f"{user}-full-filtered-urls.txt", urls)
    urls = unique(map(extract.post_modify_runction, urls))
    if save_urls:
        urls = print_iter_item(input_file, urls)
    directory_prefix = f"{user}-full"
    download_from_web(urls, target_directory=directory_prefix, overwrite=True, update_extension=True)


def full_scrape_user_urls(user: str, wait_time: float, *, json_directory: str | None) -> collections.abc.Iterable[str]:

    graft_url = f"https://www.youtube.com/@{user.strip().removeprefix('@')}/posts"

    # use the functionality in main.py to downlaod the JSON
    scraper = YtPostScraper(json_directory, graft_url, wait_time=wait_time)
    _html_data, jsons = scraper.run()
    # Use the extract.py to retrieve and modify the urls
    for j in jsons:
        yield from extract.find_keys_rec(j, "url", False)


def download_from_web(
    urls: collections.abc.Iterable[str], /, target_directory: str, overwrite=True, update_extension=False
):
    if target_directory:
        os.makedirs(target_directory, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        # From the url perform an urlsplit to remove the query parameters, and finally split at / and take the last element
        p = urllib.parse.urlsplit(url=url).path.split("/")[-1]
        with requests.get(url=url) as res:
            new_file = pathlib.Path(os.path.join(target_directory, p))
            if update_extension and (new_extension := extensions.get(res.headers["content-type"])):
                new_file = new_file.with_suffix(new_extension)
            if not overwrite and os.path.exists(new_file):
                _logger.info("[%s] %s already exists skipping writing %s", i, new_file, url)
                new_file = find_unused_filename(str(new_file))
            _logger.info("[%s] %s -> %s", i, url, new_file)
            with open(new_file, "wb") as f:
                f.write(res.content)


def find_unused_filename(original_filename: str) -> str:

    if not os.path.exists(original_filename):
        return original_filename

    for i in range(2, 100):
        new_file_name = original_filename + "." + str(i)
        if os.path.exists(new_file_name):
            continue
        return new_file_name

    return original_filename + "." + uuid4().hex[:8]


def print_iter_item(file_name: str, /, items: collections.abc.Iterable[str]) -> collections.abc.Iterable[str]:

    with open(file_name, "a") as file:
        for item in items:
            print(item, file=file)
            yield item


def unique(items: collections.abc.Iterable[str]) -> collections.abc.Iterable[str]:
    seen = dict()
    for item in items:
        if item not in seen:
            yield seen
            seen.setdefault(item)


def rename_extensionless_files_in_directory(dir: str, target_extension: str):
    assert isinstance(target_extension, str) and target_extension.startswith(".")

    directory = pathlib.Path(dir)

    assert directory.is_dir()

    for d, _dirs, files in os.walk(dir):
        for file in files:
            full_file = os.path.join(d, file)

            full_file = pathlib.Path(full_file)
            if not full_file.suffix:
                new_name = full_file.with_suffix(target_extension)
                full_file.rename(new_name)


def main():
    logging.basicConfig(level="DEBUG")
    parser = argparse.ArgumentParser()

    parser.add_argument("users", nargs="+")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--wait-time", type=float, default=4.0)

    parser.add_argument("--save-json", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-urls", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-temp-urls", action=argparse.BooleanOptionalAction, default=False)

    args = parser.parse_args()
    users = args.users
    wait_time = args.wait_time
    save_json = args.save_json
    save_urls = args.save_urls
    save_temp_urls = args.save_temp_urls
    for user in users:
        full_scrape_user(
            user, wait_time=wait_time, save_json=save_json, save_urls=save_urls, save_temp_urls=save_temp_urls
        )


if __name__ == "__main__":
    main()
