import argparse
import json
import logging
import os
import sys

from utils import find_key_rec, find_keys_rec

_logger = logging.getLogger(__name__)


# Good enough function to find all the urls
def extract_crop_image_urls(obj):
    for a, b in find_keys_rec(obj, "url", True):
        if b.startswith("https://yt3.ggpht.com"):
            print(a, b)
            yield b


def get_files(files: str) -> list[str]:
    """Retrieve a list of valid files that can be read"""
    if os.path.isdir(files):
        ans: list[str] = []
        for a in os.walk(files):
            dir_path, _others_dirs, target_files = a
            for x in target_files:
                ans.append(os.path.join(dir_path, x))
        return ans
    elif os.path.isfile(files):
        return [files]
    else:
        _logger.error("ERROR %s does not exist", files)
        return []


def get_urls_from_json_files(file: str):
    with open(file, "r") as fp:
        try:
            data = json.load(fp=fp)
            for url in find_keys_rec(data, "url", False):
                yield url
        except json.json.JSONDecodeError:
            _logger.warning("Not valid JSON %s", file)


def run(files: str, output, func=None):
    for url in get_by_pattern(files, "https://yt3.ggpht.com"):
        url = url if func is None else func(url)
        print(url, file=output)


def get_by_pattern(files: str, pattern: str):
    for f in get_files(files):
        for url in get_urls_from_json_files(f):
            if url.startswith(pattern):
                yield url


def post_modify_runction(url: str) -> str:
    # vim macro is 0nllc9e4000 + Esc + j0
    # now as a python function
    parts = url.split("=s")
    assert len(parts) == 2
    begin, end = parts
    x = end.split("-")
    x[0] = "4000"
    x[1:3] = []
    return f"{begin}=s{'-'.join(x)}"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--strict", action=argparse.BooleanOptionalAction)
    parser.add_argument("--post-process", action=argparse.BooleanOptionalAction)
    parser.add_argument("-i", "--input-file", required=True)
    parser.add_argument("-o", "--output", default="-")

    args = parser.parse_args()

    func = post_modify_runction if args.post_process else None
    with sys.stdout if args.output == "-" else open(args.output, "a") as output:
        run(args.input_file, func=func, output=output)


if __name__ == "__main__":
    main()
