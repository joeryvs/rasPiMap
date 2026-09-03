import collections.abc
import logging
import os
import pathlib
import time
import urllib.parse
from uuid import uuid4

import requests

_logger = logging.getLogger(__name__)

extensions = {
    "text/html": ".html",
    "application/json": ".json",
    "image/webp": ".webp",
}


def download_from_web(
    urls: collections.abc.Iterable[str], /, target_directory: str, overwrite=True, update_extension=False
):
    if target_directory:
        os.makedirs(target_directory, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        # From the url perform an urlsplit to remove the query parameters, and finally split at / and take the last element
        p = urllib.parse.urlsplit(url=url).path.split("/")[-1]
        time.sleep(0.1)
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
