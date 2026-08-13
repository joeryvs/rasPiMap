import argparse
import json
import logging
import os
import sys

_logger = logging.getLogger(__name__)


def find_keys_rec(obj, key, with_path=False):
    assert isinstance(key, str)
    result = []
    stack = []

    def foo(obj):
        if isinstance(obj, dict):
            if key in obj:
                # Create a new list
                result.append((stack + [key], obj[key]) if with_path else obj[key])
            for k, v in obj.items():
                stack.append(k)
                foo(v)
                stack.pop()
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                stack.append(i)
                foo(v)
                stack.pop()
        elif obj == key:
            result.append((stack.copy(), key) if with_path else key)

    foo(obj)
    return result


# Good enough function to find all the urls
def extract_crop_image_urls(obj):
    for a, b in find_keys_rec(obj, "url", True):
        if b.startswith("https://yt3.ggpht.com"):
            print(a, b)
            yield b


# Just unneeded
def extract_crop_image_urls2(obj):
    continuationItems = obj["onResponseReceivedEndpoints"][0]["appendContinuationItemsAction"]["continuationItems"]
    for ci in continuationItems:
        print(ci.keys())
        ci = ci.get("backstagePostThreadRenderer")
        if ci is None:
            continue
        print(ci.keys())
        ci = ci["post"]
        print(ci.keys())
        ci = ci.get("backstagePostRenderer")
        if ci is None:
            continue
        print(ci.keys())
        ci = ci["backstageAttachment"]
        print(ci.keys())
        ci = ci.get("backstageImageRenderer")
        if ci is None:
            continue
        print(ci.keys())
        ci = ci["image"]
        thumbnails = ci["thumbnails"]
        for t in thumbnails:
            yield t["url"]


def get_files(files):
    if os.path.isdir(files):
        ans = []
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


def run(files, output):

    for f in get_files(files):
        try:
            with open(f, "r") as fp:
                data = json.load(fp=fp)

                for cui in extract_crop_image_urls2(data):
                    print(cui, file=output)
        except json.JSONDecodeError:
            _logger.warning("not valid JSON %s", f)
        finally:
            pass


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--strict", action=argparse.BooleanOptionalAction)
    parser.add_argument("-i", "--input-file", required=True)
    parser.add_argument("-o", "--output", default="-")

    args = parser.parse_args()

    output = sys.stdout if args.output == "-" else open(args.output, "a")
    run(args.input_file, output)


if __name__ == "__main__":
    main()
