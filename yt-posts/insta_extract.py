import json
import logging
import os
from collections import Counter, defaultdict

from bs4 import BeautifulSoup
from extract import find_key_rec, find_keys_rec
from insta import _find_target_script, download_insta_page
from utils import print_iter_item, unique

_logger = logging.getLogger(__name__)


def _get_files(dir):

    for current_dir, _dirs, files in os.walk(dir):
        for f in files:
            full_file_path = os.path.join(current_dir, f)
            yield full_file_path


def read_json_from_file(file):

    with open(file, mode="r") as fp:
        json_obj = json.load(fp=fp)
        return json_obj


def run_directory_extraction(dir):

    files = _get_files(dir)
    types = []
    ids = []
    urls = defaultdict(list)
    for f in files:
        json_obj = read_json_from_file(file=f)
        edges = find_key_rec(json_obj, "edges")
        if edges is None:
            _logger.error("No edges in %s", f)
            continue
        assert isinstance(edges, list)
        for edge in edges:
            node = edge["node"]
            pk = node["pk"]
            code = node["code"]
            display_uri = node["display_uri"]
            product_type = node["product_type"]
            user = node["user"]
            username = user["username"]
            ids.append(pk)
            types.append((username, product_type))

            urls[(username, product_type)].append(code)
    c = Counter(types)
    print(*c.items(), sep="\n")

    real_urls = create_urls(urls)
    for url in real_urls:
        print(url)


def create_urls(dictionary):

    for (username, product_type), codes in dictionary.items():
        # print(username)
        # print(product_type)
        for code in codes:
            if product_type in ["feed", "carousel_container"]:
                yield f"https://instagram.com/{username}/p/{code}"
            elif product_type in ["clips"]:
                yield f"https://instagram.com/{username}/reel/{code}"
            else:
                _logger.warning("unknown type %s", product_type)


def run_download_from_file(file, target_dir, to_json=True):

    print(file)

    with open(file, "r") as f:
        data = [line.strip() for line in f]

    os.makedirs(target_dir, exist_ok=True)
    for point in data:
        target = os.path.join(target_dir, os.path.basename(point))
        download_insta_page(point, target=target)
        if to_json:
            target_dir_json = f"{target_dir}_json"
            os.makedirs(target_dir_json, exist_ok=True)
            with open(target, "r") as f:
                data = f.read()
            soup = BeautifulSoup(data, features="html.parser")
            scripts = soup.find_all("script")
            target_script = _find_target_script(scripts)
            if target_script is None:
                _logger.warning("No script found")
                continue

            json_obj = json.loads(target_script.text or "")
            with open(os.path.join(target_dir, os.path.basename(point)), mode="w") as fp:
                json.dump(fp=fp, obj=json_obj, indent=2)


def run_read(dir):

    print(dir)
    files = _get_files(dir=dir)
    all_urls = []

    for f in files:
        print(f)
        with open(f, "r") as fp:
            data = fp.read()
        # this assumes HTML is stored and not JSON
        soup = BeautifulSoup(data, features="html.parser")
        scripts = soup.find_all("script")
        target_script = _find_target_script(scripts)
        if target_script is None:
            _logger.warning("No script found")
            continue

        json_obj = json.loads(target_script.text or "")

        p = find_keys_rec(json_obj, "image_versions2", with_path=False)
        # print(p)
        for img_version in p:
            for url in img_version["candidates"]:
                all_urls.append(url["url"])

    for u in all_urls:
        print(u)

    print()
    # remove duplicate
    all_urls = unique(all_urls)
    # only keep those with stp = dst-jpg_e35_tt6 in the query parameters , str contains instead of proper parsing because we are lazy
    all_urls = [u for u in all_urls if "stp=dst-jpg_e35_tt6" in u]

    with open("output.txt", "w") as f:
        for line in all_urls:
            print(line, file=f)


def main():
    from argparse import ArgumentParser, BooleanOptionalAction

    logging.basicConfig(level="DEBUG")
    parser = ArgumentParser()
    p2 = parser.add_mutually_exclusive_group()

    p2.add_argument("--dir")
    p2.add_argument("--input-file", "-i")
    p2.add_argument("--read")
    args = parser.parse_args()

    if args.dir:
        run_directory_extraction(args.dir)
    elif args.input_file:
        run_download_from_file(args.input_file, "test2")
    elif args.read:
        run_read(args.read)


if __name__ == "__main__":
    main()
