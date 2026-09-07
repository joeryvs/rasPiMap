import logging
import re
from collections.abc import Generator

from utils import Extractor

_logger = logging.getLogger(__name__)


class LinkExtractor(Extractor):
    def extract(self, /, input_path, sort=True, unique=True, **kwargs):
        art_links = self.retrieve(input_path)
        art_link_paths = art_links
        if unique:
            _logger.info("Taking unique items")
            art_link_paths = list(dict.fromkeys(art_links))
        if sort:
            _logger.info("Sorting items")
            art_link_paths = list(art_link_paths)
            art_link_paths.sort()
        _logger.info("art_links are: ")

        self.writer.output_items(art_link_paths)

    def retrieve(self, input_path) -> Generator[str]:
        images = self.find_elements(input_path, "link", **self._find_elements_kwargs())
        # extract src and src_set
        sources = (src for srcs in (self.retrieve_href(i) for i in images) for src in srcs)
        art_links_regex = self._regex()
        art_links = (img for img in sources if self._keep_string(art_links_regex, img))
        return art_links

    def retrieve_href(self, anchor) -> Generator[str]:
        if anchor.get("href"):
            yield anchor["href"]

    def _find_elements_kwargs(self):
        return {}

    def _keep_string(self, regex, string):
        return regex.match(string)

    def _regex(self):
        return re.compile(r"^https://.*$")


class VideoExtractor(LinkExtractor):
    def _find_elements_kwargs(self):
        return {"as": "video"}
