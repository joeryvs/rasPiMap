
from abc import ABC, abstractmethod
import logging
import re

from deviant.utils import Extractor

_logger = logging.getLogger(__name__)

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


class TagPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/tag/.*$")

class AllPagesExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(".*")


class UserPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/gallery.*$")

class ArtPageExtractor(PageExtractor):
    def extract_regex(self) -> re.Pattern:
        return re.compile(r"^.*/art/.+$")

    def post_proces_function(self, link: str) -> str:
        return link.removesuffix("#comments")
