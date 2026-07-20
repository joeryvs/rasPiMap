#!../venv/bin/python
import json
import logging
import os
import pathlib
import re
import sys
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Iterable

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from srcset_parsing import ImageType, parse_src_set

_logger = logging.getLogger(__name__)


class Reader:
    def find_elements(self, path, elm_name, **kwargs):
        if not isinstance(path, Iterable):
            path = [path]
        for p in path:
            p = pathlib.Path(p)
            if p.is_dir():
                _logger.debug("Recursive on %s", p)
                yield from self.find_elements(path=(p / n for n in os.listdir(p)), elm_name=elm_name, **kwargs)
            elif p.is_file():
                _logger.debug("Parsing %s", p)
                with open(p, "r") as f:
                    data = f.read()
                soup = BeautifulSoup(data, features="html.parser")
                yield from soup.find_all(name=elm_name, **kwargs)
            else:
                _logger.error("%s IS NOT A FILE", p)


class Writer(ABC):
    @abstractmethod
    def output_items(self, items):
        pass

    @abstractmethod
    def output_content_to_directory(self, name, content):
        pass


class StdoutWriter(Writer):
    def __init__(self) -> None:
        super().__init__()

    def output_items(self, items):
        for p in items:
            print(p)

    def output_content_to_directory(self, name, content):
        print("##", name)
        print(content)
        return super().output_content_to_directory(name, content)


class FileWriter(Writer):
    def __init__(self, output) -> None:
        self.output_file = pathlib.Path(output)
        super().__init__()

    def output_items(self, items):

        with open(self.output_file, "w") as f:
            for i in items:
                print(i, file=f)

    def output_content_to_directory(self, name, content):
        path = self.output_file / name
        os.makedirs(self.output_file, exist_ok=True)
        with open(path, "w", encoding=sys.getfilesystemencoding()) as f:
            print(content, file=f)


class Extractor(ABC):
    def __init__(self, reader: Reader, writer: Writer):
        self.reader = reader
        self.writer = writer

    def find_elements(self, path, elm_name, **kwargs):
        return self.reader.find_elements(path, elm_name, **kwargs)

    @abstractmethod
    def extract(self, /, input_path, **kwargs):
        pass

    @abstractmethod
    def retrieve(self, input_path) -> Iterable:
        return []


class ImageExtractor(Extractor):
    _include_srcset = True

    def extract(self, /, input_path, sort=True, unique=True, **kwargs):
        art_links = self.retrieve(input_path)
        # remove duplicates
        art_link_paths = art_links
        if unique:
            art_link_paths = list(dict.fromkeys(art_links))
        if sort:
            art_link_paths = list(art_link_paths)
            art_link_paths.sort()
        _logger.info("art_links are: ")

        self.writer.output_items(art_link_paths)

    def retrieve(self, input_path) -> Generator[str]:
        images = self.find_elements(input_path, "img", **self._find_elements_kwargs())
        # extract src and src_set
        sources = (src.url for srcs in (self.retrieve_img_src(i) for i in images) for src in srcs)
        art_links_regex = self._regex()
        art_links = (img for img in sources if self._keep_string(art_links_regex, img))
        return art_links

    def retrieve_img_src(self, anchor) -> Generator[ImageType]:
        if anchor.get("src"):
            yield ImageType(anchor["src"], density=1)

        if self._include_srcset:
            srcset = anchor.get("srcset", default=None)
            if srcset:
                yield from self.parse_sourceset(srcset)

    def parse_sourceset(self, srcset):
        assert isinstance(srcset, str)
        return parse_src_set(srcset)

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
        return (x for x in super().retrieve_img_src(anchor) if x.density == 2)


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
    _include_srcset = True

    def retrieve_img_src(self, anchor):
        result = super().retrieve_img_src(anchor)

        maximum = max(result, default=None)
        if maximum:
            _logger.debug("maximum is %s", maximum)
            yield maximum


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
    def extract(self, /, input_path, sort=True, unique=True, **kwargs):
        art_links = self.retrieve(input_path)
        # remove duplicates

        art_link_paths = map(self.post_proces_function, art_links)
        if unique:
            _logger.info("TAking unique items")
            art_link_paths = list(dict.fromkeys(art_link_paths))
            _logger.info("new page links are: %d", len(art_link_paths))
        if sort:
            _logger.info("sorting items")
            art_link_paths = sorted(art_link_paths)

        self.writer.output_items(art_link_paths)

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


class HighestUserExtractor(UserPageExtractor):
    def extract(self, /, input_path, **kwargs):
        assert len(input_path) == 1

        art_links = self.retrieve(input_path=input_path)
        art_link_paths = map(self.post_proces_function, art_links)
        art_link_paths = list(art_link_paths)
        _logger.debug("total links in %s are %d", input_path, len(art_link_paths))
        regex = re.compile(r"page=(\d+)")
        regexes = map(regex.search, art_link_paths)
        # extract the numbers of the matches
        numbers = [int(x.group(1)) for x in regexes if x]
        highest = max(numbers, default=None)
        if highest is not None:
            self.writer.output_items([highest])
        else:
            _logger.error("No page found at %s", input_path)


class TagPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/tag/.*$")


