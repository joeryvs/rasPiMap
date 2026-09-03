import datetime
import logging
import os

from download_utils import download_from_web
from main import YtPostScraper
from utils import print_iter_item, unique

_logger = logging.getLogger(__name__)
VERSION = "0.2"


def full_scrape_user(
    user: str, wait_time: float, *, save_json: bool, save_urls: bool, save_temp_urls: bool, eager: bool
):

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

    graft_url = f"https://www.youtube.com/@{user.strip().removeprefix('@')}/posts"

    # use the functionality in main.py to downlaod the URLS
    scraper = YtPostScraper(base_dir=json_directory, graft_url=graft_url, wait_time=wait_time)
    all_urls = scraper.run()
    if eager:
        all_urls = list(all_urls)
    if save_temp_urls:
        all_urls = print_iter_item(f"{user}-full-temp-urls.txt", all_urls)

    urls = (x for x in all_urls if x.startswith("https://yt3.ggpht.com"))
    if save_temp_urls:
        urls = print_iter_item(f"{user}-full-filtered-urls.txt", urls)
    urls = unique(map(yt_crop_to_full_url, urls))
    if save_urls:
        urls = print_iter_item(input_file, urls)
    if eager:
        urls = list(urls)
    directory_prefix = f"{user}-full"
    download_from_web(urls, target_directory=directory_prefix, overwrite=True, update_extension=True)


def yt_crop_to_full_url(url: str) -> str:
    # vim macro is 0nllc9e4000 + Esc + j0
    # now as a python function
    # YOLO
    parts = url.split("=s", 1)
    assert len(parts) == 2
    begin, end = parts
    x = end.split("-")
    # set the first element to 4000, this ensure a large image is downloaded
    x[0] = "4000"
    # remove part 1 and 2, this makes sure the image is not cropped
    x[1:3] = []
    return f"{begin}=s{'-'.join(x)}"


def main():
    import argparse

    logging.basicConfig(level="DEBUG")
    parser = argparse.ArgumentParser()

    parser.add_argument("users", nargs="+")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--wait-time", type=float, default=4.0)

    parser.add_argument("--save-json", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-urls", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-temp-urls", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument(
        "--eager",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="if set, download all json before downloading images",
    )

    args = parser.parse_args()
    users = args.users
    wait_time = args.wait_time
    save_json = args.save_json
    save_urls = args.save_urls
    save_temp_urls = args.save_temp_urls
    eager = args.eager
    for user in users:
        full_scrape_user(
            user,
            wait_time=wait_time,
            save_json=save_json,
            save_urls=save_urls,
            save_temp_urls=save_temp_urls,
            eager=eager,
        )


if __name__ == "__main__":
    main()
