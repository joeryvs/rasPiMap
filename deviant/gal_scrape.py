import argparse
import logging
import os
import random
import re
import time

import requests

DEFAULT_TIMEOUT = 3000
_logger = logging.getLogger(__name__)


def pause_execution(seconds, random_wait: bool = False):
    if random_wait:
        seconds = max(0, seconds + random.uniform(-0.5, 0.5))
    return time.sleep(seconds)


def _validate_user_name(user_name):
    user_regex = re.compile(r"^[a-z0-9\-]+$")

    if not user_regex.match(user_name):
        raise ValueError("name is not valid")

    return user_name


def run_curl_download(url: str, output_file: str):
    # download 1 file, and output it, simulating a single curl call
    _logger.debug("Download %s, saving to %s", url, output_file)
    with requests.get(url=url, timeout=DEFAULT_TIMEOUT) as res, open(output_file, "wb") as f:
        f.write(res.content)


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
        run_curl_download(url, target)
        if i != start_amount:
            pause_execution(wait_times)


def run_single_page(users: list[str] | str, wait_times: float):
    if isinstance(users, str):
        users = [users]
    for i, user in enumerate(users):
        # on iterations after the first, run a delay
        if i:
            pause_execution(wait_times)
        print(user)
        user_url = "https://www.deviantart.com/{}/gallery?page=1".format(user)
        user_output = "{}_gal_page_1.html".format(user)
        run_curl_download(url=user_url, output_file=user_output)


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

    args = parser.parse_args()
    args = vars(args)

    func = args.pop("func")

    func(**args)


if __name__ == "__main__":
    main()
