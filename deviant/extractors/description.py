import logging

from markdownify import markdownify as md
from utils import OnePerPageExtractor

_logger = logging.getLogger(__name__)


class DescriptionExtractor(OnePerPageExtractor):
    _name = "deviantart.description"
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
    _name = "deviantart.story"
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
