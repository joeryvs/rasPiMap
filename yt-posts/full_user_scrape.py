import argparse
import datetime
import logging
import os
import pathlib
import subprocess
import sys

import extract
from main import YtPostScraper

_logger = logging.getLogger(__name__)
VERSION = "0.1"


def full_scrape_user(user: str, wait_time: float):

    _logger.debug("Scraping user %s", user)
    # use the functionality in main.py to downlaod the JSON
    graft_url = f"https://www.youtube.com/@{user.strip().removeprefix('@')}/posts"

    input_file = f"{user}-full-urls.txt"
    json_directory = datetime.datetime.now(tz=datetime.timezone.utc).strftime("{}-%Y-%j").format(user)
    if os.path.isdir(json_directory):
        # Early return because the existence of the directory implies this user is already scraped
        _logger.warning("User %s has already been scraped today", user)
        return
    os.makedirs(json_directory)
    scraper = YtPostScraper(json_directory, graft_url, wait_time=wait_time)
    scraper.run()
    # Use the extract.py to retrieve and modify the urls
    urls = extract.get_by_pattern(json_directory, "https://yt3.ggpht.com")
    urls = list(map(extract.post_modify_runction, urls))

    # Use subprocess and wget to download the Images
    directory_prefix = f"{user}-full"
    download_from_web(list(urls), target_directory=directory_prefix, input_file=input_file)

    rename_extensionless_files_in_directory(directory_prefix, target_extension=".webp")


def download_from_web(urls: list[str], /, target_directory: str, input_file: str):
    # TODO replace with pure python
    with open(input_file, "w") as output:
        for url in urls:
            print(url, file=output)

    subprocess.run(
        ["wget", "--input-file", input_file, "--directory-prefix", target_directory, "--no-verbose"],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


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
    logging.basicConfig(level="INFO")
    parser = argparse.ArgumentParser()

    parser.add_argument("users", nargs="+")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--wait-time", type=float, default=4.0)

    args = parser.parse_args()
    users = args.users
    wait_time = args.wait_time
    for user in users:
        full_scrape_user(user, wait_time=wait_time)


if __name__ == "__main__":
    main()
