import datetime
import logging
import os
from sre_parse import parse

from base import Factory, Scraper, State
from download_utils import download_from_web
from insta import InstagramFactory, InstaScraper, InstaState
from main import YtFactory, YtPostScraper
from utils import print_iter_item, unique

_logger = logging.getLogger(__name__)
VERSION = "0.1"


def full_scrape_user(
    user: str,
    factory: Factory,
    *,
    wait_time: float,
    save_json: bool,
    save_urls: bool,
    save_temp_urls: bool,
    eager: bool,
    from_json: bool = False,
):

    _logger.debug("Scraping user %s with %s", user, factory.__class__)

    input_file = f"{user}-full-urls.txt"
    json_directory = datetime.datetime.now(tz=datetime.timezone.utc).strftime("{}-%Y-%j").format(user)
    if os.path.isdir(json_directory):
        # Early return because the existence of the directory implies this user is already scraped
        _logger.warning("User %s has already been scraped today", user)
        if not from_json:
            return
    elif save_json:
        os.makedirs(json_directory)
    else:
        json_directory = None

    # use the functionality in main.py to downlaod the URLS
    if from_json and json_directory:
        all_urls = factory.load_urls_from_json_files(json_directory=json_directory, html_location="")
    else:
        scraper = factory.get_scraper(base_dir=json_directory, wait_time=wait_time)
        all_urls = scraper.run()
    if eager:
        all_urls = list(all_urls)
    if save_temp_urls:
        all_urls = print_iter_item(f"{user}-full-temp-urls.txt", all_urls)

    urls = (x for x in all_urls if factory.keep_url(x))
    if save_temp_urls:
        urls = print_iter_item(f"{user}-full-filtered-urls.txt", urls)
    urls = unique(map(factory.post_process_url, urls))
    if save_urls:
        urls = print_iter_item(input_file, urls)
    if eager:
        urls = list(urls)
    directory_prefix = f"{user}-full"
    download_from_web(urls, target_directory=directory_prefix, overwrite=True, update_extension=True)


FACTORIES = {
    "instagram": InstagramFactory,
    "youtube": YtFactory,
}


def main():
    import argparse

    logging.basicConfig(level="DEBUG")
    parser = argparse.ArgumentParser()

    parser.add_argument("users", nargs="+")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--factory", choices=["instagram", "youtube"], default="youtube")
    parser.add_argument("--wait-time", type=float, default=4.0)

    parser.add_argument("--save-json", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--from-json", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--save-urls", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--save-temp-urls", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument(
        "--eager",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="if set, download all json before downloading images",
    )

    args = parser.parse_args()
    factory = FACTORIES[args.factory]
    users = args.users
    wait_time = args.wait_time
    save_json = args.save_json
    save_urls = args.save_urls
    from_json = args.from_json
    save_temp_urls = args.save_temp_urls
    eager = args.eager
    for user in users:
        full_scrape_user(
            user,
            factory(user),
            wait_time=wait_time,
            save_json=save_json,
            save_urls=save_urls,
            save_temp_urls=save_temp_urls,
            from_json=from_json,
            eager=eager,
        )


if __name__ == "__main__":
    main()
