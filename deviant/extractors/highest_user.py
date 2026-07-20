import logging
import re

from .page import UserPageExtractor

_logger = logging.getLogger(__name__)


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
