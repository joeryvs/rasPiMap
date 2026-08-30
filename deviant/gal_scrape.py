import argparse
import logging
import os
import random
import re
import time
from datetime import datetime, timezone, tzinfo

import requests
import wget_utils

DEFAULT_TIMEOUT = 3000
_logger = logging.getLogger(__name__)


def _validate_user_name(user_name):
    user_regex = re.compile(r"^[a-z0-9\-]+$")

    if not user_regex.match(user_name):
        raise ValueError("name is not valid")

    return user_name


def run_multi_page(user: str, start_amount: int, end_amount: int | None, wait_times: float):
    # Validation
    if end_amount is None:
        start_amount, end_amount = 1, start_amount

    if wait_times < 0.0:
        raise ValueError("Wait time should be positive")

    user_dir = os.path.join(os.path.dirname(__file__), "gallery-pages", user)
    os.makedirs(user_dir, exist_ok=True)
    for i in range(start_amount, end_amount + 1):
        url = f"https://www.deviantart.com/{user}/gallery?page={i}"
        target = os.path.join(user_dir, f"gallery_page_{i}.html")
        wget_utils.curl_download(url, target)
        if i != start_amount:
            wget_utils.pause_execution(wait_times)


def run_single_page(users: list[str] | str, wait_times: float):
    if isinstance(users, str):
        users = [users]
    for i, user in enumerate(users):
        # on iterations after the first, run a delay
        if i:
            wget_utils.pause_execution(wait_times)
        print(user)
        user_url = "https://www.deviantart.com/{}/gallery?page=1".format(user)
        user_output = "{}_gal_page_1.html".format(user)
        wget_utils.curl_download(url=user_url, output_file=user_output)


def run_daily(wait_times: float = 0.2):

    today = datetime.now(tz=timezone.utc)
    today_map = format(today, "art-%Y-%j")

    today_index = os.path.join("front-page", format(today, "index-%Y-%j.html"))

    today_art_links = format(today, "art-%Y-%j.txt")
    print(today_map, today_index, today_art_links)

    if os.path.exists(today_map):
        _logger.error("Directory already exists, ending call")
        return 1

    os.makedirs(today_map, exist_ok=True)
    wget_utils.curl_download("https://www.deviantart.com/", today_index)
    # call python script
    import utils
    from extractors import JsonImagePreUrlExtractor

    extractor = JsonImagePreUrlExtractor(reader=utils.Reader(), writer=utils.FileWriter(today_art_links))

    extractor.extract(today_index, sort=True, unique=True)
    wget_utils.download_from_file(today_art_links, today_map, wait_time=wait_times)
    return 0


def run_tag(tags, wait_times):

    today = format(datetime.now(tz=timezone.utc), "%Y-%j")
    for tag in tags:
        print(tag)

        url = f"https://www.deviantart.com/tag/{tag}"

        today_tag_map = f"tag/art-{tag}-{today}"
        today_tag_index = f"tag/front-page/index-{tag}-{today}.html"
        today_tag_art_links = f"tag/links/art-{tag}-{today}.txt"

        print(url, today_tag_map, today_tag_index, today_tag_art_links)

        if os.path.exists(today_tag_index):
            _logger.warning("Tag $(tag)s is already downloaded", tag=tag)
            continue

        os.makedirs(today_tag_map)
        wget_utils.curl_download(url=url, output_file=today_tag_index)

        from extractors import MainImageExtractor
        from utils import FileWriter, Reader

        extractor = MainImageExtractor(reader=Reader(), writer=FileWriter(today_tag_art_links))
        extractor.extract(today_tag_index, sort=True, unique=True)
        wget_utils.download_from_file(today_tag_art_links, today_tag_map, wait_time=wait_times)

        time.sleep(3)

    return 0


def main():

    parser = argparse.ArgumentParser()

    time_parser = argparse.ArgumentParser(add_help=False)
    time_parser.add_argument("--wait-times", type=float, default=11)

    subparsers = parser.add_subparsers()
    single_page_parser = subparsers.add_parser("single", parents=[time_parser])

    single_page_parser.add_argument("users", type=_validate_user_name, nargs="+")
    single_page_parser.set_defaults(func=run_single_page)

    multi_page_parser = subparsers.add_parser("multi", parents=[time_parser])
    multi_page_parser.add_argument("user", type=_validate_user_name)
    multi_page_parser.add_argument("start_amount", type=int)
    multi_page_parser.add_argument("end_amount", type=int, nargs="?")
    multi_page_parser.set_defaults(func=run_multi_page)

    daily_parser = subparsers.add_parser("daily", parents=[time_parser])
    daily_parser.set_defaults(func=run_daily, wait_time=0.4)

    tag_parser = subparsers.add_parser("tag", parents=[time_parser])
    tag_parser.add_argument("tags", type=str, nargs="+")
    tag_parser.set_defaults(func=run_tag, wait_time=0.5)

    args = parser.parse_args()
    args = vars(args)

    func = args.pop("func")

    func(**args)


if __name__ == "__main__":
    main()
