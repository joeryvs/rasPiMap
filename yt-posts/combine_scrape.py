import datetime
import logging
import os

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
):

    _logger.debug("Scraping user %s", user)
    json_directory = datetime.datetime.now(tz=datetime.timezone.utc).strftime("{}-%Y-%j").format(user)
    if os.path.isdir(json_directory):
        # Early return because the existence of the directory implies this user is already scraped
        _logger.warning("User %s has already been scraped today", user)
        return
    if save_json:
        os.makedirs(json_directory)
    else:
        json_directory = None

    scraper = fa
    base_url = f"https://www.instagram.com/{user}/"
    html_save = f"{user}-front_page.html"
    scraper = InstaScraper(
        base_url=base_url, wait_time=wait_time, base_dir=json_directory, html_save_location=html_save
    )
    all_urls = scraper.run()
    if eager:
        all_urls = list(all_urls)
    if save_temp_urls:
        all_urls = print_iter_item(f"{user}-insta-full-temp-urls.txt", all_urls)

    urls = all_urls
    # urls = (x for x in all_urls if x.startswith("https://yt3.ggpht.com"))
    if save_temp_urls:
        urls = print_iter_item(f"{user}-insta-full-filtered-urls.txt", urls)
    input_file = f"{user}-insta-full-urls.txt"
    if save_urls:
        urls = print_iter_item(input_file, urls)
    if eager:
        urls = list(urls)
    directory_prefix = f"{user}-full"
    download_from_web(urls, target_directory=directory_prefix, overwrite=True, update_extension=True)


def main():

    from argparse import ArgumentParser, BooleanOptionalAction

    logging.basicConfig(level="DEBUG")

    parser = ArgumentParser()

    parser.add_argument("users", nargs="+")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--wait-time", type=float, default=4.0)
    parser.add_argument("--save-html", action=BooleanOptionalAction, default=True)
    parser.add_argument("--save-json", action=BooleanOptionalAction, default=True)
    parser.add_argument("--save-urls", action=BooleanOptionalAction, default=True)
    parser.add_argument("--eager", action="store_true", dest="eager", default=True)
    parser.add_argument("--lazy", action="store_false", dest="eager")
    args = parser.parse_args()

    users = args.users
    wait_time = args.wait_time
    save_html = args.save_html
    save_json = args.save_json
    save_urls = args.save_urls
    eager = args.eager
    for user in users:
        full_scrape_user(
            user,
            wait_time=wait_time,
            save_json=save_json,
            save_temp_urls=save_urls,
            save_urls=save_urls,
            eager=eager,
        )


if __name__ == "__main__":
    main()
