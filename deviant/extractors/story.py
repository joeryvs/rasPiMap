import logging

from markdownify import markdownify as md

from .one_per_page import OnePerPageExtractor

_logger = logging.getLogger(__name__)


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
