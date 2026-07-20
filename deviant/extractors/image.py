import logging
import re
from collections.abc import Generator

from srcset_parsing import ImageType, parse_src_set
from utils import Extractor

_logger = logging.getLogger(__name__)


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
