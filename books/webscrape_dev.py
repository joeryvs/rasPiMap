#!../venv/bin/python
import argparse
import os
import pathlib
import re
import sys
import uuid
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class Extractor(ABC):
    @classmethod
    def find_elements(cls, path, elm_name, **kwargs):
        result = []
        if not isinstance(path, list):
            path = [path]
        for p in path:
            with open(p, "r") as f:
                data = f.read()
            soup = BeautifulSoup(data, features="html.parser")
            x = soup.find_all(name=elm_name, **kwargs)
            for y in x:
                result.append(y)
        return result

    @classmethod
    def extract_pages_links(cls, input_path):
        anchors = cls.find_elements(input_path, "a")
        hrefs = [a["href"] for a in anchors if a.get("href", default=None)]
        # remove duplicates
        hrefs = list(dict.fromkeys(hrefs))
        return hrefs

    @abstractmethod
    def extract(self, input_path, output_path):
        pass


class ImageExtractor(Extractor):
    def extract(self, input_path, output_path):
        images = self.find_elements(input_path, "img")
        # extract src
        sources = [a["src"] for a in images if a.get("src", default=None)]
        sourcesets = [a["srcset"] for a in images if a.get("srcset", default=None)]
        # extract all from srcset
        # split at ", " afterward split at a space and take the link part
        sourcesets = [x.split(" ")[0].strip() for srcset in sourcesets for x in srcset.split(", ")]
        art_links_regex = self.regex()
        # take both
        links = sources + sourcesets
        art_links = [img for img in links if self.keep_string(art_links_regex, img)]
        # remove duplicates
        art_link_paths = list(dict.fromkeys(art_links))
        art_link_paths.sort()
        print("len art_link_paths: ", len(art_link_paths))
        print()
        print("art_links are: ")
        print(*art_link_paths, sep="\n")
        with open(output_path, "a") as f:
            print(*art_link_paths, sep="\n", file=f)

    def keep_string(self, regex, string):
        return regex.match(string)

    def regex(self):
        return re.compile(r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/.+$")


class LargeImageExtractor(ImageExtractor):
    def keep_string(self, regex, string):
        return super().keep_string(regex, string) and "92s" not in string


class PageExtractor(Extractor, ABC):
    def extract(self, input_path, output_path):
        hrefs = self.extract_pages_links(input_path=input_path)
        art_links_regex = self.extract_regex()
        art_links = [href for href in hrefs if art_links_regex.match(href)]

        # remove duplicates
        art_link_paths = list(dict.fromkeys(map(self.post_proces_function, art_links)))
        art_link_paths.sort()
        print()
        print("new page links are: ")
        print(*art_link_paths, sep="\n")
        with open(output_path, "a") as f:
            print(*art_link_paths, sep="\n", file=f)

    @abstractmethod
    def extract_regex(self) -> re.Pattern:
        pass

    def post_proces_function(self, link: str) -> str:
        """Optional function to modify the url"""
        return link


class ArtPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/art/.+$")

    def post_proces_function(self, link: str) -> str:
        return link.removesuffix("#comments")


class UserPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/gallery.*$")


class TagPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/tag/.*$")


class DescriptionExtractor(Extractor):
    def extract(self, input_path, output_path):
        if not isinstance(input_path, list):
            input_path = [input_path]
        if isinstance(output_path, str):
            output_path = pathlib.Path(output_path)
            os.makedirs(output_path, exist_ok=True)

        for input in input_path:
            input = pathlib.Path(input)
            if not input.exists():
                print("ERROR input file does not exist")
                continue
            with open(input, "r", encoding=sys.getfilesystemencoding()) as f:
                soup = BeautifulSoup(f.read(), features="html.parser")
            section = soup.find("div", id="description")

            if not section:
                print("ERROR input file has no description section")
                continue
            print(section)
            output = "\n\n".join(section.strings)
            path1 = output_path / f"{uuid.uuid4().hex}.txt"

            with open(path1, "w", encoding=sys.getfilesystemencoding()) as f:
                print(output, file=f)
            path2 = output_path / input.name
            with open(path2, "w", encoding=sys.getfilesystemencoding()) as f:
                print(output, file=f)


class ExtractorFactory:
    _options = {
        "art": ArtPageExtractor,
        "images": ImageExtractor,
        "large_images": LargeImageExtractor,
        "users": UserPageExtractor,
        "tags": TagPageExtractor,
        "description": DescriptionExtractor,
    }

    def __init__(self, item):
        self.item = item
        if self.item not in self._options:
            raise Exception

    @classmethod
    def options(cls):
        return list(cls._options.keys())

    @property
    def extractor(self) -> Extractor:
        return self._options[self.item]()


def scapable_url(url: str) -> bool:
    print(repr(url))
    if url.startswith("//"):
        return True
    return False


def main():
    path = pathlib.Path(__file__).parent / "index.html"
    output = pathlib.Path(__file__).parent / "art_links.txt"

    parser = argparse.ArgumentParser(
        prog="webscrape_dev",
        description="Choose mode and other options",
        epilog="hello world",
    )
    parser.add_argument(
        "type",
        choices=ExtractorFactory.options(),
    )
    parser.add_argument("-i", "--input", default=path, nargs="+")
    parser.add_argument("-o", "--output", default=output, nargs="?")

    args = parser.parse_args()
    print(args.type)
    print(args.input)
    print(args.output)

    extractor_object = ExtractorFactory(args.type).extractor
    if extractor_object:
        extractor_object.extract(args.input, args.output)


if __name__ == "__main__":
    main()
