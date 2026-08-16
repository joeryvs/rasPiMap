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


def full_scrape_user(user: str):

    _logger.debug("Scraping user %s", user)
    # use the functionality in main.py to downlaod the JSON
    graft_url = f"https://www.youtube.com/@{user.strip().removeprefix('@')}/posts"

    input_file = f"{user}-full-urls.txt"
    json_directory = datetime.datetime.now(tz=datetime.timezone.utc).strftime("{}-%Y-%j").format(user)
    if os.path.isdir(json_directory):
        # Early return because the existence of the directory implies this user is already scraped
        _logger.warning("User %s has already been scraped today")
        return
    os.makedirs(json_directory)
    scraper = YtPostScraper(json_directory, graft_url)
    scraper.run()
    # Use the extract.py to retrieve and modify the urls
    with open(input_file, "w") as output:
        extract.run(files=json_directory, func=extract.post_modify_runction, output=output)
    # Use subprocess and wget to download the Images
    directory_prefix = f"{user}-full"
    subprocess.run(
        ["wget", "--input-file", input_file, "--directory-prefix", directory_prefix, "--no-verbose"],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    rename_extensionless_files_in_directory(directory_prefix, ".webp")


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

    args = parser.parse_args()
    users = args.users

    for user in users:
        full_scrape_user(user)


if __name__ == "__main__":
    main()