class OnePerPageExtractor(Extractor, ABC):
    def extract(self, input_path, /, **kwargs):
        if not isinstance(input_path, list):
            input_path = [input_path]

        input_path = [
            y
            for i in input_path
            for ys in [[pathlib.Path(i) / z for z in os.listdir(i)] if pathlib.Path(i).is_dir() else [pathlib.Path(i)]]
            for y in ys
            if y.is_file()
        ]
        for input in input_path:
            if not input.exists():
                _logger.error("ERROR %s file does not exist", input)
                continue
            with open(input, "r", encoding=sys.getfilesystemencoding()) as f:
                soup = BeautifulSoup(f.read(), features="html.parser")

            self.handle_page(input, soup)

    @abstractmethod
    def handle_page(self, name, soup):
        pass

    def retrieve(self, input_path):
        return super().retrieve(input_path)


class DescriptionExtractor(OnePerPageExtractor):
    def handle_page(self, name, soup):
        section = soup.find("div", id="description")

        if not section:
            _logger.error("ERROR %s file has no description section", name)
            return
        output = md(str(section))
        self.writer.output_content_to_directory(name.with_suffix(".md").name, output)
        return super().handle_page(name, soup)

    def retrieve(self, input_path):
        return super().retrieve(input_path)


class StoryExtractor(OnePerPageExtractor):
    def handle_page(self, name, soup):

        section = soup.find("section", class_="HiQtsh")

        if not section:
            _logger.error("ERROR %s file has no section", name)
            return
        output = md(str(section))
        self.writer.output_content_to_directory(name.with_suffix(".md").name, output)
        return super().handle_page(name, soup)

    def retrieve(self, input_path):
        return super().retrieve(input_path)


class JsonExtractor(Extractor):
    def extract(self, input_path, /, **kwargs):
        if not isinstance(input_path, list):
            input_path = [input_path]
        input_path = [
            y
            for i in input_path
            for ys in [[pathlib.Path(i) / z for z in os.listdir(i)] if pathlib.Path(i).is_dir() else [pathlib.Path(i)]]
            for y in ys
            if y.is_file()
        ]
        for name in input_path:
            if not name.exists():
                _logger.error("ERROR %s file does not exist", name)
                continue
            with open(name, "r", encoding=sys.getfilesystemencoding()) as f:
                soup = BeautifulSoup(f.read(), features="html.parser")
            script = soup.find("script", id="_R_")
            if not script:
                _logger.error("ERROR %s file has no _R_ script section", name)
                continue
            text = script.text
            lines = text.split("\n")
            important: str = lines[3]
            # make a lot of assumption no of the structure
            important = important.removeprefix("window.__INITIAL_STATE__ = JSON.parse(").removesuffix(");")
            # kinda dangeroues to run arbartraty code,
            important = eval(important, {}, {})
            # parse to obj and back to string
            try:
                # prettify the JSON
                json_content = json.loads(important)
                output = json.dumps(
                    json_content,
                    check_circular=True,
                    allow_nan=False,
                    ensure_ascii=True,
                    sort_keys=True,
                    indent=2,
                )
            except json.decoder.JSONDecodeError:
                _logger.error("ERROR %s has an imparseble json content",name)
                output = important
            name = name.with_suffix(".json").name
            self.writer.output_content_to_directory(name, output)

    def retrieve(self, input_path) -> Iterable:
        return super().retrieve(input_path)


class JsonImageUrlExtractor(Extractor):
    def extract(self, /, input_path, **kwargs):
        all_urls = self.retrieve(input_path=input_path)
        all_urls = sorted(dict.fromkeys(all_urls))
        self.writer.output_items(all_urls)

    def find_props(self, dictionary, prop):
        result = []

        def find_prop_rec(obj):
            if not obj:
                return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == prop:
                        result.append(v)
                    else:
                        find_prop_rec(v)
            if isinstance(obj, list):
                for item in obj:
                    find_prop_rec(item)
            pass

        find_prop_rec(dictionary)
        return result

    def construct_url_from_media(self, media):
        baseUri = media.get("baseUri")
        prettyName = media.get("prettyName")
        tokens = media.get("token")
        if not tokens:
            _logger.warning("No tokens available for %s, %s", prettyName, baseUri)
        token = "?token=" + tokens[0] if tokens else ""
        types: list[dict] = media.get("types")

        # t is fullview or pre or social_preview
        # find first fullview, then preview and social_preview as backups
        fullviews = [t for x in ["fullview", "preview", "social_preview"] for t in types if t.get("t") == x]
        if fullviews:
            fullview = fullviews[0]
            c = fullview.get("c") or ""
            extension = c.replace("<prettyName>", prettyName)
            url = baseUri + extension + token
            _logger.debug("URL for %s is %s", prettyName, url)
            return url
        else:
            _logger.info("No fullviews for %s, %s", prettyName, baseUri)
        return ""

    def retrieve(self, input_path):
        a = self.find_elements(input_path, "script", id="_R_")
        for b in a:
            text = b.text
            lines = text.split("\n")
            important: str = lines[3]
            # make a lot of assumption no of the structure
            important = important.removeprefix("window.__INITIAL_STATE__ = JSON.parse(").removesuffix(");")
            # kinda dangeroues to run arbartraty code,
            important = eval(important, {}, {})
            x = json.loads(important)
            _logger.debug("evaluated line of %s", x)
            # find all "media"
            medias = self.find_props(x, "media")
            # construct url
            urls = [self.construct_url_from_media(media) for media in medias]
            yield from urls
        pass


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
            "highest_user_page_number": HighestUserExtractor,
            "all_links": AllPagesExtractor,
            "tags": TagPageExtractor,
            "description": DescriptionExtractor,
            "story": StoryExtractor,
            "json": JsonExtractor,
            "json_art": JsonImageUrlExtractor,
        }

    @property
    def choices(self):
        return list(self._options.keys())

    def extractor(self, item, *args, **kwargs) -> Extractor:
        return self._options[item](*args, **kwargs)
