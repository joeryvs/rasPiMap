#!../venv/bin/python
import os
import pathlib
import re
import sys
from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import Generator
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
            else:
                print("ERROR ARGUMENT IS NOT A FILE")

    @abstractmethod
    def extract(self, input_path, output_path):
        pass

    @abstractmethod
    def retrieve(self, input_path) -> Iterable:
        return []


ImageTypes = namedtuple("ImageType", ["src", "type"])


class ImageExtractor(Extractor):
    _include_srcset = True

    def extract(self, input_path, output_path):
        art_links = self.retrieve(input_path)
        # remove duplicates
        art_link_paths = list(dict.fromkeys(art_links))
        art_link_paths.sort()
        # print()
        print("art_links are: ")
        links = []
        # print(*art_link_paths, sep="\n")
        with open(output_path, "a") as f:
            for p in art_link_paths:
                links.append(p)
                print(p, file=f)
            # print(*art_link_paths, sep="\n", file=f)

    def retrieve(self, input_path) -> Generator[str]:
        images = self.find_elements(input_path, "img", **self._find_elements_kwargs())
        # extract src and src_set
        sources = (src.src for srcs in (self.retrieve_img_src(i) for i in images) for src in srcs)
        art_links_regex = self._regex()
        art_links = (img for img in sources if self._keep_string(art_links_regex, img))
        return art_links

    def retrieve_img_src(self, anchor) -> Generator[ImageTypes]:
        if anchor.get("src"):
            yield ImageTypes(anchor["src"], "main")

        if self._include_srcset:
            srcset = anchor.get("srcset", default=None)
            if srcset:
                x = srcset.split(", ")
                for y in x:
                    z = y.split(" ")
                    yield ImageTypes(z[0].strip(), z[1].strip())

    def _find_elements_kwargs(self):
        return {}

    def _keep_string(self, regex, string):
        return regex.match(string)

    def _regex(self):
        return re.compile(r"^https://.*$")


class AvatarExtractor(ImageExtractor):
    def _regex(self):
        return re.compile(r"^https://a.deviantart.net/.*$")


class DeviantArtImageExtractor(ImageExtractor):
    def _regex(self):
        return re.compile(r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/.+$")


class DeviantArtImage2XExtractor(DeviantArtImageExtractor):
    def retrieve_img_src(self, anchor):
        return (x for x in super().retrieve_img_src(anchor) if x.type == "2x")


class AllImagesExtractor(DeviantArtImageExtractor):
    def _keep_string(self, regex, string):
        return True


class MainImageExtractor(ImageExtractor):
    _include_srcset = False

    def _find_elements_kwargs(self):
        MAIN_IMAGE_CLASS = "_Cyjpk"
        return {"class_": MAIN_IMAGE_CLASS}

    def retrieve_img_src(self, anchor):
        return super().retrieve_img_src(anchor)


class NoCropImageExtractor(DeviantArtImageExtractor):
    def _keep_string(self, regex, string):
        return super()._keep_string(regex, string) and "/crop/" not in string


class NoCropImageExtractorLarge(NoCropImageExtractor):
    _include_srcset = False

    # def retrieve_img_src(self, anchor):
    #     parent = list(super().retrieve_img_src(anchor))
    #     print(parent)

    #     if res := filter(lambda x: x.type == "2x", parent):
    #         yield from res
    #     else:
    #         yield from parent


class LargeImageExtractor(DeviantArtImageExtractor):
    def _regex(self):
        return re.compile(
            r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/\w/(\d|\w|\-)+/(\d|\w|\-|\.)+\?token=(.*)$"
        )

    # def _keep_string(self, regex, string):
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
        return art_links

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
                print(f"ERROR {input} file does not exist")
                continue
            with open(input, "r", encoding=sys.getfilesystemencoding()) as f:
                soup = BeautifulSoup(f.read(), features="html.parser")
            section = soup.find("div", id="description")

            if not section:
                print(f"ERROR {input} file has no description section")
                continue
            # print(section)

            output = "\n".join(x.get_text() for x in section.find_all(["h1", "h2", "h3", "h4", "h5", "p", "br"]))
            path = output_path / input.name
            with open(path, "w", encoding=sys.getfilesystemencoding()) as f:
                print(output, file=f)

    def retrieve(self, input_path):
        return super().retrieve(input_path)


class JsonExtractor(Extractor):
    def retrieve(self, input_path) -> Iterable:
        a = self.find_elements(input_path, "script")
        for b in a:
            # print(b)
            text = b.text
            # if b.is_empty_element:
            # print("empty")
            # continue
            # print(dir(b))
            # print(text)
            regex = re.compile(r"baseUri")
            if "baseUri" in text:
                print(text)
            if x := regex.match(text):
                print(text)
                print()
                print(x)

                input()
        return super().retrieve(input_path)

    def extract(self, input_path, output_path):

        scripts = self.retrieve(input_path=input_path)
        return super().extract(input_path, output_path)


class ExtractorFactory:
    def __init__(self):
        self._options = {
            "art": ArtPageExtractor,
            "images": DeviantArtImageExtractor,
            "images2x": DeviantArtImage2XExtractor,
            "large_images": LargeImageExtractor,
            "no_crop": NoCropImageExtractor,
            "no_crop_large": NoCropImageExtractorLarge,
            "all_images": AllImagesExtractor,
            "main_image": MainImageExtractor,
            "avatar": AvatarExtractor,
            "users": UserPageExtractor,
            "all_links": AllPagesExtractor,
            "tags": TagPageExtractor,
            "description": DescriptionExtractor,
            "json": JsonExtractor,
        }

    @property
    def choices(self):
        return list(self._options.keys())

    def extractor(self, item, *args, **kwargs) -> Extractor:
        return self._options[item](*args, **kwargs)
