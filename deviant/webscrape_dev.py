#!../venv/bin/python
import argparse
import os
import pathlib
import re
import sys
from abc import ABC, abstractmethod
from typing import Iterable

from bs4 import BeautifulSoup


class Extractor(ABC):
    @classmethod
    def find_elements(cls, path, elm_name, **kwargs):
        if not isinstance(path, Iterable):
            path = [path]
        for p in path:
            p = pathlib.Path(p)
            if p.is_dir():
                yield from cls.find_elements(path=(p / n for n in os.listdir(p)), elm_name=elm_name, **kwargs)
            elif p.is_file():
                with open(p, "r") as f:
                    data = f.read()
                soup = BeautifulSoup(data, features="html.parser")
                yield from soup.find_all(name=elm_name, **kwargs)

    @abstractmethod
    def extract(self, input_path, output_path):
        pass

    @abstractmethod
    def retrieve(self, input_path):
        return []


class ImageExtractor(Extractor):
    def extract(self, input_path, output_path):
        art_links = self.retrieve(input_path)
        # remove duplicates
        art_link_paths = list(dict.fromkeys(art_links))
        art_link_paths.sort()
        print("len art_link_paths: ", len(art_link_paths))
        print()
        print("art_links are: ")
        print(*art_link_paths, sep="\n")
        with open(output_path, "a") as f:
            print(*art_link_paths, sep="\n", file=f)

    def retrieve(self, input_path):
        images = self.find_elements(input_path, "img")
        images = list(images)
        # extract src and src_set
        sources = [a["src"] for a in images if a.get("src", default=None)]
        sourcesets = [a["srcset"] for a in images if a.get("srcset", default=None)]
        # extract all from srcset
        # split at ", " afterward split at a space and take the link part
        sourcesets = [x.split(" ")[0].strip() for srcset in sourcesets for x in srcset.split(", ")]
        art_links_regex = self.regex()
        # take both
        links = sources + sourcesets
        art_links = [img for img in links if self.keep_string(art_links_regex, img)]
        return art_links

    def keep_string(self, regex, string):
        return regex.match(string)

    def regex(self):
        return re.compile(r"^https://.*$")


class AvatarExtractor(ImageExtractor):
    def regex(self):
        return re.compile(r"^https://a.deviantart.net/.*$")


class DeviantArtImageExtractor(ImageExtractor):
    def regex(self):
        return re.compile(r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/.+$")


class AllImagesExtractor(DeviantArtImageExtractor):
    def keep_string(self, regex, string):
        return True


class NoCropImageExtractor(DeviantArtImageExtractor):
    def keep_string(self, regex, string):
        return super().keep_string(regex, string) and "/crop/" not in string


class LargeImageExtractor(DeviantArtImageExtractor):
    def regex(self):
        return re.compile(
            r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/\w/(\d|\w|\-)+/(\d|\w|\-|\.)+\?token=(.*)$"
        )

    # def keep_string(self, regex, string):
    #     return (
    #         super().keep_string(regex, string)
    #         and "/crop/" not in string
    #         and "/fit/" not in string
    #         and "/fill/" not in string
    #     )


class PageExtractor(Extractor, ABC):
    def extract(self, input_path, output_path):
        art_links = self.retrieve(input_path)
        # remove duplicates
        art_link_paths = list(dict.fromkeys(map(self.post_proces_function, art_links)))
        art_link_paths.sort()
        print()
        print("new page links are: ")
        print(*art_link_paths, sep="\n")
        with open(output_path, "a") as f:
            print(*art_link_paths, sep="\n", file=f)

    def retrieve(self, input_path):
        anchors = self.find_elements(input_path, "a")
        hrefs = (str(a["href"]) for a in anchors if a.get("href", default=None))
        art_links_regex = self.extract_regex()
        art_links = (href for href in hrefs if art_links_regex.match(href))
        return list(art_links)

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


class AllPagesExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(".*")


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

        input_path = [
            y
            for i in input_path
            for ys in [[pathlib.Path(i) / z for z in os.listdir(i)] if pathlib.Path(i).is_dir() else [pathlib.Path(i)]]
            for y in ys
            if y.is_file()
        ]
        if isinstance(output_path, str):
            output_path = pathlib.Path(output_path)
        os.makedirs(output_path, exist_ok=True)
        for input in input_path:
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

            output = "\n\n".join(x.get_text() for x in section.find_all(["h1", "h2", "h3", "h4", "h5", "p"]))
            path = output_path / input.name
            with open(path, "w", encoding=sys.getfilesystemencoding()) as f:
                print(output, file=f)

    def retrieve(self, input_path):
        return super().retrieve(input_path)


class ExtractorFactory:
    _options = {
        "art": ArtPageExtractor,
        "images": DeviantArtImageExtractor,
        "large_images": LargeImageExtractor,
        "no_crop": NoCropImageExtractor,
        "all_images": AllImagesExtractor,
        "users": UserPageExtractor,
        "all_links": AllPagesExtractor,
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
